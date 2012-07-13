# -*- coding: utf-8 -*-

import sys
from nodefs import mounter
from django.core.management.base import BaseCommand
#from django.core.management.base import CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        path = args[0]

        if not path:
            print """
            Usage: manage.py nodefs <action> <mount point path>
            Available actions:
            """
            sys.exit(0)

        mounter.mount(path)
