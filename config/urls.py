"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import signup
from store.views import home, checkout, profile, batch_fulfillment_report
from inventory.views import chef_dashboard, add_ingredient, manage_recipe, delete_recipe, manage_meal, delete_meal
from store.views import add_menu_item
from inventory.views import chef_dashboard, add_ingredient, manage_recipe, delete_recipe, manage_meal, delete_meal
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('checkout/', checkout, name='checkout'),
    path('profile/', profile, name='profile'),
    path('report/current/', batch_fulfillment_report, name='fulfillment_report'),
    
    # Auth Routes
    path('signup/', signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')), # Handles /login/ and /logout/
    path('chef/', chef_dashboard, name='chef_dashboard'),
    path('chef/ingredient/add/', add_ingredient, name='add_ingredient'),
    path('chef/recipe/add/', manage_recipe, name='add_recipe'),
    path('chef/recipe/edit/<int:recipe_id>/', manage_recipe, name='edit_recipe'),
    path('chef/recipe/delete/<int:recipe_id>/', delete_recipe, name='delete_recipe'),
    path('chef/meal/add/', manage_meal, name='add_meal'),
    path('chef/meal/edit/<int:meal_id>/', manage_meal, name='edit_meal'),
    path('chef/meal/delete/<int:meal_id>/', delete_meal, name='delete_meal'),
    path('chef/menu/add/', add_menu_item, name='add_menu_item'),
]
