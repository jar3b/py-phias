def trigram(inp: str) -> str:
    inp = u"__" + inp + u"__"
    return " ".join([inp[i:i + 3] for i in range(0, len(inp) - 2)])
