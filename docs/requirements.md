## Sprint 1 — Functional Requirements

### Vision
Provide a lightweight web-based inventory management system that lets small operations track products, suppliers, and stock movements in real time using a Flask backend with a MySQL database and Bootstrap UI.

### Personas & Goals
- **Inventory Manager**: Maintains product catalog, monitors stock levels, receives replenishment alerts.
- **Warehouse Staff**: Records stock in/out transactions quickly from desktop or tablet.
- **Business Owner**: Reviews dashboards for valuation, movement trends, and outstanding orders.

### Core User Stories
1. As an Inventory Manager, I can create, update, archive, and search products with assigned categories and suppliers.
2. As Warehouse Staff, I can log stock receipts (inbound) and shipments (outbound) to keep the on-hand quantity accurate.
3. As the Business Owner, I can view low-stock alerts and recent movement history from a dashboard.
4. As any user, I require secure authentication with role-based access (planned for Sprint 4).

### Non-Functional Requirements
- Accessible via modern browsers, responsive layouts via Bootstrap 5.
- Auditability: every stock movement stores actor, timestamp, quantity delta, and optional notes.
- Configurable thresholds for low-stock alerts per product.
- Deployment-ready configuration via `.env` file (database credentials, secret key, etc.).

### Sprint 1 Deliverables
1. Documented requirements (this file).
2. Flask project skeleton with configuration placeholders.
3. Draft MySQL schema covering products, suppliers, categories, stock movements, and users.
4. UI layout strategy referencing Bootstrap components.

