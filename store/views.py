from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.contrib import messages
from .models import MenuWeek, MenuItem, Order, OrderItem
from .forms import MenuItemForm

def home(request):
    """
    Landing Page: Shows the currently active MenuWeek.
    """
    # Fetch the currently active week (The Drop)
    active_week = MenuWeek.objects.filter(is_active=True).first()
    
    context = {
        'active_week': active_week,
        # If no week is active, items will be None, template handles "Closed" state
        'items': active_week.items.all() if active_week else None
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
    active_week = MenuWeek.objects.filter(is_active=True).first()
    grocery_list = {}

    if active_week:
        # Get all PAID orders for the active week
        # We traverse: Order -> OrderItems -> MenuItem -> MenuWeek
        paid_orders = Order.objects.filter(
            status='PAID',
            items__menu_item__menu_week=active_week
        ).distinct()

        for order in paid_orders:
            for item in order.items.all():
                # For each plate ordered, how much of each ingredient is needed?
                # Navigate: OrderItem -> MenuItem -> Recipe -> RecipeIngredient
                recipe_ingredients = item.menu_item.recipe.recipe_ingredients.all()
                
                for ri in recipe_ingredients:
                    ingredient_name = ri.ingredient.name
                    # Total needed = (Amount per recipe * OrderItem Qty)
                    total_needed = ri.quantity * item.quantity

                    if ingredient_name in grocery_list:
                        grocery_list[ingredient_name]['qty'] += total_needed
                    else:
                        grocery_list[ingredient_name] = {
                            'qty': total_needed,
                            'unit': ri.ingredient.unit_display
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
            form.save()
    return redirect('chef_dashboard')