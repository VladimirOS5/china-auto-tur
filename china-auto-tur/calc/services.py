"""Расчёты под ключ и кредита. Деньги только Decimal, округление половины вверх."""

from decimal import Decimal, ROUND_HALF_UP

ZERO = Decimal("0")


def money(value):
    # до целых рублей по правилу половины вверх, как в пояснительной записке
    return Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def customs_payments(price_rub, power_hp, rate):
    # пошлина от стоимости, акциз от мощности, НДС от суммы стоимости+пошлина+акциз
    duty = money(price_rub * rate.duty_percent / 100)
    excise = money(Decimal(power_hp) * rate.excise_per_hp)
    vat = money((price_rub + duty + excise) * rate.vat_percent / 100)
    util = money(rate.util_fee)
    total = duty + excise + vat + util
    return {"duty": duty, "excise": excise, "vat": vat, "util": util, "total": total}


def turnkey(price_cny, cny_rate, power_hp, rate, fees):
    price_rub = money(Decimal(price_cny) * cny_rate)
    customs = customs_payments(price_rub, power_hp, rate)
    fees_total = money(sum((f.amount_rub for f in fees), ZERO))
    total = price_rub + customs["total"] + fees_total
    return {
        "price_rub": price_rub,
        "customs": customs,
        "fees_total": fees_total,
        "total": total,
    }


def annuity(total_rub, down_percent, months, annual_percent):
    # аннуитет: P = S * r * (1+r)^n / ((1+r)^n - 1), график помесячно
    down = money(total_rub * Decimal(down_percent) / 100)
    principal_sum = total_rub - down
    r = Decimal(annual_percent) / 12 / 100
    n = int(months)

    if r == 0:
        payment = money(principal_sum / n)
    else:
        k = (1 + r) ** n
        payment = money(principal_sum * r * k / (k - 1))

    schedule = []
    balance = principal_sum
    paid = ZERO
    for m in range(1, n + 1):
        interest = money(balance * r)
        if m == n:
            # последний месяц гасим остаток тела, чтобы не剩下 копеек
            principal = balance
            pay = principal + interest
        else:
            pay = payment
            principal = pay - interest
        balance -= principal
        paid += pay
        schedule.append(
            {
                "month": m,
                "payment": pay,
                "interest": interest,
                "principal": principal,
                "balance": max(balance, ZERO),
            }
        )

    return {
        "down": down,
        "credit_sum": principal_sum,
        "payment": payment,
        "overpay": money(paid - principal_sum),
        "schedule": schedule,
    }
