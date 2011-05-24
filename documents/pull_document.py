"""  Sync a local document to a documentcloud-hosted document, creating or updating based on document cloud slug """


import sys
from datetime import datetime
from optparse import OptionParser
from django.template.defaultfilters import slugify
from django.core.management import setup_environ
from helpers import django_location
sys.path.append(django_location())

from myproject import settings
setup_environ(settings)

from myproject.documents.models import *
from myproject.documents.docwrangle import dochandler
from myproject.documents.helpers import LocalResourceNotExistError



def sync_document(dc_slug, local_project_id, verbose=True):
    handler = dochandler(settings.DOCUMENT_CLOUD_LOGIN, settings.DOCUMENT_CLOUD_PASSWORD)
    doc_json = handler.get_doc_json(dc_slug)['document']
    
    if (verbose): print "Retrieved Documentcloud json:\n %s" % (doc_json)
    
    local_project = None
    try:
        local_project = DocumentCollection.objects.get(project_id=local_project_id)
    except:
        raise LocalResourceNotExistError("The local project you're trying to add this document to does not exist. Perhaps it hasn't been created yet?")
    
    newdoc, created = Document.objects.get_or_create(collection=local_project, document_id=dc_slug)
    
    
    # will break if dc stops using gmt. What's up with %z ?
    created_at=datetime.strptime(doc_json['created_at'], "%a, %d %b %Y %H:%M:%S +0000")
    updated_at=datetime.strptime(doc_json['updated_at'], "%a, %d %b %Y %H:%M:%S +0000")
    
    newdoc.document_headline=doc_json['title']
    newdoc.document_description=doc_json['description']
    newdoc.source=doc_json['source']
    newdoc.created_at=created_at
    newdoc.updated_at=updated_at
    newdoc.contributor=doc_json['contributor']
    
    # it seems like related article isn't necessarily there ? 
    try: 
        newdoc.related_article_url=doc_json['related_article']
        newdoc.save()
    except:
        newdoc.save()
    
# if we're running as a script
if __name__ == '__main__':

    #options stuff
    usage = "usage: %prog [options] document_cloud_slug"
    parser = OptionParser(usage=usage)

    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
                  
    (options, args) = parser.parse_args()

    if len(args) > 0:
        document_slug=args[0]
        if len(args) > 1:
            the_project_id = args[1]
        else: 
            the_project_id = None
            
        sync_document(document_slug, the_project_id, options.verbose)
        
        
        
    else:
        print "Please enter a project id!\n"
        parser.print_help()    