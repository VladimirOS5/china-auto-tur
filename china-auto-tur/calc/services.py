# расчёт под ключ и кредита: только Decimal, округление до рубля
from decimal import Decimal, ROUND_HALF_UP


def rub(value):
    return Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def turnkey(price_cny, rate, power, row, fees):
    price = rub(Decimal(price_cny) * rate)
    duty = rub(price * row.duty / 100)
    excise = rub(Decimal(power) * row.excise)
    vat = rub((price + duty + excise) * row.vat / 100)
    util = rub(row.util)
    extra = rub(sum((f.amount for f in fees), Decimal("0")))
    total = price + duty + excise + vat + util + extra
    return dict(price=price, duty=duty, excise=excise, vat=vat, util=util, extra=extra, total=total)


def credit(total, down_pct, months, annual):
    down = rub(total * Decimal(down_pct) / 100)
    body = total - down
    r = Decimal(annual) / 12 / 100
    n = int(months)
    if r == 0:
        pay = rub(body / n)
    else:
        k = (1 + r) ** n
        pay = rub(body * r * k / (k - 1))
    rows = []
    rest = body
    paid = Decimal("0")
    for m in range(1, n + 1):
        pct = rub(rest * r)
        if m == n:
            main = rest
            p = main + pct
        else:
            p = pay
            main = p - pct
        rest -= main
        paid += p
        rows.append([m, p, pct, main, max(rest, Decimal("0"))])
    return dict(down=down, body=body, pay=pay, over=rub(paid - body), rows=rows)
