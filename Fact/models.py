from __future__ import unicode_literals

import os
from uuid import uuid4
import datetime
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from versatileimagefield.fields import VersatileImageField, PPOIField
from itertools import chain
from django.db.models import Q
from django.urls import reverse

# Create your models here.


def path_and_rename(instance, filename):
    now = datetime.datetime.now()
    upload_to = 'photos/' + str(now.year) + '/' + str(now.month) + '/' + str(now.day) + '/'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_base')
    profile = JSONField(null=True, blank=True)
    image = VersatileImageField('Path', upload_to=path_and_rename, ppoi_field='path_ppoi')

    path_ppoi = PPOIField()

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.image.storage, self.image.path
        # Delete the model before the file
        super(Member, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)

    def __str__(self):
        return self.user.username

    def facts(self):
        return Fact.objects.filter(creator=self)


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.CharField(max_length=60, unique=True)
    icon = VersatileImageField('Path', upload_to=path_and_rename, ppoi_field='path_ppoi', blank=True)
    description = models.CharField(max_length=160, blank=True)
    parent = models.ForeignKey("self", null=True, default=None, related_name='parent_category',
                               on_delete=models.SET_NULL, blank=True)
    path_ppoi = PPOIField()

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.icon.storage, self.icon.path
        # Delete the model before the file
        super(Category, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)

    def __str__(self):
        return self.name

    def count_object(self):
        result = Object.objects.filter(category=self).count()
        for child in self.childs():
            result = result + Object.objects.filter(category=child).count()
        return result

    def childs(self):
        return Category.objects.filter(parent=self)

    def posts(self):
        self_posts = Object.objects.filter(category=self).order_by('pub_date')
        for child in self.childs():
            self_posts = list(chain(self_posts, Object.objects.filter(category=child).order_by('pub_date')))
        return self_posts[:6]

    def posts_all(self):
        self_posts = Object.objects.filter(Q(category__parent=self) | Q(category=self)).order_by('-id')
        return self_posts

    def get_absolute_url(self):
        return reverse('fact:category_show', kwargs={'slug': self.slug})


class Object(models.Model):
    name = models.CharField(max_length=60, null=False, default="aaa")
    title = models.CharField(max_length=160, unique=True)
    slug = models.CharField(max_length=160, unique=True)
    description = models.TextField(default=None, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category', blank=True)
    pub_date = models.DateField(auto_now=True)
    image = VersatileImageField('Path', upload_to=path_and_rename, ppoi_field='path_ppoi', blank=True)

    path_ppoi = PPOIField()

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.image.storage, self.image.path
        # Delete the model before the file
        super(Object, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)

    def __str__(self):
        return self.name

    def facts(self):
        return Fact.objects.filter(object=self)

    def get_absolute_url(self):
        return reverse('fact:object_show', kwargs={'slug': self.slug})


class Fact(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator')
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='object')
    content = models.TextField(unique=True)
    source = JSONField(null=True, blank=True)
    pub_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.object.name

    def comments(self):
        return Comment.objects.filter(fact=self)

    def confirm(self):
        return Confirm.objects.filter(fact=self).count()


class Comment(models.Model):
    fact = models.ForeignKey(Fact, on_delete=models.CASCADE, related_name='fact_comment')
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='member_comment', blank=True, null=True,
                               default=None)
    guess = JSONField(blank=True, null=True)
    content = models.TextField()
    parent = models.ForeignKey("self", null=True, default=None, related_name='parent_comment',
                               on_delete=models.SET_NULL, blank=True)
    pub_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.fact.object.name + self.member.username


class Confirm(models.Model):
    fact = models.ForeignKey(Fact, on_delete=models.CASCADE, related_name='fact_confirm')
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='member_confirm')
