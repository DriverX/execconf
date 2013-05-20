MERGE = False

OPT1 = {
    "FOO": 1,
    "BAR": {
        "BAZ": 2
    },
    "QUX": 3
}

OPT2 = {
    "LVL1_KEY1": True,
    "LVL1": {
        "LVL2_KEY1": True,
        "LVL2": {
            "LVL3_KEY1": True,
            "LVL3": {
                "LVL4_KEY1": True
            }
        }
    },
}

OPT3 = {
    "LVL1_KEY1": True,
    "LVL1": {
        "LVL2_KEY1": True,
        "LVL2": {
            "LVL3_KEY1": True,
            "LVL3": {
                "LVL4_KEY1": True
            }
        }
    },
}

OPT4 = {
    "FOO": 1
}

OPT5 = "FOO"

OPT7 = True

merge_option("merge_option-merging", ["MERGE", "OPT1"])
merge_option("merge_option-merging", "OPT2", depth=1)
merge_option("merge_option-merging", "OPT3", depth=3)
merge_option("merge_option-merging2", "OPT4")
merge_option("merge_option-merging2", "OPT6")
merge_option("merge_option-merging2", "OPT7")
merge_option("merge_option-merging2", "OPT8")

