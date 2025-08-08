
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker
from accounts.models import User, JobSeekerProfile, EmployerProfile
from jobs.models import Skill, Industry, JobCategory, Job, JobApplication, SavedJob
from crm.models import MessageThread, Message, Notification, JobAlert

class Command(BaseCommand):
    help = 'Populates the database with an enhanced set of sample data for a manual demo.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))

        # Clean up existing data
        self.stdout.write('Cleaning up old data...')
        User.objects.all().delete()
        Job.objects.all().delete()
        JobCategory.objects.all().delete()
        Industry.objects.all().delete()
        Skill.objects.all().delete()
        MessageThread.objects.all().delete()

        fake = Faker()

        # Create Skills
        skills = [
            'Python', 'Django', 'JavaScript', 'React', 'Vue.js', 'Node.js', 
            'SQL', 'PostgreSQL', 'Docker', 'AWS', 'Project Management',
            'Agile Methodologies', 'Scrum', 'Data Analysis', 'Machine Learning',
            'Communication', 'Teamwork', 'Problem Solving', 'Leadership'
        ]
        skill_objects = [Skill.objects.create(name=skill) for skill in skills]
        self.stdout.write(self.style.SUCCESS(f'{len(skill_objects)} skills created.'))

        # Create Industries
        industries = [
            'Technology', 'Finance', 'Healthcare', 'Education', 'Marketing', 
            'Sales', 'Human Resources', 'Design', 'Engineering', 'Retail'
        ]
        industry_objects = [Industry.objects.create(name=industry) for industry in industries]
        self.stdout.write(self.style.SUCCESS(f'{len(industry_objects)} industries created.'))

        # Create Job Categories
        categories = [
            'Software Development', 'Data Science', 'Product Management',
            'UX/UI Design', 'Marketing & Sales', 'Business', 'Healthcare'
        ]
        category_objects = [JobCategory.objects.create(name=cat) for cat in categories]
        self.stdout.write(self.style.SUCCESS(f'{len(category_objects)} categories created.'))

        # --- Create Users ---

        # 1. Job Seeker
        job_seeker_user = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@example.com',
            password='password',
            user_type='jobseeker',
            first_name='John',
            last_name='Doe'
        )
        job_seeker_profile = JobSeekerProfile.objects.create(
            user=job_seeker_user,
            headline='Experienced Python Developer',
            bio=fake.paragraph(nb_sentences=5),
            years_of_experience=5,
            education=fake.sentence(nb_words=6),
            desired_position='Senior Software Engineer'
        )
        job_seeker_profile.skills.add(*random.sample(skill_objects, 7))
        self.stdout.write(self.style.SUCCESS('Job Seeker "jobseeker" created.'))
        
        # 2. Another Job Seeker
        job_seeker_user_2 = User.objects.create_user(
            username='jobseeker2',
            email='jobseeker2@example.com',
            password='password',
            user_type='jobseeker',
            first_name='Alice',
            last_name='Williams'
        )
        job_seeker_profile_2 = JobSeekerProfile.objects.create(
            user=job_seeker_user_2,
            headline='Data Scientist',
            bio=fake.paragraph(nb_sentences=5),
            years_of_experience=3,
        )
        job_seeker_profile_2.skills.add(*random.sample(skill_objects, 5))
        self.stdout.write(self.style.SUCCESS('Job Seeker "jobseeker2" created.'))
        
        
        # 3. Employer
        employer_user = User.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='password',
            user_type='employer',
            first_name='Jane',
            last_name='Smith'
        )
        employer_profile = EmployerProfile.objects.create(
            user=employer_user,
            company_name='Innovate Inc.',
            company_description=fake.paragraph(nb_sentences=5),
            industry='Technology',
            company_location='San Francisco, CA',
            company_website=fake.url()
        )
        self.stdout.write(self.style.SUCCESS('Employer "employer" created.'))
        
        # 4. Another Employer
        employer_user_2 = User.objects.create_user(
            username='employer2',
            email='employer2@example.com',
            password='password',
            user_type='employer',
            first_name='Bob',
            last_name='Johnson'
        )
        employer_profile_2 = EmployerProfile.objects.create(
            user=employer_user_2,
            company_name='Health Solutions',
            company_description=fake.paragraph(nb_sentences=5),
            industry='Healthcare',
            company_location='New York, NY',
            company_website=fake.url()
        )
        self.stdout.write(self.style.SUCCESS('Employer "employer2" created.'))

        # 5. Admin User
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password',
            user_type='admin',
            first_name='Admin',
            last_name='User'
        )
        self.stdout.write(self.style.SUCCESS('Admin "admin" created.'))

        # Create Jobs
        job_titles = [
            'Senior Python Developer', 'Frontend Engineer (React)', 'Data Scientist',
            'Product Manager', 'UX Designer', 'Digital Marketing Specialist',
            'Nurse Practitioner', 'Scrum Master'
        ]
        employers = [employer_profile, employer_profile_2]
        for title in job_titles:
            job = Job.objects.create(
                title=title,
                employer=random.choice(employers),
                category=random.choice(category_objects),
                job_type=random.choice(['full_time', 'part_time', 'contract']),
                experience_level=random.choice(['entry','mid', 'senior']),
                location=random.choice(['San Francisco, CA', 'New York, NY', 'Remote']),
                description=fake.paragraph(nb_sentences=10),
                responsibilities=fake.paragraph(nb_sentences=10),
                requirements=fake.paragraph(nb_sentences=10),
                application_deadline=timezone.now() + timezone.timedelta(days=random.randint(10, 60)),
                status='published'
            )
            job.industries.add(random.choice(industry_objects))
            job.skills_required.add(*random.sample(skill_objects, random.randint(3, 6)))
        self.stdout.write(self.style.SUCCESS(f'{len(job_titles)} jobs created.'))

        # Create Job Applications
        jobs_to_apply = Job.objects.filter(status='published').order_by('?')[:4]
        for job in jobs_to_apply:
            JobApplication.objects.create(
                job=job,
                applicant=job_seeker_profile,
                cover_letter=fake.paragraph(nb_sentences=3)
            )
        
        jobs_to_apply_2 = Job.objects.filter(status='published').order_by('?')[:3]
        for job in jobs_to_apply_2:
            JobApplication.objects.create(
                job=job,
                applicant=job_seeker_profile_2,
                cover_letter=fake.paragraph(nb_sentences=3)
            )
        self.stdout.write(self.style.SUCCESS(f'{len(jobs_to_apply) + len(jobs_to_apply_2)} job applications created.'))

        # Create Saved Jobs
        saved_job = Job.objects.exclude(applications__applicant=job_seeker_profile).first()
        if saved_job:
            SavedJob.objects.create(user=job_seeker_user, job=saved_job)
            self.stdout.write(self.style.SUCCESS('1 saved job created for jobseeker.'))
            
        saved_job_2 = Job.objects.exclude(applications__applicant=job_seeker_profile_2).first()
        if saved_job_2:
            SavedJob.objects.create(user=job_seeker_user_2, job=saved_job_2)
            self.stdout.write(self.style.SUCCESS('1 saved job created for jobseeker2.'))

        # Create CRM data: Message Thread and Messages
        thread = MessageThread.objects.create()
        thread.participants.add(job_seeker_user, employer_user)
        Message.objects.create(
            thread=thread,
            sender=job_seeker_user,
            recipient=employer_user,
            content="Hello, I'm very interested in the Senior Python Developer position."
        )
        Message.objects.create(
            thread=thread,
            sender=employer_user,
            recipient=job_seeker_user,
            content="Thanks for your interest, John. We've received your application and will review it shortly."
        )
        self.stdout.write(self.style.SUCCESS('1 message thread with 2 messages created.'))

        # Create Notifications
        Notification.objects.create(
            user=job_seeker_user,
            type='application',
            title='Application Received',
            message='Your application for Senior Python Developer has been received.'
        )
        Notification.objects.create(
            user=employer_user,
            type='message',
            title='New Message',
            message='You have a new message from John Doe.'
        )
        Notification.objects.create(
            user=job_seeker_user_2,
            type='job_alert',
            title='New Jobs Available',
            message='New jobs matching your "Data Science" alert are available.'
        )
        self.stdout.write(self.style.SUCCESS('3 notifications created.'))

        # Create Job Alert
        alert = JobAlert.objects.create(
            user=job_seeker_user,
            title='Python Job Alert',
            keywords='python, django',
            location='Remote',
            frequency='daily'
        )
        alert.categories.add(category_objects[0]) # Software Development
        
        alert2 = JobAlert.objects.create(
            user=job_seeker_user_2,
            title='Data Science Job Alert',
            keywords='data science, machine learning',
            location='New York',
            frequency='weekly'
        )
        alert2.categories.add(category_objects[1]) # Data Science
        self.stdout.write(self.style.SUCCESS('2 job alerts created.'))

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
