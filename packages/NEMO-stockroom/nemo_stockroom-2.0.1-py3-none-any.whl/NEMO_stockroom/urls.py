from django.conf.urls.static import static
from django.urls import path

import settings
from NEMO_stockroom import views

urlpatterns = [
    # Requesting for users
    path("stockroom/", views.stockroom, name="stockroom"),
    path("stockroom/<int:index>/remove/", views.remove_order_at_index, name="remove_order"),
    path("stockroom/order/", views.make_orders, name="order_consumables"),
    path("stockroom/clear/", views.clear_orders, name="clear_orders"),
    # Staff fulfilling orders
    path("stockroom/requests", views.stockroom_requests, name="stockroom_requests"),
    path("stockroom/requests/delete/<int:consumable_id>/", views.delete_order, name="delete_order"),
    path("stockroom/requests/cancel/<int:consumable_id>/", views.cancel_order, name="cancel_order"),
    path("stockroom/requests/fulfill/<int:consumable_request_id>/", views.fulfill_order, name="fulfill_order"),
    # Order status pages
    path("stockroom/order_history", views.order_history, name="order_history"),
    path("stockroom/withdraws", views.display_withdraws, name="display_withdraws"),
    # Display, and allow staff to update, quantities of items in the stockroom
    path("stockroom/items", views.items_page, name="items_page"),
    # For users to update quantity of their request before it's fulfilled
    path("stockroom/update_qty_in_session/", views.update_qty_in_session, name="update_qty_in_session"),
    path(
        "stockroom/update_qty_in_pending_order/", views.update_qty_in_pending_order, name="update_qty_in_pending_order"
    ),
    # Fetch specific data from the database
    # path("stockroom/requests/get_consumable_qty/<ind:consumable_request_id>", stockroom_custom_tags_and_filters.get_consumable_qty, name="get_consumable_qty"),
    # If using this Django debugger, enable this
    # Django debugger:  https://django-debug-toolbar.readthedocs.io/en/latest/
    # path('__debug__/', include('debug_toolbar.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
