import json
import sys

import matplotlib.pyplot as plt
import numpy as np


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def print_statistics(lengths, label):
    arr = np.array(lengths)
    print(f"Statistics for {label}:")
    print(f"  Count   : {len(arr)}")
    print(f"  Min     : {arr.min()}")
    print(f"  Max     : {arr.max()}")
    print(f"  Mean    : {arr.mean():.2f}")
    print(f"  Median  : {np.median(arr)}")
    print(f"  Std Dev : {arr.std():.2f}")
    print()


def main(file1_path, file2_path):
    data1 = load_json(file1_path)
    data2 = load_json(file2_path)

    common_keys = set(data1.keys()) & set(data2.keys())
    print(f"# Common keys: {len(common_keys)}\n")

    lengths_file1 = []
    lengths_file2 = []

    for key in common_keys:
        val1, val2 = data1[key], data2[key]
        if isinstance(val1, list) and isinstance(val2, list):
            lengths_file1.append(len(val1))
            lengths_file2.append(len(val2))

    print(f"Number of values for common keys in File 1: {len(lengths_file1)}")
    print(f"Number of values for common keys in File 2: {len(lengths_file2)}")

    allt = [
        12317,
        12311,
        12873,
        12657,
        12679,
        12683,
        12697,
        12858,
        12786,
        12785,
        12755,
        12762,
        12770,
        12782,
        13062,
        12776,
        12778,
        12783,
        12785,
        12785,
        12788,
        12816,
        12799,
        12795,
        12796,
        12912,
        12962,
        12850,
        12867,
        12890,
        12873,
        12911,
        12923,
        12926,
        12927,
        13024,
        13024,
        13026,
        13035,
        13026,
        13053,
        13050,
        13053,
        13060,
        13061,
        13100,
        13114,
        13129,
        13281,
        13289,
        13332,
        13333,
        13331,
        13367,
        13405,
        13409,
        13428,
        13416,
        13421,
        13720,
        13433,
        13468,
        13472,
        13600,
        13661,
        13627,
        13655,
        13771,
        13659,
        13688,
        13767,
        13786,
        13820,
        13830,
        13834,
        13922,
        13942,
        13950,
        13953,
        13954,
        13966,
        13990,
        14010,
        14064,
        14087,
        14288,
        14113,
        14104,
        14103,
        14112,
        14127,
        14131,
        14141,
        14133,
        14218,
        14248,
        14251,
        14249,
        14273,
        14270,
        14282,
        14285,
        14357,
        14367,
        14417,
        14440,
        14441,
        14445,
        14436,
        14445,
        14449,
        14450,
        14453,
        14443,
        14449,
        14456,
        14641,
        14477,
        14911,
        14517,
        14538,
        14556,
        14559,
        14621,
        14604,
        14643,
        14717,
        14665,
        14677,
        14674,
        14680,
        14682,
        14696,
        14709,
        14754,
        14758,
        14910,
        14786,
        14783,
        14770,
        14842,
        14842,
        14888,
        15535,
        14936,
        14949,
        14816,
        14974,
        15098,
        14820,
        14994,
        14941,
        14940,
        14999,
        15483,
        15461,
        15460,
        15475,
        15497,
        15534,
        15541,
        15543,
        15613,
        15650,
        15653,
        15662,
        15709,
        15711,
        15815,
        15834,
        15824,
        15889,
        15924,
        15936,
        15955,
        15966,
        16022,
        16022,
        16019,
        16056,
        16062,
        16104,
        16111,
        16172,
        16159,
        16192,
        16304,
        16377,
        16464,
        8700,
        13057,
        7887,
        7892,
        8171,
        8187,
        8241,
        8256,
        8515,
        8742,
        8781,
        8783,
        8938,
        8905,
        8951,
        8952,
        9106,
        9126,
        9128,
        9129,
        9138,
        9163,
        9191,
        9194,
        9204,
        9285,
        9285,
        9286,
        9363,
        9410,
        9472,
        9428,
        9486,
        9502,
        9534,
        9557,
        13601,
        8404,
        8400,
        8713,
        10478,
        13250,
        12408,
        12859,
        13402,
        13107,
        10384,
        13145,
        13679,
        10839,
        10795,
        15866,
        15867,
        15918,
        15946,
        16658,
        16052,
        16696,
        9716,
        9970,
        10547,
        12658,
        10718,
        10774,
        10777,
        10777,
        11686,
        11739,
        11769,
        12393,
        12569,
        12559,
        12589,
        12962,
        13022,
        13164,
        13813,
        13436,
        13749,
        27774,
        27597,
        28074,
        28165,
        28208,
        28471,
        29405,
        12994,
        7205,
        7351,
        7435,
        7446,
        7485,
        7594,
        7671,
        8134,
        8141,
    ]
    print(allt)
    print(lengths_file1)
    print(lengths_file2)

    exit(0)
    print_statistics(lengths_file1, "File 1")
    print_statistics(lengths_file2, "File 2")

    # Box plot
    plt.figure(figsize=(8, 6))
    box = plt.boxplot(
        [lengths_file1, lengths_file2], labels=["File 1", "File 2"], patch_artist=True
    )

    # Custom colors
    colors = ["skyblue", "lightgreen"]
    for patch, color in zip(box["boxes"], colors):
        patch.set_facecolor(color)

    plt.title("Boxplot of Number of Values for Common Keys")
    plt.ylabel("Number of Values")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("common_key_value_lengths_boxplot.pdf")
    # plt.show()


if __name__ == "__main__":
    j2 = "ten_coverage_tests_mini_model.json"
    j1 = "ten_files_combined_tests.json"
    main(j1, j2)
