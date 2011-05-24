""" Reporters tend to not add the related article id -- possibly because they don't know it when they're annotating documents. . Sync the related article id to the local projects' related article id."""


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


def push_project_url(local_project_id, verbose):
    handler = dochandler(settings.DOCUMENT_CLOUD_LOGIN, settings.DOCUMENT_CLOUD_PASSWORD)
    # will throw an error if the collection is missing.
    this_collection = DocumentCollection.objects.get(project_id=local_project_id)
    if (verbose): print "Got collection '%s'" % (this_collection)

    this_collection_link = this_collection.collection_backlink

    # get all local documents that are in the collection and have document cloud ids. If they don't have ids, we have no idea what's up with them. 

    contained_doc_ids = Document.objects.filter(collection=this_collection).values('document_id')
    linkparams = {
        'related_article':this_collection_link,
    }
    for dc_id in contained_doc_ids:
        theid = dc_id['document_id']
        if (verbose): print "trying to update document %s " % (theid)
        results = handler.update_document(theid, linkparams)
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

        push_project_url(the_project_id, options.verbose)



    else:
        print "Please enter a project id!\n"
        parser.print_help()
