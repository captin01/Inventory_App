## Inventory Management System

Sprint 1 establishes the foundation of a Flask + MySQL web app for tracking inventory.

### Quick Start
1. Create and activate a virtual environment (example using PowerShell):
   ```
   py -3 -m venv .venv
   .\.venv\Scripts\activate
   ```
2. Install dependencies (list to be finalized in Sprint 2):
   ```
   pip install flask python-dotenv mysqlclient mysql-connector-python
   ```
3. Set environment variables:
   ```
   set FLASK_APP=app
   set FLASK_ENV=development
   ```
4. Run the development server:
   ```
   flask run
   ```

### Repository Layout
- `app/`: Flask application package (created in Sprint 1).
- `docs/`: Requirements, schema, and UI plans.
- `python_test.ipynb`: Existing notebook verifying MySQL connectivity.

Subsequent sprints will add blueprints, services, and front-end components.

