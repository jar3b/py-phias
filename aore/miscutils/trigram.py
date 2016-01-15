# -*- coding: utf-8 -*-


def trigram(inp):
    inp = u"__"+inp+u"__"
    output = []

    for i in range(0, len(inp) - 2):
        output.append(inp[i:i + 3])

    return " ".join(output)
