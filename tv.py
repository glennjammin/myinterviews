#!/usr/bin/env python2.7
# coding: utf-8
# vim:softtabstop=4:ts=4:sw=4:expandtab:tw=120
"""
Django in single file with model and admin. Based on:-

http://fahhem.com/blog/2011/10/django-models-without-apps-or-everything-django-truly-in-a-single-file/
"""
import json, os, sys, time

def rel_path(*p): return os.path.normpath(os.path.join(rel_path.path, *p))
rel_path.path = os.path.abspath(os.path.dirname(__file__))
this = os.path.splitext(os.path.basename(__file__))[0]

from django.conf import settings
SETTINGS = dict(
    SITE_ID=1,
    DATABASES = {},
    DEBUG=True,
    TEMPLATE_DEBUG=True,
    ROOT_URLCONF = this
)
SETTINGS['TEMPLATE_DIRS'] = (rel_path(),),
SETTINGS['DATABASES']={
    'default':{
        'ENGINE':'django.db.backends.sqlite3',
        'NAME':rel_path('tvdata.db')
    }
}

SETTINGS['INSTALLED_APPS'] = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
)

if not settings.configured:
    settings.configure(**SETTINGS)


########################################################################################################################
# model definitions
########################################################################################################################
from django.db import models

class TvChannel(models.Model):
    guid  = models.CharField(max_length=32)  # the cms external_id
    title = models.CharField(max_length=64)

    class Meta:
        app_label = this
    __module__ = this

    def __unicode__(self):
        return '%s(%s)' % (self.title, self.guid)


########################################################################################################################
# django admin stufff
########################################################################################################################
from django.contrib import admin
try:
    admin.site.register(TvChannel)
except admin.sites.AlreadyRegistered:
    pass

admin.autodiscover()

from django.conf.urls import include, patterns, url
from django.http import HttpResponse


urlpatterns = patterns("",
    url(r'^admin/', include(admin.site.urls)),
)


########################################################################################################################
# utility functions for querying the Content Management System (cms)
########################################################################################################################
cmshost = "http://bbtv.qa.movetv.com"


def get_channels():
    """Return the json objects for the cms channel list"""
    path = "/cms/publish3/channel/catalog/catalog.json"
    resp = requests.get(cmshost + path)
    if resp.ok:
        return resp.json()
    else:
        raise ValueError("Failed to get channels, error=%d" % resp.status_code)


def get_shows(channel):
    """Return the json objects for the epg (Electrong Program Guide) data for what's on right now
    The data will be in this format:
    {
        "schedule": [
            {
                "external_id": <show guid>,
                "title": <show title>,
                "schedule_start": <start time (posix timestamp)>,
                "schedule_stop": <end time (posix timestamp)>,
                ...
            },
            ...
        ]
    }
    """
    now = time.time()
    nowstr = time.strftime("%y%m%d%H%M", time.gmtime(now))
    path = "/cms/publish3/channel/schedule/1/%s/%s.json" % (nowstr, channel)
    resp = requests.get(cmshost + path)
    if resp.ok:
        return resp.json()
    else:
        raise ValueError("Failed to get channels, error=%d" % resp.status_code)


########################################################################################################################
# management commands
########################################################################################################################
from django.core.management import get_commands, BaseCommand
import requests


class LoadTvChannels(BaseCommand):
    def handle(self, **options):
        newchannels = []
        json = get_channels()
        for ch in json["channels"]:
            chobj = TvChannel(guid=ch["external_id"], title=ch["title"])
            newchannels.append(chobj)
        TvChannel.objects.bulk_create(newchannels)


class ShowCurrentShows(BaseCommand):
    def handle(self, **options):
        for ch in TvChannel.objects.all():
            shows = get_shows(ch.guid)
            print "%s shows: %s" % (ch.guid, json.dumps(shows, indent=2))


########################################################################################################################
# main entry point
########################################################################################################################
if __name__=='__main__':
    # override get_app to work with us
    get_app_orig = models.get_app
    def get_app(app_label,*a, **kw):
        if app_label==this:
            return sys.modules[__name__]
        return get_app_orig(app_label, *a, **kw)
    models.get_app = get_app

    models.loading.cache.app_store[type(this+'.models',(),{'__file__':__file__})] = this

    commands = get_commands()
    commands["load_channels"] = LoadTvChannels()
    commands["print_shows"] = ShowCurrentShows()

    from django.core import management
    management.execute_from_command_line()
