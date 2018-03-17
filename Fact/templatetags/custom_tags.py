from django import template
from django.apps import apps
from django.utils.safestring import mark_safe
from Fact.models import Category, Confirm, Member, Fact


register = template.Library()


@register.filter(is_safe=True)
def half_slug(value):
    return value.replace(" ", "-")


@register.simple_tag
def get_categories():
    return Category.objects.filter(parent__isnull=True)


@register.simple_tag
def verify_message(number, user):
    if int(number) == 0:
        return "Non verified"
    else:
        if user.is_authenticated:
            data = Confirm.objects.filter(member=user)
            if data:
                return "You verified this"
        return str(number) + " people confirm that's true!"


@register.simple_tag
def verify_check(number):
    if int(number) == 0:
        return "non-verified"
    else:
        return "verified"


@register.simple_tag
def get_image_safe(image, size):
    if image:
        return image.crop[size]
    else:
        return "/static/img/thumbnail_" + size + ".png"


@register.simple_tag
def allow_page(current_page, index):
    if index < current_page:
        return index > current_page - 5
    elif index > current_page:
        return index < current_page + 5
    else:
        return True


@register.simple_tag
def get_facts(user):
    return Fact.objects.filter(creator=user).count()


@register.simple_tag
def get_confirm(user):
    return Confirm.objects.filter(member=user).count()


@register.simple_tag
def get_member(user):
    return Member.objects.filter(user=user).first()

