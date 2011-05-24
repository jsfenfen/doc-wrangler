""" makes only the local version of the document public """


import sys
from optparse import OptionParser
from django.core.management import setup_environ
from helpers import django_location
sys.path.append(django_location())

from myproject import settings
setup_environ(settings)

from myproject.documents.models import *
from myproject.documents.docwrangle import dochandler
from myproject.documents.helpers import LocalResourceNotExistError

def publish_local(local_project_id):

    handler = dochandler(settings.DOCUMENT_CLOUD_LOGIN, settings.DOCUMENT_CLOUD_PASSWORD)


    this_collection = DocumentCollection.objects.get(project_id=local_project_id)
    this_collection.public=True
    this_collection.save()

    related_documents=Document.objects.filter(collection=this_collection)

    for doc in related_documents:
        doc.public=True
        doc.save()
        
        

# if we're running as a script
if __name__ == '__main__':

    #options stuff
    usage = "usage: %prog [options] project_id"
    parser = OptionParser(usage=usage)


    (options, args) = parser.parse_args()

    if len(args) > 0:
        the_project_id = args[0]

        publish_local(the_project_id)

    else:
        print "Please enter a project id!\n"
        parser.print_help()