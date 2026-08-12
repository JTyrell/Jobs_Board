# Job Board Domain Specification

## Ground Truth Definitions
- **Job Seeker**: A user seeking employment. Can view jobs, save jobs, set up job alerts, and apply for jobs.
- **Employer**: A user representing a company. Can post jobs, review applications, and communicate with applicants.
- **Job Posting**: A position available for application, containing metadata like salary, experience level, remote options, and required skills.
- **Application**: The record of a Job Seeker expressing interest in a Job Posting, including status tracking (pending, accepted, rejected).

## Feature Engineering Specs
- **Resume Processing**: The system features resume parsing (potentially using `pdfplumber`, `spacy`, `scikit-learn` based on dependencies) to extract skills and match them against job requirements.
- **Job Matching**: Algorithms or queries that connect a Job Seeker's skills and desired position to relevant Job Postings.

## Evaluation Metrics
- **User Engagement**: Active daily job seekers, number of applications submitted per day.
- **Employer Success**: Time-to-hire, number of relevant applications per job posting.
- **Platform Health**: Platform uptime, background task success rate (Celery), and email delivery rates.

## Constraints & Requirements
- **Data Privacy**: Resumes and private messages between users must be secure. Job alerts must respect user frequency preferences.
- **Scalability**: The platform must handle spikes in traffic without degrading database performance.
- **Role Isolation**: Ensure strict permission boundaries between employers and job seekers at the view and API levels.
