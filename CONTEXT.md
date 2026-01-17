# Project Context: CiCi's Pre-Order Platform (CFP)

## Project Overview
A weekly "drop-style" food ordering platform where a Chef controls the menu and views automated cost breakdowns.
**Tech Stack:** Django (Backend), Vanilla JS (Frontend Logic), Tailwind CSS + FontAwesome (Styling), SQLite (Dev DB).

## Core Terminology
- **The Drop:** The active ordering window (usually weekly).
- **Batch Report:** The aggregated grocery list of all ingredients needed for accepted orders.
- **Kill Switch:** A `MenuWeek` boolean (`is_active`) that toggles the frontend ordering availability.

## Architecture & Naming Conventions
**Root Configuration Directory:** `config/` (Standard Django layout)
**Python Version:** 3.10+
**Environment Management:** `python-dotenv`
**Static Files:** `static/css` (Global overrides), `static/img` (Assets).
**Templates:** `templates/` (Global root), subdivided by app (`inventory/`, `store/`).

## App Structure & Models

### 1. App: `users` (Handles Auth)
* **Model:** `User`
    * Inherits from: `AbstractUser`
    * Key Fields: `is_chef` (Boolean) - distinguishes Admin/Chef from customers.
    * *Note: Using a custom user model is a Django strict requirement for future-proofing.*

### 2. App: `inventory` (The "Chef's Brain")
* **Model:** `Ingredient`
    * `name` (Char)
    * `unit_type` (Choice: 'LB', 'OZ', 'G', 'QTY')
    * `cost_per_unit` (Decimal: max_digits=6, decimal_places=2)
* **Model:** `Recipe`
    * `name` (Char)
    * `instructions` (Text)
    * *Method:* `calculate_cost()` -> Sums all related ingredient costs.
* **Model:** `RecipeIngredient` (Through Table)
    * `recipe` (FK -> Recipe)
    * `ingredient` (FK -> Ingredient)
    * `quantity` (Decimal)

### 3. App: `store` (The Customer Facing Store)
* **Model:** `MenuWeek`
    * `start_date` (Date)
    * `is_active` (Boolean) - The "Kill Switch" per week. Only one week should be active at a time.
* **Model:** `MenuItem`
    * `menu_week` (FK -> MenuWeek)
    * `recipe` (FK -> inventory.Recipe)
    * `selling_price` (Decimal)
    * *Property:* `projected_profit` -> (Selling Price - Recipe Cost).
* **Model:** `Order`
    * `customer` (FK -> users.User)
    * `created_at` (DateTime)
    * `status` (Choice: 'PENDING', 'PAID', 'FULFILLED')
* **Model:** `OrderItem`
    * `order` (FK -> Order)
    * `menu_item` (FK -> MenuItem)
    * `quantity` (Int)

## Security Guidelines
- NEVER commit `.env` files.
- `DEBUG` must be `False` in production.
- All views modifying data must require `@login_required`, and Chef views must require `is_staff` or `@staff_member_required`.

## Key Routes & Views Specification

### Public Storefront
* `GET /`: Landing page. Shows the active `MenuWeek` items. Redirects or shows "Closed" banner if no week is active.
* `POST /checkout/`: Handles the order submission. Creates `Order` and `OrderItem` records.
* `GET /profile/`: User Dashboard. Lists past orders and status (Pending/Paid).

### Auth System
* `GET /signup/`: Custom registration view.
* `GET /accounts/login/`: Standard Django auth (redirects to Home).

### Chef/Admin Dashboard (Staff Only)
* `GET /chef/`: **The Chef Dashboard.** Main hub for managing inventory and the active drop.
    * *Features:* Modal popups for adding Ingredients and Menu Items.
* `GET /chef/recipe/add/`: **Recipe Editor.** dedicated page for creating recipes with multiple ingredient rows (Formsets).
* `GET /report/current/`: **Batch Fulfillment Report.** Aggregates ingredients for the current active week's PAID orders.

## Frontend & Styling Specifications

### Design System
* **Framework:** Tailwind CSS (CDN) + FontAwesome (CDN).
* **Colors:**
    * **Brand Dark:** `#071B26` (Text, Nav, Headers)
    * **Brand Teal:** `#58A7A6` (Buttons, Accents, Links)
    * **Brand Light:** `#F5FDFE` (Backgrounds, Cards)
* **Global CSS:** `static/css/styles.css` handles form input normalization to match Tailwind styles.

### Template Architecture
* **Base Template (`base.html`):**
    * Contains Tailwind CDN config with Brand Colors.
    * Navigation Bar: Dynamic links based on `user.is_authenticated` and `user.is_staff`.
    * Messages Block: Styled alerts for success/error notifications.
* **Chef Dashboard (`inventory/dashboard.html`):**
    * Uses HTML5 `<dialog>` elements for "Add Ingredient" and "Add to Menu" modals.
    * Displays 3 Panels: Ingredients, Recipes, and Active Menu.
* **Recipe Editor (`inventory/recipe_editor.html`):**
    * Uses Django Formsets to allow dynamic adding/removing of ingredient rows.

## User Flows (Walkthroughs)

### 1. The Chef Setup (Admin Side)
1.  **Login:** Access `/admin/` or `/chef/`.
2.  **Stock Pantry:** Click "+ Add New" on Ingredients panel.
3.  **Create Dish:** Click "+ Build Recipe". Name the dish, add ingredient rows, save.
4.  **Launch Drop:** Ensure a `MenuWeek` is active (via Admin or future dashboard toggle).
5.  **Price & List:** On Dashboard, click "+ Add Dish to Drop". Select Recipe, set Price, Save.

### 2. The Customer Loop
1.  **Browse:** Visit Home (`/`). If Active, see Menu Grid.
2.  **Select:** Input quantities for desired dishes.
3.  **Order:** Click "Place Order" -> Redirects to Profile.
4.  **Track:** View Order Status (PENDING). (Payment flow to be added).