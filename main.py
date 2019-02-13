import csv
import os
import bitarray
import zipper
import time


def write_csv(header, listoflists):
    with open("out.csv", "a") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([header])
        for row in listoflists:
            writer.writerow(row)


def read_bits(file_path):
    bits = bitarray.bitarray()
    fi = open(file_path, "rb")
    bits.fromfile(fi)
    fi.close()
    return bits


def write_bits(file_path, bits):
    fo = open(file_path, "wb")
    bits.tofile(fo)
    fo.close()


def testLZString():
    peter = "Peter Piper picked a peck of pickled peppers; " \
            "A peck of pickled peppers Peter Piper picked; " \
            "If Peter Piper picked a peck of pickled peppers, " \
            "Where's the peck of pickled peppers Peter Piper picked?"
    encoded = zipper.encode(peter, 32, 16)
    print(encoded)
    decoded = zipper.decode(encoded)
    print("Decoded:", decoded)
    print("Nocoded:", peter)
    print(decoded == peter)


def bitwise_LZ():
    bits = read_bits("./files/source.txt")
    W = 63
    L = 31
    out = zipper.bitwise_encode(bits, W, L)
    print("Source:", bits)
    print("Source length:", len(bits))
    print("Encoded:", out)
    print("Encoded length:", len(out))
    print("Remainder:", len(out) % (6 + 5 + 8))
    source = zipper.bitwise_decode(out, W, L)
    print("Decoded:", source)
    print("Decoded==source:", bits == source)


def batch(W, L, filePaths):
    zipTimes = []
    befaft = []  # store as (before, after) tuples
    ratios = []  # store as (before, after) tuples
    unzipTimes = []
    for i in filePaths:
        print("Processing", i)
        bits = read_bits(i)
        start = time.time()
        out = zipper.lzss_bytewise_encode(bits, W, L)
        zipTimes.append(time.time() - start)
        start = time.time()
        print("Compression ratio:", len(bits) / len(out))
        befaft.append((len(bits), len(out)))
        ratios.append(len(bits) / len(out))
        zipper.lzss_bytewise_decode(out, W, L)
        unzipTimes.append(start - time.time())
    write_csv("LZSS FHIR experiment - W={}, L={}, bytewise".format(W, L),
              [["Zip Times"] + zipTimes,
               ["ratios"] + ratios,
               ["befaft"] + befaft])


def main():
    bits = read_bits("./files/shakespeare/hamlet.txt")
    # 2 bytes to encode W, 1 byte to encode L
    W = 2 ** 16 - 1
    L = 2 ** 8 - 1
    n = 8  # byte-wise
    start = time.time()
    print("Starting job at {}".format(start))
    out = zipper.lzss_bytewise_encode(bits, W, L)
    # print(out)
    print("Finished job at {}, after {} timeunits".format(time.time(), time.time() - start))
    start = time.time()
    print("Source length:", len(bits))
    print("Encoded length:", len(out))
    print("Compression ratio:", len(out) / len(bits))
    back = zipper.lzss_bytewise_decode(out, W, L)
    print("Finished decoding at {}, after {} timeunits".format(time.time(), time.time() - start))
    print("Success:", back == bits)
    write_bits("./files/out.mp3", back)


def fhir_set():
    return ["./files/fhir/" + i for i in os.listdir("./files/fhir/")]


batch(15 ** 2 - 1, 8 ** 2 - 1, fhir_set())
