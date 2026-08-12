# UI Context

## Design System
- **Framework**: Bootstrap 5
- **Forms**: `django-crispy-forms` integrated with `crispy-bootstrap5`
- **Methodology**: Mobile-first responsive design.

## Layout Structure
- **Base Template (`base.html`)**: Contains the global navigation bar, footer, and includes necessary Bootstrap CDN links or local static assets.
- **App Templates**: Each Django app has its dedicated folder in `templates/` (e.g., `templates/jobs/`, `templates/accounts/`).

## Styling Guidelines
1. **Utility First**: Use Bootstrap's native utility classes (spacing, flex, colors, typography) before writing custom CSS.
2. **Crispy Forms**: All forms must utilize `{% crispy form %}` to automatically render with Bootstrap styling, error states, and help texts.
3. **Accessibility**: Ensure all interactive elements have appropriate ARIA labels and color contrasts meet WCAG standards.
4. **JavaScript**: Keep inline scripts to a minimum. Use external scripts for complex UI interactions, but rely on Bootstrap's native JS components (modals, dropdowns) when possible.

## Key Views
- **Home Page**: Search bar front and center, featured jobs, and clear call-to-action buttons for registration.
- **Job Detail**: Clear hierarchy of job title, employer, salary, and a prominent "Apply Now" button.
- **Dashboards**: Tabular layouts or card grids for managing applications and posted jobs, prioritizing scannability and quick actions.
