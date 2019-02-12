import bitarray
import math
import time


# handles n bits at a time as characters (i.e. 8 bits at a time to do bytewise compression)
# W, L in nbits - i.e. for n=8, if W=32, then window spans 32 bytes (!= 32 bits)
def n_bitwise_encode(bits, W, L, n):
    # only accepts bitstrings of length k*n.
    if len(bits) % n != 0:
        return False
    # log2_W is the number of bits needed to represent W
    log2_W = math.ceil(math.log(W + 1, 2))
    WintConverter = "0" + str(log2_W) + "b"
    # log2_L is the number of bits needed to represent L
    log2_L = math.ceil(math.log(L + 1, 2))
    LintConverter = "0" + str(log2_L) + "b"
    encoded = bitarray.bitarray()
    # pos is a bitwise address - translate to indexing address by dividing by n
    pos = 0
    window = bits[max(0, pos - W * n):pos]
    buffer = bits[pos:pos + L * n]
    while pos < len(bits):
        # for each n-bit "word" (for n=8, for each byte)
        l = n
        flag = False
        while len(buffer) > l and buffer[:l] in window:
            # ensure there exists at least one "legal" index - byte-wise splitting for n=8, etc.
            if all([i % n for i in window.search(buffer[:l])]):
                print("Broke on pos {}".format(pos))
                break
            l += n
            flag = True
        if flag:
            # finds first occurrence within buffer; note indexing here is bitwise
            print([i for i in window.search(buffer[:l - n]) if i % n == 0])
            rel_pos = (min(pos, W * n) - [i for i in window.search(buffer[:l - n]) if i % n == 0][0])
            # append (rel_pos, l-1, buffer[l-1]) to encoded - divide by n for n-bitwise indexing
            encoded.extend(format(rel_pos // n, WintConverter) + format((l - 1) // n, LintConverter))
            encoded.extend(buffer[l - n:l])
            if pos == 424:
                testTup = "Pos {}: Write tuple {}, {}, {} - {}".format(pos, rel_pos // n, (l - 1) // n,
                                                                       buffer[l - n:l].tobytes().decode('utf-8'),
                                                                       buffer[l - n:l])
                print(testTup)
                # verify finding index of [space] properly
                # verify encoding said index properly
                # should output "5, 1, 'o'" instead of "6,1,'0'"
                space_pos = window.search(buffer[:l - n], 1)[0]
                print(window[space_pos:space_pos + n])
                rel_pos = W * n - space_pos
                print(window[-1 * rel_pos:-1 * rel_pos + n])
                print(window[-1 * (6 * 8):-1 * rel_pos + n])
                print("Window:", window)
                print("Buffer:", buffer)
                print()
                print("Source:\n", bits.tobytes().decode('utf-8'))
                print()
        else:
            encoded.extend(format(0, WintConverter) + format(0, LintConverter))
            encoded.extend(buffer[0:n])
            testTup = "Pos {}: Write tuple {}, {}, {} - {}".format(pos, 0, 0, buffer[0:n].tobytes().decode('utf-8'),
                                                                   buffer[0:n])

        pos += l
        window = bits[max(0, pos - W * n):pos]
        buffer = bits[pos:pos + L * n]

    return encoded


def bitwise_encode(bits, W, L):
    # log2_W is the number of bits needed to represent W
    log2_W = math.ceil(math.log(W + 1, 2))
    WintConverter = "0" + str(log2_W) + "b"
    # log2_L is the number of bits needed to represent L
    log2_L = math.ceil(math.log(L + 1, 2))
    LintConverter = "0" + str(log2_L) + "b"
    # list of tuples
    encoded = bitarray.bitarray()
    pos = 0
    window = bits[max(0, pos - W):pos]
    buffer = bits[pos:pos + L]
    while pos < len(bits):
        # for each bit
        l = 1
        flag = False
        while len(buffer) > l and buffer[:l] in window:
            l += 1
            flag = True
        if flag:
            # finds first occurrence within buffer
            rel_pos = min(pos, W) - window.search(buffer[:l - 1], 1)[0]
            # print("rel_pos ({}) = min(pos ({}), W({})) - window.search(buffer[:l - 1], 1)({})[0]"
            # .format(rel_pos, pos, W, window.search(buffer[:l - 1], 1)))
            # append (rel_pos, l-1, buffer[l-1]) to encoded
            extension = bitarray.bitarray(format(rel_pos, WintConverter) + format(l - 1, LintConverter))
            encoded.extend(format(rel_pos, WintConverter) + format(l - 1, LintConverter))
            # WARNING: CHANGE APPEND TO EXTEND IN BYTEWISE ENCODER
            encoded.append(buffer[l - 1])
            extension.append(buffer[l - 1])
            testOutput = str(rel_pos) + "," + str(l - 1) + "," + str(buffer[l - 1])
        else:
            encoded.extend(format(0, WintConverter) + format(0, LintConverter))
            extension = bitarray.bitarray(format(0, WintConverter) + format(0, LintConverter))
            # WARNING: CHANGE APPEND TO EXTEND IN BYTEWISE ENCODER
            encoded.append(buffer[0])
            extension.append(bits[pos])
            testOutput = "0,0," + str(bits[pos])
        """
        print("window:", window)
        print("buffer:", buffer)
        print("input:", bits)
        print("sequence at {}:".format(pos), testOutput)
        print("extension at {}:".format(pos), extension)
        print("len window: {}, len buffer: {}".format(len(window), len(buffer)))
        print()
        """
        pos += l
        window = bits[max(0, pos - W):pos]
        buffer = bits[pos:pos + L]

    return encoded


# pass message as string to make use of .index to find where substring starts
def encode(message, W, L):
    # list of tuples
    encoded = []
    pos = 0
    window = message[max(0, pos - W):pos]
    buffer = message[pos:pos + L]
    while pos < len(message):
        # for each "stop"
        l = 1
        flag = False
        while len(buffer) > l and buffer[:l] in window:
            l += 1
            flag = True
        # need to replace window.index with index relative to pos
        if flag:
            rel_pos = min(pos, W) - window.index(buffer[:l - 1])
            encoded.append((rel_pos, l - 1, buffer[l - 1]))
            if rel_pos == 20:
                print("\n", "rel_pos = pos - window.index(buffer[:l - 1])")
                print("{} = {} - window.index({})".format(rel_pos, pos, buffer[:l - 1]))
                print("window.index({}) = {}".format(buffer[:l - 1], window.index(buffer[:l - 1])))
                print("window: {}".format(window))
                print(encoded[-1], "\n")

        else:
            encoded.append((0, 0, message[pos]))
        pos += l
        window = message[max(0, pos - W):pos]
        buffer = message[pos:pos + L]
    return encoded


def n_bitwise_decode(encoded_bits, W, L, n):
    # log2_W is the number of bits needed to represent W
    log2_W = math.ceil(math.log(W + 1, 2))
    # log2_L is the number of bits needed to represent L
    log2_L = math.ceil(math.log(L + 1, 2))
    print("log2W = {}, log2L = {}".format(log2_W, log2_L))
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
        print("So far: {}".format(source.tobytes().decode('utf-8')))
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
        print("Read tuple {}, {}, {}".format(d // n, l // n, m.tobytes().decode('utf-8')))
        print("Extended to: {}".format(source.tobytes().decode('utf-8')))
        # print("ASCII {} --> {}".format(m, m.tobytes().decode('utf-8')))
        print()
        readpos += n
    return source


def bitwise_decode(encoded_bits, W, L):
    # log2_W is the number of bits needed to represent W
    log2_W = math.ceil(math.log(W + 1, 2))
    WintConverter = "0" + str(log2_W) + "b"
    # log2_L is the number of bits needed to represent L
    log2_L = math.ceil(math.log(L + 1, 2))
    LintConverter = "0" + str(log2_L) + "b"
    print("log2W = {}, log2L = {}".format(log2_W, log2_L))
    source = bitarray.bitarray()
    readpos = 0
    while readpos < len(encoded_bits):
        print("\n", readpos)
        # read in d
        # VERY INEFFICIENT - CONVERTS TO STRING THEN INT - REPLACE WITH DIRECT CONVERSION AFTER UNIT TESTING
        d = int(encoded_bits[readpos:readpos + log2_W].to01(), 2)
        readpos += log2_W
        # read in l
        l = int(encoded_bits[readpos:readpos + log2_L].to01(), 2)
        readpos += log2_L
        # read in m
        # CHANGE TO +8 IN BYTEWISE
        m = encoded_bits[readpos:readpos + 1]
        if d != 0 or l != 0:
            if l - d == 0:
                source.extend(source[-1 * d:])
            else:
                source.extend(source[-1 * d:l - d])
        source.extend(m)
        readpos += 1
    return source


def decode(encoded):
    source = ""
    for d, l, m in encoded:
        if d == 0 and l == 0:
            source += m
        elif l - d == 0:
            source += source[-1 * d:] + m
        else:
            source += source[(-1 * d):(l - d)] + m
    return source
