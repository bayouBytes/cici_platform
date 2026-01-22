from django.db import models
from django.conf import settings  # To reference users.User
from inventory.models import Meal
from djmoney.models.fields import MoneyField
class MenuWeek(models.Model):
    """Represents a specific 'Drop' or ordering window."""
    name = models.CharField(max_length=100, help_text="e.g., 'Week of Oct 10'")
    start_date = models.DateField()
    is_active = models.BooleanField(default=False, help_text="The Kill Switch. Only one week should be active at a time.")
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status = "ARCHIVED" if self.is_archived else ("ACTIVE" if self.is_active else "CLOSED")
        return f"{self.name} ({status})"

class MenuItem(models.Model):
    """A specific meal being sold during a specific week."""
    menu_week = models.ForeignKey(MenuWeek, related_name='items', on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.PROTECT, null=True, blank=True)
    @property
    def projected_profit(self):
        # Math now works automatically between Money objects
        if not self.meal:
            return None
        if not self.meal.customer_price:
            return None
        return self.meal.customer_price - self.meal.calculate_cost()
    def __str__(self):
        if not self.meal:
            return "(Unassigned)"
        return f"{self.meal.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid'),
        ('FULFILLED', 'Fulfilled'),
    ]

    menu_week = models.ForeignKey(MenuWeek, related_name='orders', on_delete=models.PROTECT, null=True, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_chef': False},
    )
    customer_name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    total_price = MoneyField(max_digits=14, decimal_places=2, default=0, default_currency='USD')
    total_cost = MoneyField(max_digits=14, decimal_places=2, default=0, default_currency='USD')
    total_profit = MoneyField(max_digits=14, decimal_places=2, default=0, default_currency='USD')

    def save(self, *args, **kwargs):
        if self.customer and not self.customer_name:
            self.customer_name = self.customer.get_full_name() or self.customer.username
        super().save(*args, **kwargs)

    def update_totals(self, save=False):
        from djmoney.money import Money
        total_price = Money(0, 'USD')
        total_cost = Money(0, 'USD')
        for item in self.items.all():
            total_price += item.line_price
            total_cost += item.line_cost
        self.total_price = total_price
        self.total_cost = total_cost
        self.total_profit = total_price - total_cost
        if save:
            self.save(update_fields=['total_price', 'total_cost', 'total_profit'])

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    meal_name = models.CharField(max_length=200, blank=True)
    unit_price = MoneyField(max_digits=14, decimal_places=2, default=0, default_currency='USD')
    unit_cost = MoneyField(max_digits=14, decimal_places=2, default=0, default_currency='USD')
    line_price = MoneyField(max_digits=14, decimal_places=2, default=0, default_currency='USD')
    line_cost = MoneyField(max_digits=14, decimal_places=2, default=0, default_currency='USD')
    line_profit = MoneyField(max_digits=14, decimal_places=2, default=0, default_currency='USD')

    def refresh_prices(self):
        from djmoney.money import Money
        meal = self.menu_item.meal if self.menu_item else None
        if meal and meal.customer_price:
            self.unit_price = meal.customer_price
        else:
            self.unit_price = Money(0, 'USD')
        if meal:
            self.unit_cost = meal.calculate_cost()
        else:
            self.unit_cost = Money(0, 'USD')
        self.line_price = self.unit_price * self.quantity
        self.line_cost = self.unit_cost * self.quantity
        self.line_profit = self.line_price - self.line_cost
        if meal and not self.meal_name:
            self.meal_name = meal.name

    def save(self, *args, **kwargs):
        self.refresh_prices()
        super().save(*args, **kwargs)
        if self.order_id:
            self.order.update_totals(save=True)

    def __str__(self):
        if not self.menu_item.meal:
            return f"{self.quantity}x (Unassigned)"
        return f"{self.quantity}x {self.menu_item.meal.name}"