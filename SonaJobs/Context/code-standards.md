# Code Standards

## Python & Django
- Adhere to PEP 8 styling conventions.
- Use meaningful variable names and document complex logic with docstrings.
- Utilize Pylint and Bandit for static analysis and security linting (`pylint --rcfile=.pylintrc .`).
- Keep models "fat" and views "skinny". Business logic should primarily reside in models or dedicated service layers, not in the view layer.
- Use Django's ORM efficiently; avoid N+1 query problems by using `select_related()` and `prefetch_related()`.

## HTML & Templates
- Extend `base.html` for all user-facing views to maintain consistent navigation and footer.
- Use Django template tags efficiently.
- Structure templates mirroring the app structure (e.g., `templates/accounts/`, `templates/jobs/`).
- Forms must be rendered using crispy forms `{% crispy form %}`.

## Static & Assets
- Use organized subdirectories within the `static/` folder (e.g., `css/`, `js/`, `img/`).
- Write custom CSS only when Bootstrap 5 utility classes are insufficient.
- Minimize JavaScript logic embedded directly in HTML; use external `.js` files when possible.

## Testing
- Write test cases for all major models, views, and forms using Django's built-in `TestCase`.
- Aim for high test coverage on critical paths like user authentication and job application flows.
