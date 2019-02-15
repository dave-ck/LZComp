import time
import bitarray
import math


def lzss_bytewise_encode(bits, W, L):
    # redundant statement - .tobytes() calls .fill() - still good for clarity
    if len(bits) % 8 != 0:
        print("len(bits) = {} is not divisible by given n = {}. Returned false.".format(len(bits), 8))
        print("Padding {} bits".format(bits.fill()))
    source_bytes = bytes(bits.tobytes())
    # log2_W is the number of bits needed to represent W
    log2_W = int(math.ceil(math.log(W + 1, 2)))
    WintConverter = "0" + str(int(log2_W)) + "b"
    # log2_L is the number of bits needed to represent L
    log2_L = int(math.ceil(math.log(L + 1, 2)))
    LintConverter = "0" + str(int(log2_L)) + "b"
    # encoding n characters as a tuple requires 1 + log2_W + log2_L + 8 bits
    lempelength = log2_L + log2_W + 9
    encoded = bitarray.bitarray()
    # pos is bytewise address
    pos = 0
    window = source_bytes[max(0, pos - W):pos]
    buffer = source_bytes[pos:pos + L]
    while pos < len(source_bytes):
        # for each bit
        l = 1
        flag = False
        while len(buffer) > l and buffer[:l] in window:
            l += 1
            flag = True
        # check whether it is shorter or longer to encode (0,0,m) l times over or (rel_pos, l-1, m)
        if flag and l * 9 > lempelength:
            # finds first occurrence within buffer
            rel_pos = min(pos, W) - window.find(buffer[:l - 1])
            # 1 is the flag for a (w, l, m) tuple
            encoded.extend('1' + format(rel_pos, WintConverter) + format(l - 1, LintConverter))
            encoded.frombytes(buffer[l - 1:l])
            pos += l
        else:
            # 0 is the flag for a (0,0,m) tuple
            encoded.extend('0')
            encoded.frombytes(buffer[0:1])
            pos += 1
        window = source_bytes[max(0, pos - W):pos]
        buffer = source_bytes[pos:pos + L]
    return encoded


def lzss_bytewise_decode(encoded_bits, W, L):
    # log2_W is the number of bits needed to represent W
    log2_W = int(math.ceil(math.log(W + 1, 2)))
    # log2_L is the number of bits needed to represent L
    log2_L = int(math.ceil(math.log(L + 1, 2)))
    # print("log2W = {}, log2L = {}".format(log2_W, log2_L))
    source = bitarray.bitarray()
    readpos = 0
    while readpos < len(encoded_bits):
        # read in flag
        flag = encoded_bits[readpos]
        readpos += 1
        if flag:
            # read in d
            d = int(encoded_bits[readpos:readpos + log2_W].to01(), 2)
            readpos += log2_W
            # read in l
            l = int(encoded_bits[readpos:readpos + log2_L].to01(), 2)
            readpos += log2_L
            # need to multiply by n to produce bitwise indices
            if l - d == 0:
                d *= 8
                source.extend(source[-1 * d:])
            else:
                l *= 8
                d *= 8
                source.extend(source[-1 * d:l - d])
        # read in m
        m = encoded_bits[readpos:readpos + 8]
        source.extend(m)
        readpos += 8
    return source


def lz77_bytewise_encode(bits, W, L):
    # redundant statement - .tobytes() calls .fill() - still good for clarity
    if len(bits) % 8 != 0:
        print("len(bits) = {} is not divisible by given n = {}. Returned false.".format(len(bits), 8))
        print("Padding {} bits".format(bits.fill()))
    source_bytes = bytes(bits.tobytes())
    # log2_W is the number of bits needed to represent W
    log2_W = int(math.ceil(math.log(W + 1, 2)))
    WintConverter = "0" + str(int(log2_W)) + "b"
    # log2_L is the number of bits needed to represent L
    log2_L = int(math.ceil(math.log(L + 1, 2)))
    LintConverter = "0" + str(int(log2_L)) + "b"
    encoded = bitarray.bitarray()
    # pos is bytewise address
    pos = 0
    window = source_bytes[max(0, pos - W):pos]
    buffer = source_bytes[pos:pos + L]
    while pos < len(source_bytes):
        # for each bit
        l = 1
        flag = False
        while len(buffer) > l and buffer[:l] in window:
            l += 1
            flag = True
        if flag:
            # finds first occurrence within buffer
            rel_pos = min(pos, W) - window.find(buffer[:l - 1])
            # # print("rel_pos ({}) = min(pos ({}), W({})) - window.search(buffer[:l - 1], 1)({})[0]"
            # .format(rel_pos, pos, W, window.search(buffer[:l - 1], 1)))
            # append (rel_pos, l-1, buffer[l-1]) to encoded
            encoded.extend(format(rel_pos, WintConverter) + format(l - 1, LintConverter))
            encoded.frombytes(buffer[l - 1:l])
        else:
            encoded.extend(format(0, WintConverter) + format(0, LintConverter))
            encoded.frombytes(buffer[0:1])
        pos += l
        window = source_bytes[max(0, pos - W):pos]
        buffer = source_bytes[pos:pos + L]
    return encoded


def lz77_n_bitwise_encode(bits, W, L, n):
    # only accepts bitstrings of length k*n.
    if n == 8:
        print("Detected bytewise call - using optimized function")
        return lz77_bytewise_encode(bits, W, L)
    if len(bits) % n != 0:
        print("len(bits) = {} is not divisible by given n = {}. Returned false.".format(len(bits), n))
        return False
    # log2_W is the number of bits needed to represent W
    log2_W = int(math.ceil(math.log(W + 1, 2)))
    WintConverter = "0" + str(int(log2_W)) + "b"
    # log2_L is the number of bits needed to represent L
    log2_L = int(math.ceil(math.log(L + 1, 2)))
    LintConverter = "0" + str(int(log2_L)) + "b"
    encoded = bitarray.bitarray()
    # pos is a bitwise address - translate to indexing address by dividing by n
    pos = 0
    window = bits[max(0, pos - W * n):pos]
    buffer = bits[pos:pos + L * n]
    loadbar = 0
    while pos < len(bits):
        # for each n-bit "word" (for n=8, for each byte)
        l = n
        flag = False
        while len(buffer) > l and buffer[:l] in window:
            # ensure there exists at least one "legal" index - byte-wise splitting for n=8, etc.
            if all([i % n for i in window.search(buffer[:l])]):
                # print("Broke on pos {}".format(pos))
                break
            l += n
            flag = True
        if flag:
            # finds first occurrence within buffer; note indexing here is bitwise
            # print([i for i in window.search(buffer[:l - n]) if i % n == 0])
            rel_pos = (min(pos, W * n) - [i for i in window.search(buffer[:l - n]) if i % n == 0][0])
            # append (rel_pos, l-1, buffer[l-1]) to encoded - divide by n for n-bitwise indexing
            encoded.extend(format(rel_pos // n, WintConverter) + format((l - 1) // n, LintConverter))
            encoded.extend(buffer[l - n:l])
        else:
            encoded.extend(format(0, WintConverter) + format(0, LintConverter))
            encoded.extend(buffer[0:n])
        pos += l
        window = bits[max(0, pos - W * n):pos]
        buffer = bits[pos:pos + L * n]
        loadbar += l
        if loadbar > 100000:
            print("Progress: {} bits of {} read so far.".format(pos, len(bits)))
            loadbar = 0
    return encoded


# decodes for both n_bitwise and bytewise encoders
def lz77_n_bitwise_decode(encoded_bits, W, L, n):
    # log2_W is the number of bits needed to represent W
    log2_W = int(math.ceil(math.log(W + 1, 2)))
    # log2_L is the number of bits needed to represent L
    log2_L = int(math.ceil(math.log(L + 1, 2)))
    # print("log2W = {}, log2L = {}".format(log2_W, log2_L))
    source = bitarray.bitarray()
    readpos = 0
    while readpos < len(encoded_bits):
        # read in d
        # VERY INEFFICIENT - CONVERTS TO STRING THEN INT - REPLACE WITH DIRECT CONVERSION AFTER UNIT TESTING
        d = int(encoded_bits[readpos:readpos + log2_W].to01(), 2)
        readpos += log2_W
        # read in l
        l = int(encoded_bits[readpos:readpos + log2_L].to01(), 2)
        readpos += log2_L
        # read in m
        m = encoded_bits[readpos:readpos + n]
        # print("So far: {}".format(source.tobytes().decode('utf-8')))
        if d != 0 or l != 0:
            # need to multiply by n to produce bitwise indices
            if l - d == 0:
                d *= n
                source.extend(source[-1 * d:])
            else:
                l *= n
                d *= n
                source.extend(source[-1 * d:l - d])
        source.extend(m)
        # print("Read tuple {}, {}, {}".format(d // n, l // n, m.tobytes().decode('utf-8')))
        # print("Extended to: {}".format(source.tobytes().decode('utf-8')))
        # # print("ASCII {} --> {}".format(m, m.tobytes().decode('utf-8')))
        # print()
        readpos += n
    return source
