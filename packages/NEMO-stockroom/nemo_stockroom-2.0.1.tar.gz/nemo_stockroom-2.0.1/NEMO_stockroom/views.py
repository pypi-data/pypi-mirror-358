from logging import getLogger
from typing import List, Optional

from NEMO.decorators import staff_member_required
from NEMO.exceptions import ProjectChargeException
from NEMO.models import Consumable, ConsumableWithdraw, User
from NEMO.policy import policy_class as policy
from NEMO.utilities import (
    BasicDisplayTable,
    EmailCategory,
    export_format_datetime,
    extract_optional_beginning_and_end_dates,
    get_month_timeframe,
    month_list,
    send_mail,
)
from NEMO.views.customization import ApplicationCustomization, EmailsCustomization
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from NEMO_stockroom.customizations import StockroomCustomization
from NEMO_stockroom.forms import ConsumableRequestForm
from NEMO_stockroom.models import ConsumableRequest, QuantityModification
from NEMO_stockroom.templatetags.stockroom_custom_tags_and_filters import get_request_date

consumables_logger = getLogger(__name__)


@login_required
@require_http_methods(["GET", "POST"])
def stockroom(request):
    user: User = request.user
    if request.method == "GET":
        from NEMO.rates import rate_class

        rate_dict = rate_class.get_consumable_rates(Consumable.objects.all())
        consumables = Consumable.objects.filter(visible=True).order_by("category", "name")
        dictionary = {
            "customer": user,
            "consumables": consumables,
            "consumables_set": set(consumables),
            "rates": rate_dict,
            "projects": user.active_projects().filter(allow_consumable_withdrawals=True),
            "consumable_list_collapse": False,
        }
        return render(request, "NEMO_stockroom/stockroom.html", dictionary)
    elif request.method == "POST":
        form = ConsumableRequestForm(request.POST)
        if form.is_valid():
            withdraw = form.save(commit=False)
            try:
                future_withdrawal = ConsumableWithdraw(
                    consumable_id=withdraw.consumable_id,
                    quantity=withdraw.quantity,
                    merchant=user,
                    customer_id=user.id,
                    project_id=withdraw.project_id,
                )
                policy.check_billing_to_project(withdraw.project, user, withdraw.consumable, future_withdrawal)
            except ProjectChargeException as e:
                return HttpResponseBadRequest(e.msg)
            add_order_to_session(request, withdraw)
        else:
            return HttpResponseBadRequest(form.errors.as_ul())
        return render(request, "NEMO_stockroom/stockroom_order.html")


@staff_member_required
@require_http_methods(["GET", "POST"])
def stockroom_requests(request):
    from NEMO.rates import rate_class

    rate_dict = rate_class.get_consumable_rates(Consumable.objects.all())
    consumable_requests = ConsumableRequest.objects.filter(withdraw__isnull=True)
    user_set = set()
    for cr in consumable_requests:
        user_set.add(cr.customer)
    if request.method == "GET":
        if request.GET.get("start") or request.GET.get("end"):
            start_date, end_date = extract_optional_beginning_and_end_dates(request.GET, date_only=True)
        else:
            start_date, end_date = get_month_timeframe()
    elif request.method == "POST":
        if request.POST.get("start") or request.POST.get("end"):
            start_date, end_date = extract_optional_beginning_and_end_dates(request.POST, date_only=True)
        else:
            start_date, end_date = get_month_timeframe()
        if request.POST.get("stockroom_requests_user_id"):
            user_id = request.POST["stockroom_requests_user_id"]
            consumable_requests = consumable_requests.filter(customer_id=user_id)
        consumable_requests = consumable_requests.filter(date__gte=start_date, date__lte=end_date)
    dictionary = {
        "start_date": start_date,
        "end_date": end_date,
        "month_list": month_list(),
        "consumable_requests": consumable_requests,
        "user_set": user_set,
        "rates": rate_dict,
    }
    return render(request, "NEMO_stockroom/stockroom_requests.html", dictionary)


@staff_member_required
@require_POST
def reset_stockroom_requests(request):
    return


def add_order_to_session(request, withdrawal: ConsumableRequest):
    request.session.setdefault("withdrawals", [])
    withdrawals: List = request.session.get("withdrawals")
    if withdrawals is not None:
        withdrawal_dict = {
            "consumable": str(withdrawal.consumable),
            "consumable_id": withdrawal.consumable_id,
            "project": str(withdrawal.project),
            "project_id": withdrawal.project_id,
            "quantity": withdrawal.quantity,
            "withdrawal_id": len(withdrawals),
        }
        withdrawals.append(withdrawal_dict)
    request.session["withdrawals"] = withdrawals


@login_required
@require_POST
def update_qty_in_session(request):
    withdrawal_id = int(request.POST.get("update_withdrawal_id"))
    new_qty = request.POST.get("update_quantity")
    withdrawals = request.session.get("withdrawals")
    for w in withdrawals:
        if w["withdrawal_id"] == withdrawal_id:
            w["quantity"] = new_qty
    return redirect("stockroom")


@login_required
@require_POST
def update_qty_in_pending_order(request):
    cr_id = request.POST.get("update_pending_request_id")
    cr = ConsumableRequest.objects.get(id=cr_id)
    new_qty = request.POST.get("update_quantity")
    cr.quantity = new_qty
    cr.save()
    return redirect("order_history")


@login_required
@require_GET
def remove_order_at_index(request, index: str):
    try:
        index = int(index)
        withdrawals: List = request.session.get("withdrawals")
        if withdrawals:
            del withdrawals[index]
            request.session["withdrawals"] = withdrawals
    except Exception as e:
        consumables_logger.exception(e)
    return render(request, "NEMO_stockroom/stockroom_order.html")


@login_required
@require_GET
def clear_orders(request):
    if "withdrawals" in request.session:
        del request.session["withdrawals"]
    return render(request, "NEMO_stockroom/stockroom_order.html")


@login_required
@require_POST
def make_orders(request):
    withdrawals: List = request.session.setdefault("withdrawals", [])
    for withdraw in withdrawals:
        consumable_id = withdraw["consumable_id"]
        # Update qtys in the qty session variables from the input
        for key, value in request.POST.items():
            if key[0:9] == "qty_box__":
                field_name, separator, id = key.partition("__")
                id = int(id)
                if id == withdraw.get("withdrawal_id"):
                    withdraw["quantity"] = value
        make_order(
            consumable_id=consumable_id,
            quantity=withdraw["quantity"],
            project_id=withdraw["project_id"],
            customer=request.user,
            request=request,
        )
    del request.session["withdrawals"]
    return redirect("stockroom")


def make_order(consumable_id: int, quantity: int, project_id: int, customer: User, request=None):
    order = ConsumableRequest.objects.create(
        consumable_id=consumable_id,
        quantity=quantity,
        customer=customer,
        project_id=project_id,
    )
    # Only add notification message if request is present
    if request:
        message = f"Your order of {order.quantity} of {order.consumable}"
        message += f" was successfully logged and will be billed to project {order.project} once it is fulfilled."
        messages.success(request, message, extra_tags="data-speed=9000")


@login_required
@staff_member_required
def delete_order(request, consumable_id):
    consumable = ConsumableRequest.objects.get(id=consumable_id)
    consumable.deleted = True
    consumable.date_deleted = timezone.now()
    consumable.save()
    return HttpResponseRedirect(reverse("stockroom_requests"))


@login_required
def cancel_order(request, consumable_id):
    consumable = ConsumableRequest.objects.get(id=consumable_id)
    consumable.deleted = True
    consumable.date_deleted = timezone.now()
    consumable.save()
    return HttpResponseRedirect(reverse("order_history"))


@login_required
@staff_member_required
def fulfill_order(request, consumable_request_id):
    c = ConsumableRequest.objects.get(id=consumable_request_id)
    c.quantity = int(request.POST.get("request_qty"))
    if c.quantity > c.consumable.quantity:
        message = f"ERROR:  There aren't enough {c.consumable}'s to fulfill this order.  "
        message += f"There are {c.consumable.quantity} in the system, but {c.quantity} were requested.  "
        message += f"Please add more {c.consumable}'s to the system before fulfilling this order."
        messages.error(request, message, extra_tags="data-speed=9000")
        return HttpResponseRedirect(reverse("stockroom_requests"))
    withdrawal = ConsumableWithdraw.objects.create(
        consumable_id=c.consumable_id,
        quantity=c.quantity,
        merchant=request.user,
        customer_id=c.customer_id,
        project_id=c.project_id,
    )
    c.withdraw = withdrawal
    qm = QuantityModification.objects.create(
        modification_type=QuantityModification.ModificationType.FULFILLED,
        old_qty=c.consumable.quantity,
        new_qty=c.consumable.quantity - withdrawal.quantity,
        consumable=c.consumable,
        withdraw=withdrawal,
        modifier=request.user,
    )
    qm.save()
    consumable_to_update = Consumable.objects.get(id=withdrawal.consumable_id)
    consumable_to_update.quantity -= withdrawal.quantity
    consumable_to_update.save()
    c.withdraw.merchant = request.user
    c.save()
    send_stockroom_order_confirmation_email(c.withdraw, request)
    message = f"Order of {c.quantity} {c.consumable}'s for {c.customer.first_name} {c.customer.last_name} "
    message += f"fulfilled successfully."
    messages.success(request, message, extra_tags="data-speed=9000")
    return HttpResponseRedirect(reverse("stockroom_requests"))


def send_stockroom_order_confirmation_email(withdrawal: ConsumableWithdraw, request):
    """
    withdrawal:  ConsumableWithdraw associated w/ this order
    """
    facility_name = ApplicationCustomization.get("facility_name")
    subject = f"{facility_name} Stockroom order confirmation: {withdrawal.quantity} {withdrawal.consumable.name}"
    message = StockroomCustomization.render_template(
        "stockroom_order_confirmation_email.html", {"withdrawal": withdrawal}, request
    )
    if not message:
        message = f"""Hello {withdrawal.customer.first_name},<br><br>
		Your order for {withdrawal.quantity} {withdrawal.consumable.name} from the {facility_name} stockroom was fulfilled by {withdrawal.merchant.first_name} {withdrawal.merchant.last_name} 
		on {withdrawal.date}.  The {withdrawal.quantity} {withdrawal.consumable.name} should be available in your group's designated drop-off location.<br>
		Please reply to this email if you have any questions.<br><br>
		Thank you,<br>
		{facility_name} Staff"""
    user_office_email = EmailsCustomization.get("user_office_email_address")
    send_mail(
        subject=subject,
        content=message,
        from_email=user_office_email,
        to=[withdrawal.customer.email],
        email_category=EmailCategory.GENERAL,
    )


@login_required
@require_GET
def order_history(request):
    user = request.user
    deleted_orders = ConsumableRequest.objects.filter(customer=user).filter(deleted=True)
    pending_orders = ConsumableRequest.objects.filter(customer=user).filter(withdraw__isnull=True)
    fulfilled_orders = ConsumableRequest.objects.filter(customer=user).filter(withdraw__isnull=False)
    dictionary = {
        "user": user,
        "deleted_orders": deleted_orders,
        "pending_orders": pending_orders,
        "fulfilled_orders": fulfilled_orders,
    }
    return render(request, "NEMO_stockroom/order_history.html", dictionary)


@login_required
@staff_member_required
@require_GET
def display_withdraws(request):
    from NEMO.rates import rate_class

    rate_dict = rate_class.get_consumable_rates(Consumable.objects.all())
    consumable_withdraws = ConsumableWithdraw.objects.all()
    user_set = set()
    selected_user: Optional[User] = None
    for cw in consumable_withdraws:
        user_set.add(cw.customer)
    if request.GET.get("start") or request.GET.get("end"):
        start_date, end_date = extract_optional_beginning_and_end_dates(request.GET, date_only=True)
    else:
        start_date, end_date = get_month_timeframe()
    if request.GET.get("stockroom_withdrawals_user_id"):
        user_id = request.GET["stockroom_withdrawals_user_id"]
        consumable_withdraws = consumable_withdraws.filter(customer_id=user_id)
        selected_user = User.objects.filter(id=user_id).first()
    consumable_withdraws = (
        consumable_withdraws.filter(date__gte=start_date, date__lte=end_date)
        .order_by("-date")
        .prefetch_related("consumablerequest_set")
    )
    if bool(request.GET.get("csv", False)):
        return csv_export_withdraws(consumable_withdraws, rate_dict)
    dictionary = {
        "start_date": start_date,
        "end_date": end_date,
        "selected_user": selected_user,
        "month_list": month_list(),
        "consumable_withdraws": consumable_withdraws,
        "user_set": user_set,
        "rates": rate_dict,
    }
    return render(request, "NEMO_stockroom/stockroom_withdraws.html", dictionary)


@login_required
@staff_member_required
@require_http_methods(["GET", "POST"])
def items_page(request):
    from NEMO.rates import rate_class

    consumables = Consumable.objects.filter(visible=True).order_by("category", "name")
    rate_dict = rate_class.get_consumable_rates(Consumable.objects.all())
    search_item = ""
    if request.method == "POST":
        if "clicked_submit" in request.POST.keys():
            if request.POST["clicked_submit"] == "true":
                # Update the quantities of the stockroom items
                for key, value in request.POST.items():
                    if key[0:21] == "stockroom_qty_input__":
                        field_name, separator, id = key.partition("__")
                        if field_name == "stockroom_qty_input":
                            id = int(id)
                            consumable = Consumable.objects.get(id=id)
                            value = int(value)
                            # Record quantity modification
                            if abs(consumable.quantity - value) != 0:
                                qm = QuantityModification.objects.create(
                                    modification_type=QuantityModification.ModificationType.EDITED,
                                    old_qty=consumable.quantity,
                                    new_qty=value,
                                    consumable=consumable,
                                    withdraw=None,
                                    modifier=request.user,
                                )
                                qm.save()
                            consumable.quantity = value
                            consumable.save()
                consumables = Consumable.objects.filter(visible=True).order_by("category", "name")
                message = f"Item quantities updated successfully!"
                messages.success(request, message, extra_tags="data-speed=9000")
        else:
            search_item = request.POST["search_stockroom_items"]
            consumables = (
                Consumable.objects.filter(visible=True).filter(name__icontains=search_item).order_by("category", "name")
            )
    dictionary = {
        "consumables": consumables,
        "consumables_set": set(consumables),
        "consumable_list_collapse": False,
        "rates": rate_dict,
        "search_item": search_item,
    }
    return render(request, "NEMO_stockroom/stockroom_items.html", dictionary)


def csv_export_withdraws(consumable_withdraws, rate_dict):
    table_result = BasicDisplayTable()
    table_result.add_header(("name", "Name"))
    table_result.add_header(("username", "Username"))
    table_result.add_header(("item", "Item"))
    table_result.add_header(("price", "Price"))
    table_result.add_header(("qty", "Quantity"))
    table_result.add_header(("project", "Project"))
    table_result.add_header(("account", "Account"))
    table_result.add_header(("date_fulfilled", "Date Fulfilled"))
    table_result.add_header(("date_requested", "Date of Request"))
    table_result.add_header(("merchant", "Order Fulfilled By"))
    cw_list = list(consumable_withdraws)
    for cw in cw_list:
        row = {
            "name": cw.customer.first_name + " " + cw.customer.last_name,
            "username": cw.customer.username,
            "item": cw.consumable.name,
            "price": rate_dict.get(cw.consumable.name).strip("<b>").strip("</b>"),
            "qty": cw.quantity,
            "project": cw.project,
            "account": cw.project.account.name,
            "date_fulfilled": cw.date,
            "date_requested": get_request_date(cw),
            "merchant": cw.merchant.first_name + " " + cw.merchant.last_name,
        }
        table_result.add_row(row)
    response = table_result.to_csv()
    filename = f"consumable_withdraws_export_{export_format_datetime()}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
