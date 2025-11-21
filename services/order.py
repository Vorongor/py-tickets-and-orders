from datetime import datetime

from django.db import transaction
from django.db.models import QuerySet

from db.models import Ticket, Order
from services.user import get_user_by_username


def create_order(
        tickets: list[dict[str, int]],
        username: str,
        date: str = None
) -> None:
    from django.utils import timezone

    with transaction.atomic():
        user = get_user_by_username(username)

        if date:
            provided_date = datetime.strptime(date, "%Y-%m-%d %H:%M")
        else:
            provided_date = timezone.now()

        order = Order.objects.create(user=user)
        if date:
            Order.objects.filter(id=order.id).update(created_at=provided_date)
            order.refresh_from_db()

        for tick in tickets:
            ticket = Ticket(
                row=tick["row"],
                seat=tick["seat"],
                movie_session_id=tick["movie_session"],
                order=order,
            )
            ticket.full_clean()
            ticket.save()


def get_orders(username: str = None) -> QuerySet:
    orders = Order.objects.all()

    if username:
        orders = orders.filter(user__username__icontains=username)

    return orders
