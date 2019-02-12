import bitarray
import lz77


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


def main():
    bits = read_bits("./files/source.txt")
    W = 63
    L = 31
    out = lz77.bitwise_encode(bits, W, L)
    print("Source:", bits)
    print("Source length:", len(bits))
    print("Encoded:", out)
    print("Encoded length:", len(out))
    print("Remainder:", len(out) % (6 + 5 + 8))
    source = lz77.bitwise_decode(out, W, L)
    print("Decoded:", source)
    print("Decoded==source:", bits==source)
    peter = "Peter Piper picked a peck of pickled peppers; " \
            "A peck of pickled peppers Peter Piper picked; " \
            "If Peter Piper picked a peck of pickled peppers, " \
            "Where's the peck of pickled peppers Peter Piper picked?"
    encoded = lz77.encode(peter, 32, 16)
    print(encoded)
    decoded = lz77.decode(encoded)
    print("Decoded:", decoded)
    print("Nocoded:", peter)

    print(decoded == peter)


main()
