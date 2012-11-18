# -*- coding: utf-8 -*-

import sys
from nodefs import mounter
from django.core.management.base import BaseCommand
#from django.core.management.base import CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):

        if len(args) < 1:
            print """
            Usage: manage.py nodefs_mount <mount point path>
            """
            sys.exit(0)

        path = args[0]
        mounter.mount(path)
