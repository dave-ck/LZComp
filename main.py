import csv
import datetime
import os
import bitarray
import zipper
import time
import json


# processed data
def load_data():
    errors = 0
    data = {"lz77": {}, "lzss": {}}
    L_W_set = [(6, 8), (8, 8), (6, 10), (6, 16), (8, 12), (8, 16), (12, 12), (12, 16), (16, 16)]
    for log2_L, log2_W in L_W_set:
        LWtup = str((2 ** log2_L - 1, 2 ** log2_W - 1))
        data["lz77"].update({LWtup: {}})
        data["lzss"].update({LWtup: {}})
    # for clarity: source_file refers to the file compressed and decompressed.
    # metadata_file refers to the json file written elsewhere in this program
    for file_name in os.listdir("./outputs/json/raw/"):
        with open("./outputs/json/raw/" + file_name, "r") as json_file:
            metadata_file = json.load(json_file)
            for source_filename in metadata_file:
                # source_extension = source_filename[source_filename.index('.'):]
                sourcefile_metadata = metadata_file[source_filename]
                # identify L and W
                L, W = sourcefile_metadata["L"], sourcefile_metadata["W"]
                # identify algorithm used
                alg = file_name[:4].lower()
                # update data set
                try:
                    data[alg][str((L, W))].update({source_filename: metadata_file[source_filename]})
                except Exception as e:
                    print(e)
                    print(alg)
                    print(L, W)
                    print(source_filename)
                    errors += 1
                    pass
    print("finished wih {} errors writing into the dictionary".format(errors))
    return data


# raw data
def write_json(filename_header, dictionary, raw=True):
    if raw:
        with open("./outputs/json/raw/" + filename_header + "dump.json", "w") as json_file:
            json.dump(dictionary, json_file)

    else:
        with open("./outputs/json/processed/" + filename_header + "dump.json", "w") as json_file:
            json.dump(dictionary, json_file)


def write_csv(header, iterable_of_lists):
    with open("./outputs/" + datetime.datetime.now().strftime("%H-%M-%S") + header + "dump.csv", "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([header])
        for row in iterable_of_lists:
            writer.writerow(row)
    with open("out.csv", "a") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([header])
        for row in iterable_of_lists:
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
    # print(encoded)
    decoded = zipper.decode(encoded)
    # print("Decoded:", decoded)
    # print("Nocoded:", peter)
    # print(decoded == peter)


def bitwise_LZ():
    bits = read_bits("./files/source.txt")
    W = 63
    L = 31
    out = zipper.bitwise_encode(bits, W, L)
    # print("Source:", bits)
    # print("Source length:", len(bits))
    # print("Encoded:", out)
    # print("Encoded length:", len(out))
    # print("Remainder:", len(out) % (6 + 5 + 8))
    source = zipper.bitwise_decode(out, W, L)
    # print("Decoded:", source)
    # print("Decoded==source:", bits == source)


def lzss_batch(W, L, filePaths):
    data = {}
    for path in filePaths:
        # print("Processing", i)
        bits = read_bits(path)
        start = time.time()
        out = zipper.lzss_bytewise_encode(bits, W, L)
        encode_time = time.time() - start
        start = time.time()
        # print("Compression ratio:", len(bits) / len(out))
        start_size = len(bits)
        compressed_size = len(out)
        ratio = len(bits) / len(out)
        zipper.lzss_bytewise_decode(out, W, L)
        decode_time = time.time() - start
        data.update({path: {"W": W, "L": L, "encode": encode_time, "decode": decode_time, "source (bits)": start_size,
                            "encoded (bits)": compressed_size}})
    return data


def lz77_batch(W, L, filePaths):
    data = {}
    for path in filePaths:
        # print("Processing", i)
        bits = read_bits(path)
        start = time.time()
        out = zipper.lzss_bytewise_encode(bits, W, L)
        encode_time = time.time() - start
        start = time.time()
        # print("Compression ratio:", len(bits) / len(out))
        start_size = len(bits)
        compressed_size = len(out)
        ratio = len(bits) / len(out)
        zipper.lzss_bytewise_decode(out, W, L)
        decode_time = time.time() - start
        data.update({path: {"W": W, "L": L, "encode": encode_time, "decode": decode_time, "source (bits)": start_size,
                            "encoded (bits)": compressed_size}})
    return data


def fhir_set(n):
    return ["./files/fhir/" + i for i in os.listdir("./files/fhir/")][:n]


def shakespeare(n):
    return ["./files/shakespeare/" + i for i in os.listdir("./files/shakespeare/")][:n]


def lol_music(n):
    return ["./files/music/Albums/Warsongs_-_League_of_Legends/" + i for i in
            os.listdir("./files/music/Albums/Warsongs_-_League_of_Legends/")][:n]


def javacode(n):
    return ["./files/javacode/" + i for i in os.listdir("./files/javacode/")][:n]


def beethoven(n):
    beeth = ["./files/music/Other/Beethoven - Symphonies No 1 and 2/" + i for i in
             os.listdir("./files/music/Other/Beethoven - Symphonies No 1 and 2/")]
    beeth += ["./files/music/Other/Beethoven - Symphonies No 3 and 4/" + i for i in
              os.listdir("./files/music/Other/Beethoven - Symphonies No 3 and 4/")]
    beeth += ["./files/music/Other/Beethoven - Symphonies No 5 and 6/" + i for i in
              os.listdir("./files/music/Other/Beethoven - Symphonies No 5 and 6")]
    beeth += ["./files/music/Other/Beethoven - Symphonies No 7 and 8/" + i for i in
              os.listdir("./files/music/Other/Beethoven - Symphonies No 7 and 8/")]
    beeth += ["./files/music/Other/Beethoven - Symphonies No 9/" + i for i in
              os.listdir("./files/music/Other/Beethoven - Symphonies No 9/")]
    return beeth[:n]


def master_batch():
    L_W_set = [(6, 8), (8, 8), (6, 16), (8, 12), (8, 16), (12, 12), (12, 16), (16, 16)]
    datasets = {"shakespeare": shakespeare(10), "java": javacode(10), "fhir": fhir_set(30)}
    # datasets.update({"beethoven": beethoven(3), "league": lol_music(3)}
    for log2L, log2W in L_W_set:
        for data_name in datasets:
            # noinspection PyBroadException
            # need to run overnight and not produce results even if some files aren't readable/compressible
            print("Processing data-{}-Wbits-{}-Lbits-{}".format(data_name, log2W, log2L))
            try:
                data = datasets[data_name]
                # write_json("LZSS-data-{}-Wbits-{}-Lbits-{}".format(data_name, log2W, log2L),
                #           lzss_batch(2 ** log2W - 1, 2 ** log2L - 1, data))
                write_json("LZ77-data-{}-Wbits-{}-Lbits-{}".format(data_name, log2W, log2L),
                           lz77_batch(2 ** log2W - 1, 2 ** log2L - 1, data))
            except Exception:
                print("ERROR WITH data-{}-Wbits-{}-Lbits-{}".format(data_name, log2W, log2L))
                pass


def raspi_batch():
    L_W_set = [(6, 8), (8, 8), (6, 16), (8, 12), (8, 16), (12, 12), (12, 16), (16, 16)]
    datasets = {"shakespeare": shakespeare(3), "fhir": fhir_set(3)}
    # datasets.update({"beethoven": beethoven(3), "league": lol_music(3)}
    for log2L, log2W in L_W_set:
        for data_name in datasets:
            # noinspection PyBroadException
            # need to run overnight and not produce results even if some files aren't readable/compressible
            print("Processing data-{}-Wbits-{}-Lbits-{}".format(data_name, log2W, log2L))
            try:
                data = datasets[data_name]
                # write_json("LZSS-data-{}-Wbits-{}-Lbits-{}".format(data_name, log2W, log2L),
                #           lzss_batch(2 ** log2W - 1, 2 ** log2L - 1, data))
                write_json("LZ77-data-{}-Wbits-{}-Lbits-{}".format(data_name, log2W, log2L),
                           lz77_batch(2 ** log2W - 1, 2 ** log2L - 1, data))
            except Exception:
                print("ERROR WITH data-{}-Wbits-{}-Lbits-{}".format(data_name, log2W, log2L))
                pass
    return


if __name__ == '__main__':
    # facilitates running from pi zero
    print("Hello RasPI")
    raspi_batch()

# print(len(json.dumps(load_data(), indent=4)))
