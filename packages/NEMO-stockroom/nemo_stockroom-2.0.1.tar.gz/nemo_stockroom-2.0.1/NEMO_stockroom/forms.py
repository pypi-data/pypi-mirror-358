from NEMO.models import Consumable
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from NEMO_stockroom.models import ConsumableRequest


class ConsumableRequestForm(ModelForm):
    class Meta:
        model = ConsumableRequest
        fields = ["project", "consumable", "quantity"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["consumable"].queryset = Consumable.objects.filter(visible=True)

    def clean_project(self):
        project = self.cleaned_data["project"]
        if not project.active:
            raise ValidationError(
                "A consumable may only be billed to an active project. The user's project is inactive."
            )
        if not project.account.active:
            raise ValidationError(
                "A consumable may only be billed to a project that belongs to an active account. The user's account is inactive."
            )
        return project

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity < 1:
            raise ValidationError("Please specify a valid quantity of items to withdraw.")
        return quantity

    def clean(self):
        if any(self.errors):
            return
        cleaned_data = super().clean()
        quantity = cleaned_data["quantity"]
        consumable = cleaned_data["consumable"]
        if not consumable.reusable and quantity > consumable.quantity:
            raise ValidationError(
                'There are not enough "'
                + consumable.name
                + '". (The current quantity in stock is '
                + str(consumable.quantity)
                + "). Please order more as soon as possible."
            )
        project = cleaned_data["project"]
        return cleaned_data
