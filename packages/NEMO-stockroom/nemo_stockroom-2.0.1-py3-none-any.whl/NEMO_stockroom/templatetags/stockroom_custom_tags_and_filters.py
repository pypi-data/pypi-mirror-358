from django import template

register = template.Library()


@register.filter
def get_total_price(unit_price, qty):
    unit_price = float(unit_price)
    qty = float(qty)
    return str(round(unit_price / qty, 2))


@register.filter
def get_request_date(cw):
    try:
        return cw.consumablerequest_set.all()[0].date
    except Exception:
        return "N/A"
