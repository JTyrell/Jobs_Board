# AI Workflow Rules

## 1. Initial State Check
Before writing any code or modifying configuration, agents MUST:
- Check this `Context/` folder for architectural guidelines.
- Review existing models in `accounts`, `jobs`, and `crm` apps.
- Verify environment variables layout in `env.example`.

## 2. Django Specific Constraints
- All database changes MUST be followed by `python manage.py makemigrations` and `python manage.py migrate`.
- Views should prefer Class-Based Views (CBV) where appropriate unless function-based views provide a simpler mechanism for the specific endpoint.
- All forms should utilize `django-crispy-forms` with the `crispy-bootstrap5` pack for consistent UI rendering.

## 3. Deployment Constraints
- Be aware of the `railway.json` for deployment commands.
- Ensure static files are managed using `whitenoise` in production.
- Do not commit `.env` or sensitive API keys. Use `python-decouple` config settings.

## 4. UI/UX Rules
- Strictly use Bootstrap 5 utility classes.
- Ensure all pages are responsive (mobile-first approach).
- Maintain consistent branding and layout via base templates.
