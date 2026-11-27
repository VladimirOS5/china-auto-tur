# общие помощники для всех приложений


def digits_ok(phone):
    d = "".join(c for c in phone if c.isdigit())
    return len(d) == 11 and d[0] in "78"
