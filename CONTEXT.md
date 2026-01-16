# Project Context: CiCi's Pre-Order Platform (CFP)

## Project Overview
A weekly "drop-style" food ordering platform where a Chef controls the menu and views automated cost breakdowns.
**Tech Stack:** Django (Backend), Vanilla JS/CSS (Frontend), PostgreSQL (DB).

## Core Terminology
- **The Drop:** The active ordering window (usually weekly).
- **Batch Report:** The aggregated grocery list of all ingredients needed for accepted orders.
- **Kill Switch:** A global boolean that immediately disables frontend ordering.

## Architecture & Naming Conventions
**Root Configuration Directory:** `config/` (Standard Django layout)
**Python Version:** 3.10+
**Environment Management:** `python-dotenv`

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
    * `is_active` (Boolean) - The "Kill Switch" per week.
* **Model:** `MenuItem`
    * `menu_week` (FK -> MenuWeek)
    * `recipe` (FK -> inventory.Recipe)
    * `selling_price` (Decimal)
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
- All views modifying data must require `@login_required` or correct permissions.