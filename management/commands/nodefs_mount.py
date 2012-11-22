# -*- coding: utf-8 -*-

import sys
import os

from django.core.management.base import BaseCommand
#from django.core.management.base import CommandError
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        if hasattr(settings, 'NODEFS_PROFILE_MODULE') and not os.environ.get('NODEFS_PROFILE_MODULE'):
            os.environ['NODEFS_PROFILE_MODULE'] = settings.NODEFS_PROFILE_MODULE

        if len(args) < 1:
            print """
            Usage: manage.py nodefs_mount <mount point path>
            """
            sys.exit(0)

        from nodefs import mounter

        path = args[0]
        mounter.mount(path)
