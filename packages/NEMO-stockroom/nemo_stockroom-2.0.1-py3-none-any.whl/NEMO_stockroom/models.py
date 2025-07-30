from NEMO.models import BaseModel, Consumable, ConsumableWithdraw, Project, User
from django.db import models
from django.utils import timezone


class ConsumableRequest(BaseModel):
    customer = models.ForeignKey(
        User,
        related_name="consumable_requester",
        help_text="The user who will use the consumable item.",
        on_delete=models.CASCADE,
    )
    consumable = models.ForeignKey(Consumable, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    project = models.ForeignKey(
        Project, help_text="The withdraw will be billed to this project.", on_delete=models.CASCADE
    )
    date = models.DateTimeField(
        default=timezone.now, help_text="The date and time when the user placed the request for the consumable."
    )
    withdraw = models.ForeignKey(
        ConsumableWithdraw,
        null=True,
        blank=True,
        help_text="Withdrawal associated with this request",
        on_delete=models.CASCADE,
    )
    deleted = models.BooleanField(default=False, help_text="Marks request as deleted")
    date_deleted = models.DateTimeField(
        default=None, null=True, blank=True, help_text="The date and time when the request was marked as fulfilled."
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return str(self.id)


class QuantityModification(BaseModel):
    class ModificationType(object):
        FULFILLED = "Fulfilled order"
        EDITED = "Edited"
        Choices = (
            (FULFILLED, "Fulfilled order"),
            (EDITED, "Edited"),
        )

    modification_type = models.CharField(max_length=15, choices=ModificationType.Choices, default=None)
    old_qty = models.PositiveIntegerField()
    new_qty = models.PositiveIntegerField()
    consumable = models.ForeignKey(Consumable, on_delete=models.CASCADE)
    withdraw = models.ForeignKey(
        ConsumableWithdraw,
        null=True,
        blank=True,
        help_text="Withdrawal associated with this request",
        on_delete=models.CASCADE,
    )
    modifier = models.ForeignKey(
        User,
        related_name="consumable_qty_modifier",
        help_text="The user who modified the quantity of this consumable.",
        on_delete=models.CASCADE,
    )
    date = models.DateTimeField(
        default=timezone.now, help_text="The date and time when the consumable quantity was modified."
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return str(self.id)


class ConsumableDetails(BaseModel):
    consumable = models.OneToOneField(Consumable, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to="stockroom_thumbnails/", null=True, blank=True, help_text="The thumbnail image for this item"
    )
    warning_message = models.TextField(
        null=True,
        blank=True,
        help_text="The warning message to show users when they are ordering this item. HTML is NOT allowed.",
    )

    class Meta:
        ordering = ["consumable"]
        verbose_name_plural = "Consumable details"

    def __str__(self):
        return f"{self.consumable.name} details"
