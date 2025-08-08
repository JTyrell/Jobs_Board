from django.db import models
from django.contrib.auth import get_user_model
from jobs.models import Job, JobApplication

User = get_user_model()


class ResumeAnalysis(models.Model):
    """Model to store resume analysis results"""
    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='resume_analysis')
    raw_text = models.TextField(help_text="Extracted text from resume")
    processed_at = models.DateTimeField(auto_now_add=True)
    confidence_score = models.FloatField(default=0.0, help_text="Overall confidence in extraction")
    
    class Meta:
        verbose_name = "Resume Analysis"
        verbose_name_plural = "Resume Analyses"
    
    def __str__(self):
        return f"Analysis for {self.application.applicant.get_full_name()} - {self.application.job.title}"


class ExtractedSkill(models.Model):
    """Model to store extracted skills from resumes"""
    analysis = models.ForeignKey(ResumeAnalysis, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=100)
    confidence = models.FloatField(default=0.0)
    source_text = models.TextField(help_text="Original text where skill was found")
    
    class Meta:
        unique_together = ['analysis', 'skill_name']
    
    def __str__(self):
        return f"{self.skill_name} ({self.confidence:.2f})"


class ExtractedExperience(models.Model):
    """Model to store extracted work experience"""
    analysis = models.ForeignKey(ResumeAnalysis, on_delete=models.CASCADE, related_name='experiences')
    company_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    duration = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    confidence = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"{self.position} at {self.company_name}"


class ExtractedEducation(models.Model):
    """Model to store extracted education information"""
    analysis = models.ForeignKey(ResumeAnalysis, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    confidence = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"{self.degree} from {self.institution}"


class ResumeMatchScore(models.Model):
    """Model to store job-resume matching scores"""
    analysis = models.ForeignKey(ResumeAnalysis, on_delete=models.CASCADE, related_name='match_scores')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    overall_score = models.FloatField(help_text="Overall match percentage")
    skills_match = models.FloatField(default=0.0)
    experience_match = models.FloatField(default=0.0)
    education_match = models.FloatField(default=0.0)
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['analysis', 'job']
    
    def __str__(self):
        return f"{self.overall_score:.1f}% match for {self.job.title}" 