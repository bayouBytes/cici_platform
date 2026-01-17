from django.db import models
from django.conf import settings  # To reference users.User
from inventory.models import Recipe
from djmoney.models.fields import MoneyField
class MenuWeek(models.Model):
    """Represents a specific 'Drop' or ordering window."""
    name = models.CharField(max_length=100, help_text="e.g., 'Week of Oct 10'")
    start_date = models.DateField()
    is_active = models.BooleanField(default=False, help_text="The Kill Switch. Only one week should be active at a time.")

    def __str__(self):
        status = "ACTIVE" if self.is_active else "CLOSED"
        return f"{self.name} ({status})"

class MenuItem(models.Model):
    """A specific recipe being sold during a specific week."""
    menu_week = models.ForeignKey(MenuWeek, related_name='items', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT) # Protect prevents deleting recipe if sold
    selling_price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    @property
    def projected_profit(self):
        # Math now works automatically between Money objects
        return self.selling_price - self.recipe.calculate_cost()
    def __str__(self):
        return f"{self.recipe.name} (${self.selling_price})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid'),
        ('FULFILLED', 'Fulfilled'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.recipe.name}"