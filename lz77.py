import bitarray
import math


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
            encoded.append(bits[pos])
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
            if l-d == 0:
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
