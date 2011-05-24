## Import django to run as a standalone

import sys

from optparse import OptionParser
from django.core.management import setup_environ
from helpers import django_location
sys.path.append(django_location())

from myproject import settings
setup_environ(settings)


from myproject.documents.docwrangle import dochandler                



# assumes these are set in settings
handler = dochandler(settings.DOCUMENT_CLOUD_LOGIN, settings.DOCUMENT_CLOUD_PASSWORD)

result = handler.get_project_json()

for project in result['projects']:
    print "Found '%s' with id: %s" % (project['title'], project['id'])

