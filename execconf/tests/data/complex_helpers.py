COMPLEX = True

FOO = 1

MERGE_INCLUDE = {
    "FOO": 1,
}

include("complex_helpers-include")
merge("complex_helpers-merge")
merge_option("complex_helpers-merge_option", "COMPLEX_MERGE_OPTION")
merge_option("complex_helpers-merge_option", "MERGE_INCLUDE")
merge_option("complex_helpers-merge_option", "MERGE_OPTION1")
merge_option("complex_helpers-merge_option", "MERGE_OPTION2", depth=1)


