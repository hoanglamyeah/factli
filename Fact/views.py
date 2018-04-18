import json
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
import urllib.request
from urllib.parse import urlparse
from django.core.files import File
from . import models


# Create your views here.


def index(request):
    # categories = models.Category.objects.all()
    objs = models.Object.objects.all().order_by('-id')[:8]
    return render(request, 'index.html', {'objs': objs})


def fact_post(request):
    pass


def get_object(request, slug):
    object = models.Object.objects.get(slug=slug)
    facts = models.Fact.objects.filter(object=object)
    if request.GET.get('filter') is not None:
        admin = User.objects.get(pk=1)
        if request.GET['filter'] == "system":
            facts = facts.filter(creator=admin)
        elif request.GET['filter'] == "member":
            facts = facts.exclude(creator=admin)
    return render(request, 'fact_get.html', {"object": object, "facts": facts})


def fact_get(request, slug, fact_id):
    object_data = models.Object.objects.get(slug=slug)
    index = int(fact_id) - 1
    if request.method == 'GET':
        return render(request, 'fact_get_sub.html',
                      {"object": object_data, "fact": object_data.facts()[index], "index": fact_id})
    else:
        if request.POST['submit'] == "verified":
            if request.user.is_authenticated:
                fact = models.Fact.objects.get(pk=int(request.POST['fact_id']))
                confirm = models.Confirm.objects.filter(fact=fact, member=request.user)
                if confirm:
                    confirm.delete()
                else:
                    confirm = models.Confirm(member=request.user, fact=fact)
                    confirm.save()
        elif request.POST['submit'] == "comment_add":
            parent = models.Comment.objects.filter(pk=int(request.POST['parent_id'])).first()
            fact = models.Fact.objects.get(pk=int(request.POST['fact_id']))
            if request.user.is_authenticated:
                comment = models.Comment(fact=fact, member=request.user, parent=parent,
                                         content=request.POST['comment_content'])
                comment.save()
            else:
                guest = {"name": request.POST['guest_name'], "email": request.POST['guest_email']}
                comment = models.Comment(fact=fact, guess=guest, parent=parent,
                                         content=request.POST['comment_content'])
                comment.save()
        return render(request, 'fact_get_sub.html',
                      {"object": object_data, "fact": object_data.facts()[index], "index": fact_id})


def fact_update(request):
    pass


def fact_delete(request):
    pass


def archive_index(request):
    categories = models.Category.objects.filter()
    paginator = Paginator(categories, 8)
    page = request.GET.get('page')
    try:
        list_categories = paginator.page(page)
    except PageNotAnInteger:
        list_categories = paginator.page(1)
    except EmptyPage:
        list_categories = paginator.page(paginator.num_pages)
    return render(request, 'archive_index.html', {"categories": list_categories})


def archive_detail(request, slug):
    archive = models.Category.objects.get(slug=slug)
    objects = archive.posts_all()
    paginator = Paginator(objects, 8)
    page = request.GET.get('page')
    try:
        list_objects = paginator.page(page)
    except PageNotAnInteger:
        list_objects = paginator.page(1)
    except EmptyPage:
        list_objects = paginator.page(paginator.num_pages)
    return render(request, 'archive_detail.html', {"objects": list_objects, "archive": archive})


def member_index(request):
    users = User.objects.all()
    paginator = Paginator(users, 8)
    page = request.GET.get('page')
    try:
        list_members = paginator.page(page)
    except PageNotAnInteger:
        list_members = paginator.page(1)
    except EmptyPage:
        list_members = paginator.page(paginator.num_pages)
    return render(request, 'registration/member.html', {"members": list_members})


def member_get(request, member_id):
    member = User.objects.filter(pk=member_id).first()
    return render(request, 'registration/user.html', {"member": member})


def page_faq(request):
    return render(request, 'page/faq.html', {})


def page_term(request):
    return render(request, 'page/term.html', {})


def page_support(request):
    return render(request, 'page/support.html', {})


def page_career(request):
    return render(request, 'page/career.html', {})


def get_title(name):
    import random
    list_title = [
        'Interesting facts about ' + name,
        'Surprising facts about ' + name,
        'Exciting facts about ' + name,
        name + ' facts that you may not know',
    ]
    return random.choice(list_title)


@csrf_exempt
def import_data(request):
    if request.method == "GET":
        return render(request, 'page/import.html', {})
    if request.method == "POST":
        user = User.objects.get(pk=1)
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        name = body['name']
        description = body['description']
        category_name = body['category'] or 'None'
        image_url = body['image'] or 'None'
        sub_category_name = body['sub_category'] or 'None'
        obj = models.Object.objects.filter(slug=slugify(name)).first()
        try:
            category = models.Category.objects.filter(slug=slugify(category_name)).first()
            if category_name != 'None':
                if category is not None:
                    category = category
                else:
                    category = models.Category(name=category_name, slug=slugify(category_name))
                    category.save()
            else:
                return HttpResponse("Missing Category")
            if sub_category_name != 'None':
                sub_category = models.Category.objects.filter(slug=slugify(sub_category_name), parent=category).first()
                if sub_category is not None:
                    category = sub_category
                else:
                    sub_category = models.Category(
                        name=sub_category_name,
                        slug=slugify(sub_category_name),
                        parent=category
                    )
                    sub_category.save()
                    category = sub_category
            massage = ""
            if obj is None:
                obj = models.Object(
                    name=name,
                    description=description,
                    title=get_title(name),
                    slug=slugify(name),
                    category=category
                )
                obj.save()
                if image_url != 'None':
                    name = urlparse(image_url).path.split('/')[-1]
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(urllib.request.urlopen(image_url).read())
                    img_temp.flush()
                    obj.image.save(name, File(img_temp), save=True)
                    obj.save()
            else:
                if not obj.image:
                    if image_url != 'None':
                        name = urlparse(image_url).path.split('/')[-1]
                        img_temp = NamedTemporaryFile(delete=True)
                        img_temp.write(urllib.request.urlopen(image_url).read())
                        img_temp.flush()
                        obj.image.save(name, File(img_temp), save=True)
                        obj.save()
                massage = "Duplicated\n"
            if body['facts']:
                for fact in body['facts']:
                    if fact != "" and models.Fact.objects.filter(content=fact).first() is None:
                        fact_inside = models.Fact(creator=user, object=obj, content=fact)
                        fact_inside.save()
            return HttpResponse(massage + "Inserted")
        except IntegrityError:
            return HttpResponse("Duplicated")


def search(request):
    objects = models.Object.objects.all()
    if request.GET.get('query') is not None:
        objects = objects.filter(name__icontains=request.GET.get('query'))
    paginator = Paginator(objects, 8)
    page = request.GET.get('page')
    try:
        list_objects = paginator.page(page)
    except PageNotAnInteger:
        list_objects = paginator.page(1)
    except EmptyPage:
        list_objects = paginator.page(paginator.num_pages)
    return render(request, 'search.html', {"objects": list_objects, "keyword": request.GET.get('query')})


def test(request):
    return HttpResponse("OK")
