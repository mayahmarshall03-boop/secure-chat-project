Mariyah Marshall Senior Project

**Week 1 - Project Initialization**
- Selected project topic: Secure Encrypted Chat Application.
- Wrote and submitted the initial project proposal outlining goals, architecture, and planned technologies.
- Created the initial project folder structure (backend, frontend, docs, tests).
- Installed required development tools (Python 3, VS Code, SQLite tools).
- Began reviewing Flask documentation and encryption concepts (AES, RSA, hashing).

**Week 2 — Backend Planning and Architecture**
- Created the backend/routes/ folder to organize route files.
- Added empty placeholder files (auth_routes.py, message_routes.py) to prepare for modular routing.
- Began planning how authentication and messaging would be separated into Blueprints.

**Week 3 — Environment Setup and Flask Initialization**
- Created and activated a Python virtual environment (venv).
- Installed Flask and Flask‑CORS inside the virtual environment.
- Created app.py and initialized the Flask application instance.
- Set up CORS to allow communication with the future frontend.
- Registered route Blueprints in app.py to prepare for modular routing.
- Added placeholder route functions in both route files to confirm the structure works.

**Week 4 — Debugging and Server Launch**
- Resolved import errors caused by missing Blueprint definitions.
- Implemented working Blueprint objects (auth_bp, messages_bp) in their respective files.
- Launched the Flask development server successfully at http://127.0.0.1:5000.
- Verified that all placeholder endpoints return JSON responses.
- Fixed VS Code interpreter issues by pointing it to the correct virtual environment path.
- Confirmed that Flask imports and linting warnings were resolved.

**Week 5**