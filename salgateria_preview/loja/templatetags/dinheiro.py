from django import template

register = template.Library()


def _fmt(centavos):
    inteiro, resto = divmod(int(centavos or 0), 100)
    return f"{inteiro:,}".replace(",", ".") + f",{resto:02d}"


@register.filter
def reais(centavos):
    """750 -> 'R$ 7,50'"""
    return "R$ " + _fmt(centavos)


@register.filter
def num(centavos):
    """750 -> '7,50'"""
    return _fmt(centavos)
