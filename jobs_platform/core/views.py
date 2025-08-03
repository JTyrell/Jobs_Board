from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Page, FAQ, Testimonial, ContactMessage
from .forms import ContactForm
from jobs.models import Job, JobCategory, Industry

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_jobs'] = Job.objects.filter(status='published').order_by('-created_at')[:8]
        context['job_categories'] = JobCategory.objects.all()[:10]
        context['testimonials'] = Testimonial.objects.filter(is_active=True)[:4]
        return context


class AboutView(TemplateView):
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['about_page'] = Page.objects.get(slug='about')
        except Page.DoesNotExist:
            context['about_page'] = None
        context['testimonials'] = Testimonial.objects.filter(is_active=True)
        return context


class ContactView(CreateView):
    template_name = 'core/contact.html'
    model = ContactMessage
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['contact_page'] = Page.objects.get(slug='contact')
        except Page.DoesNotExist:
            context['contact_page'] = None
        return context
    
    def form_valid(self, form):
        # Save the IP address
        form.instance.ip_address = self.request.META.get('REMOTE_ADDR')
        messages.success(self.request, 'Thank you for your message. We will get back to you shortly.')
        return super().form_valid(form)


class FAQView(ListView):
    template_name = 'core/faq.html'
    model = FAQ
    context_object_name = 'faqs'
    
    def get_queryset(self):
        return FAQ.objects.filter(is_active=True).order_by('category', 'order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group FAQs by category
        context['faq_categories'] = {
            'general': self.get_queryset().filter(category='general'),
            'jobseekers': self.get_queryset().filter(category='jobseekers'),
            'employers': self.get_queryset().filter(category='employers'),
            'technical': self.get_queryset().filter(category='technical'),
        }
        try:
            context['faq_page'] = Page.objects.get(slug='faq')
        except Page.DoesNotExist:
            context['faq_page'] = None
        return context


class PageDetailView(DetailView):
    model = Page
    template_name = 'core/page_detail.html'
    context_object_name = 'page'
    
    def get_queryset(self):
        # Only show published pages
        return Page.objects.filter(is_published=True)