from django import template

register = template.Library()

@register.simple_tag
def get_unread_count(thread, user):
    return thread.get_unread_count(user)
