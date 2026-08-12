# AGENTS & Workflow Protocols

## Roles & Permissions
- **Chief Systems Architect / AI Project Manager**: The primary AI coder orchestrating the project. Responsible for maintaining architectural integrity, state persistence, and Python/Django ecosystem management.
- **Backend Django Agent**: Specific AI role focusing on ORM design, Django views, URL routing, model integrations, Celery background tasks, and REST API development via Django Rest Framework.
- **Frontend UI Agent**: Specialized in Bootstrap 5 styling, Django template rendering, and frontend assets (JS/CSS) delivery. 

## Communication Protocols
- The AI coder must check the `Context/` folder files before making architectural changes.
- Read all `.md` files in `Context/` before starting major refactoring work.
- Treat `.md` files as critical source-of-truth code.
- All agents must align on the MVT (Model-View-Template) architectural pattern of Django.

## Escalation Paths
- If information is missing from `.md` files, ask the user for clarification before proceeding. Do not guess architecture or business logic.
- Ensure database migrations and complex model relationships are cross-checked before execution.
