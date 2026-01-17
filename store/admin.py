from django.contrib import admin
from .models import MenuWeek, MenuItem, Order, OrderItem

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1

@admin.register(MenuWeek)
class MenuWeekAdmin(admin.ModelAdmin):
    inlines = [MenuItemInline]
    list_display = ('name', 'start_date', 'is_active')
    list_editable = ('is_active',) # Quick toggle from the list view

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'customer', 'status', 'created_at')
    list_filter = ('status', 'created_at')