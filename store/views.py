from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.contrib import messages
from django.utils import timezone
from .models import MenuWeek, MenuItem, Order, OrderItem
from .forms import MenuItemForm, MenuWeekForm

def home(request):
    """
    Landing Page: Shows the currently active MenuWeek.
    """
    # Fetch the currently active week (The Drop)
    active_week = MenuWeek.objects.filter(is_active=True, is_archived=False).first()
    
    context = {
        'active_week': active_week,
        # If no week is active, items will be None, template handles "Closed" state
        'items': active_week.items.select_related('meal').filter(meal__isnull=False) if active_week else None
    }
    return render(request, 'store/home.html', context)

@login_required
def checkout(request):
    """
    Processes the order submission.
    Expects POST data in format: item_<menu_item_id> = quantity
    """
    if request.method == 'POST':
        active_week = MenuWeek.objects.filter(is_active=True).first()
        if not active_week:
            messages.error(request, "Ordering is currently closed.")
            return redirect('home')

        # 1. Create the Order shell
        order = Order.objects.create(
            customer=request.user,
            status='PENDING' # Default status
        )
        
        has_items = False
        
        # 2. Loop through POST data to find items
        for key, value in request.POST.items():
            if key.startswith('item_'):
                try:
                    item_id = int(key.split('_')[1])
                    quantity = int(value)
                    
                    if quantity > 0:
                        menu_item = get_object_or_404(MenuItem, id=item_id)
                        # Verify item belongs to active week to prevent tampering
                        if menu_item.menu_week == active_week:
                            OrderItem.objects.create(
                                order=order,
                                menu_item=menu_item,
                                quantity=quantity
                            )
                            has_items = True
                except ValueError:
                    continue

        if has_items:
            messages.success(request, "Order placed successfully! Please pay below.")
            return redirect('profile') # Redirect to profile to see the order/pay
        else:
            order.delete() # Cleanup empty order
            messages.warning(request, "Your cart was empty.")
            return redirect('home')

    return redirect('home')

@login_required
def profile(request):
    """
    User Dashboard: Shows past and current orders.
    """
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {'orders': orders})

@staff_member_required
def batch_fulfillment_report(request):
    """
    Chef's View: Aggregates ingredients for the ACTIVE week's PAID orders.
    """
    active_week = MenuWeek.objects.filter(is_active=True, is_archived=False).first()
    grocery_list = {}

    if active_week:
        # Get all PAID orders for the active week
        # We traverse: Order -> OrderItems -> MenuItem -> MenuWeek
        paid_orders = Order.objects.filter(
            status='PAID',
            items__menu_item__menu_week=active_week
        ).distinct()

        for order in paid_orders:
            for item in order.items.select_related('menu_item__meal'):
                meal = item.menu_item.meal
                if not meal:
                    continue
                # For each meal ordered, aggregate recipe ingredients
                for mr in meal.meal_recipes.all():
                    recipe_ingredients = mr.recipe.recipe_ingredients.all()
                    for ri in recipe_ingredients:
                        resolved = ri.resolved_ingredient
                        ingredient_name = resolved.name if resolved else ri.ingredient_name
                        ingredient_unit = resolved.unit_display if resolved else (ri.ingredient_unit.name if ri.ingredient_unit else '')
                        if not ingredient_name:
                            continue
                        # Total needed = (Amount per recipe * meal recipe qty * order item qty)
                        total_needed = ri.quantity * mr.quantity * item.quantity

                        if ingredient_name in grocery_list:
                            grocery_list[ingredient_name]['qty'] += total_needed
                        else:
                            grocery_list[ingredient_name] = {
                                'qty': total_needed,
                                'unit': ingredient_unit
                            }

    return render(request, 'store/report.html', {
        'grocery_list': grocery_list,
        'active_week': active_week
    })
    
@staff_member_required
def add_menu_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            menu_item = form.save(commit=False)
            if not menu_item.menu_week:
                menu_item.menu_week = MenuWeek.objects.filter(is_archived=False).order_by('-is_active', '-start_date').first()
            if menu_item.menu_week:
                menu_item.save()
    return redirect('chef_dashboard')

@staff_member_required
def create_menu_week(request):
    if request.method == 'POST':
        form = MenuWeekForm(request.POST)
        if form.is_valid():
            week = form.save(commit=False)
            week.is_archived = False
            if week.is_active:
                MenuWeek.objects.filter(is_active=True, is_archived=False).update(is_active=False)
            week.save()
    return redirect('chef_dashboard')

@staff_member_required
def edit_menu_item(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=menu_item, prefix='menu-edit')
        if form.is_valid():
            updated_item = form.save(commit=False)
            if not updated_item.menu_week:
                updated_item.menu_week = menu_item.menu_week
            updated_item.save()
    return redirect('chef_dashboard')

@staff_member_required
def delete_menu_item(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    menu_item.delete()
    return redirect('chef_dashboard')

@staff_member_required
def archive_menu_week(request, week_id):
    week = get_object_or_404(MenuWeek, id=week_id)
    if request.method == 'POST':
        week.is_active = False
        week.is_archived = True
        week.archived_at = timezone.now()
        week.save(update_fields=['is_active', 'is_archived', 'archived_at'])
    return redirect('chef_dashboard')