""" makes all parts of a project--both local and on dc--public """


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

def unpublish_now(local_project_id, verbose):
    handler = dochandler(settings.DOCUMENT_CLOUD_LOGIN, settings.DOCUMENT_CLOUD_PASSWORD)
    this_collection = DocumentCollection.objects.get(project_id=local_project_id)
    this_collection.public=True
    this_collection.save()
    
    related_documents=Document.objects.filter(collection=this_collection)

    params = {
        'access':'organization',
    }
    
    for doc in related_documents:
        doc.public=False
        doc.save()
        results = handler.update_document(doc.document_id, params)
        if (verbose): print results
        
        
# if we're running as a script
if __name__ == '__main__':

    #options stuff
    usage = "usage: %prog [options] project_id"
    parser = OptionParser(usage=usage)

    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

    (options, args) = parser.parse_args()

    if len(args) > 0:
        the_project_id = args[0]

        unpublish_now(the_project_id, options.verbose)



    else:
        print "Please enter a project id!\n"
        parser.print_help()