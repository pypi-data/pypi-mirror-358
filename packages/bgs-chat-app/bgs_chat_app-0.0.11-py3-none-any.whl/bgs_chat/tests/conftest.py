import os
import django
# from django.conf import settings
import sys
# from django.core.management import call_command

import pytest

pytestmark = pytest.mark.django_db

sys.path.append(os.path.join(os.path.dirname(__file__)))
os.environ["DJANGO_SETTINGS_MODULE"] = "bgs_chat_site.settings"
django.setup()