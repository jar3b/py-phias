import Levenshtein
import re


def violet_ratio(pattern, candidate):
    arr_pattern = re.split(r"[ ,:.#$-]+", pattern)
    arr_candidate = re.split(r"[ ,:.#$-]+", candidate)

    result = list()

    for i in range(len(arr_pattern) - 1, -1, -1):
        max_j = -1
        max_ratio = -1
        allowed_nums = list(range(len(arr_candidate) - 1, -1, -1))

        for j in allowed_nums:
            ratio = Levenshtein.ratio(arr_pattern[i], arr_candidate[j])
            if max_ratio < ratio:
                max_ratio = ratio
                max_j = j

        result.append(max_j * abs(max_ratio))

        if max_j > -1:
            del allowed_nums[max_j]
            del arr_candidate[max_j]

    return sum(result) - len(arr_candidate)
