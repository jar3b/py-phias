# -*- coding: utf-8 -*-
import re

import Levenshtein


def violet_ratio(pattern, candidate):
    arr_pattern = re.split(r"[ ,:.#$-]+", pattern)
    arr_candidate = re.split(r"[ ,:.#$-]+", candidate)

    result = list()

    for i in range(len(arr_pattern) - 1, 0, -1):
        max_j = -1
        max_ratio = 0
        allowed_nums = range(len(arr_candidate) - 1, 0, -1)

        for j in allowed_nums:
            ratio = Levenshtein.ratio(arr_pattern[i], arr_candidate[j])
            if max_ratio < ratio:
                max_ratio = ratio
                max_j = j

        result.append(max_j*max_ratio)

        if max_j > -1:
            allowed_nums.remove(max_j)
            del arr_candidate[max_j]

    return sum(result) - len(arr_candidate)
