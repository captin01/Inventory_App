## UI Layout & Bootstrap Components

### Navigation
- Top navbar (Bootstrap `navbar-expand-lg`) with brand logo, links to Dashboard, Products, Suppliers, Stock Movements, Reports.
- Right-aligned user menu with avatar + dropdown for profile/logout (placeholder until auth delivered).

### Dashboard
- Two-column responsive layout using Bootstrap grid.
- Cards (`.card`) summarizing total SKUs, stock valuation, low-stock count, recent movements.
- Table listing last 10 movements with badges for inbound/outbound status.

### Product Management
- Products list: `table.table-striped` with responsive wrapper; column filters via input group.
- Action buttons (`btn-sm`) for edit/view/archive.
- Modal form for quick add; dedicated page for full CRUD using Bootstrap form controls.

### Stock Movements
- Form split into Product Selector (`select2` style planned) and movement details (quantity, type, reference).
- Timeline component using stacked list group items to show history; color-coded icons.

### General Style Guide
- Base layout extends `templates/base.html` (Sprint 1 deliverable) with Bootstrap 5 CDN plus custom `static/css/main.css`.
- Utility classes: `text-muted` for metadata, `badge bg-success/bg-danger` for movement types.
- Use `container-fluid` for primary pages to support widescreen warehouse displays.

### Accessibility & Responsiveness
- Ensure form labels and aria attributes are present.
- Breakpoints tested for tablets (md) and phones (sm) to support floor operations.

