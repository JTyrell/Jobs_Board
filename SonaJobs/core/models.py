from django.db import models
from django.urls import reverse

class Page(models.Model):
    """Content pages that can be managed through the admin interface"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    meta_description = models.CharField(max_length=160, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('core:page_detail', kwargs={'slug': self.slug})


class Testimonial(models.Model):
    """Testimonials from users that can be displayed on the site"""
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    quote = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class FAQ(models.Model):
    """Frequently asked questions"""
    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('jobseekers', 'For Job Seekers'),
        ('employers', 'For Employers'),
        ('technical', 'Technical'),
    )
    
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='general')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'question']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    """Contact form submissions"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.subject} from {self.name}"