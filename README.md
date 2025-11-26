## Inventory Management System (Flask)

This repository contains a **web application for managing inventory** in a small‑to‑medium business.  
It is built with **Flask** on the backend, a relational database (MySQL or SQLite), and HTML templates for the UI.

Think of it as a simple internal tool that lets you:

- Keep a list of all your products.
- See how much stock you currently have.
- Record when stock comes in and goes out.
- Give admins a dashboard to manage everything in one place.

> 💡 **Where to look first as a reader:**  
> - Open `app/templates/landing.html` to see the main landing page.  
> - Open `app/routes/` to see how different pages are wired.  

The code that matters for this app is under the `Inv_project/` folder.

---

### Visual Overview (Screenshots)

You can use this section to show how the app looks and flows.  
Replace the comments below with real images once you have them.

<!-- TODO: Add a full-page screenshot of the landing/dashboard view -->
<!-- Example: ![Landing Page](docs/images/landing.png) -->


<!-- TODO: Add a screenshot of the product list page -->
<!-- Example: ![Product List](docs/images/product-list.png) -->

<!-- TODO: Add a screenshot or GIF showing creating/updating a product -->
<!-- Example: ![Create Product Flow](docs/images/create-product.gif) -->

<!-- TODO: Add a screenshot of an inventory/stock movement screen -->
<!-- Example: ![Stock Movement](docs/images/stock-movement.png) -->

---

### What the App Can Do (Features)

- **Product & Category Management**
  - Create, edit, view, and delete products.
  - Associate products with categories / groups (e.g. by type, brand, or location).
  - Store key attributes such as SKU, name, description, pricing, and stock thresholds.

- **Inventory & Stock Tracking**
  - Track current stock levels for each product.
  - Support for stock adjustments (stock‑in / stock‑out operations).
  - Highlight low‑stock items (below minimum threshold).

- **Transactions / Movements**
  - Log inventory movements (purchases, sales, returns, adjustments).
  - Keep a basic audit trail of when quantities changed and by how much.

- **User & Admin Experience**
  - Admin dashboard views for an overview of inventory health.
  - Authentication / admin‑only operations (e.g. managing products, categories, users).  
    *(Exact behavior depends on your current `routes` and `models`.)*

- **Clean UI**
  - Uses HTML templates in `app/templates/` (including `landing.html`) for a cohesive UI.
  - Styles are defined in `app/static/` so you can customize branding and layout.

---

### Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL or SQLite (depending on your configuration in `config.py` / `db_setup.py`)
- **ORM / DB Layer**: SQLAlchemy‑style models in `app/models/`
- **Frontend**: Jinja2 templates + CSS

---

### Project Structure (Inventory App)

Inside `Inv_project/`:

- `app/`
  - `config.py` – application configuration (database, secrets, debug flags, etc.).
  - `db_setup.py` / `db.py` – database initialization and connection helpers.
  - `models/` – database models for products, categories, inventory movements, users, etc.
  - `routes/` – Flask blueprints / route handlers for different sections of the app.
  - `templates/` – Jinja2 templates (HTML), including `landing.html` and other pages.
  - `static/` – static assets (CSS, images, JS if any).
- `app.py` – main Flask entry point (creates the app and wires routes/models).
- `docs/` – project documentation:
  - `requirements.md` – high‑level functional requirements.
  - `schema.md` – database schema and relationships.
  - `ui_plan.md` – screens, flows, and UI notes.
- `scripts/`
  - `create_admin.py` – helper script for creating an initial admin user (if implemented).
- `requirements.txt` – Python dependencies for this inventory app.

---

