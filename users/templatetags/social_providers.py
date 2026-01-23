from django import template
from django.contrib.sites.shortcuts import get_current_site

from allauth.socialaccount.models import SocialApp

register = template.Library()


@register.simple_tag(takes_context=True)
def has_social_provider(context, provider):
    request = context.get("request")
    if request is None:
        return False

    site = get_current_site(request)
    return SocialApp.objects.filter(provider=provider, sites=site).exists()
