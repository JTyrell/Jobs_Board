# Architecture Context

## Tech Stack
| Layer            | Technology              | Role                                                           |
| ---------------- | ----------------------- | -------------------------------------------------------------- |
| **Framework**    | Django 4.2              | Main web framework (MVT architecture)                          |
| **UI**           | Bootstrap 5             | Frontend responsive styling & UI components                    |
| **Backend**      | Python 3                | Server-side logic, data models, ORM                            |
| **Database**     | PostgreSQL / SQLite     | Relational data storage (PostgreSQL for production)            |
| **Cache/Queue**  | Redis & Celery          | Background task processing, caching                            |
| **Hosting**      | Railway                 | Containerized PaaS deployment via Nixpacks                     |
| **Static Files** | Whitenoise              | Efficient static file serving in production                    |

## System Boundaries
- `accounts/` — User authentication, JobSeeker profiles, and Employer profiles.
- `jobs/` — Core job postings, categories, skills, and the job application lifecycle.
- `crm/` — Notifications, message threads, communications between users, and job alerts.
- `core/` — General pages, home page, static templates.
- `api/` — REST API endpoints built with Django Rest Framework.

## Storage Model
- **PostgreSQL**: Primary transactional database storing users, jobs, communications, and analytics.
- **Local/Cloud Media**: User-uploaded files (resumes, company logos, profile pictures). Usually an S3 bucket in production, falling back to local file system.

## Integration Model
- **Stripe**: Handles any potential payment workflows (subscriptions, premium job postings).
- **SendGrid**: Transactional emails for notifications, password resets, and alerts.
- **Celery/Redis**: Asynchronous workers for heavy tasks like bulk email sending or resume parsing.

## Critical Invariants
1. **User Types**: A User must be distinctly identifiable as either a `jobseeker`, `employer`, or `admin`.
2. **Access Control**: Employers cannot apply to jobs; Job Seekers cannot post jobs.
3. **Data Integrity**: Job applications are inherently tied to both a `Job` and a `JobSeekerProfile`. Deleting a job cascade deletes applications.
