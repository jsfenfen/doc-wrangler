"""  Sync a local project to a documentcloud-hosted project, creating or updating local resources as it goes """


import sys
from optparse import OptionParser
from django.template.defaultfilters import slugify
from django.core.management import setup_environ
from helpers import django_location
sys.path.append(django_location())

from myproject import settings
setup_environ(settings)

from myproject.documents.models import *
from myproject.documents.docwrangle import dochandler
from myproject.documents.pull_document import sync_document
from myproject.documents.helpers import DoesNotExistError

def create_project(project_to_pull_id, verbose):
    handler = dochandler(settings.DOCUMENT_CLOUD_LOGIN, settings.DOCUMENT_CLOUD_PASSWORD)

    result = handler.get_project_json()



    project_json = "-1"
    for project in result['projects']:
        if project['id']==project_to_pull_id:
            project_json=project

    if (project_json=="-1"):
        raise DoesNotExistError("The resource you've requested does not exist or is unavailable without the proper credentials.")
    #    raise Exception("Can't find project id %s" % (project_to_pull_id))

    #print "got json: %s" % (project_json)
    newproj, created = DocumentCollection.objects.get_or_create(project_id=project_to_pull_id)

    # Regardless of whether the project already existed locally, update it with the dc version, except for the slug
    
    newproj.collection_headline = project_json['title']
    newproj.collection_chatter =project_json['description']

    # Don't change the slug on an existing project, since that will change the URL and break links (if there are any)
    if (created):
        newproj.collection_slug = slugify(project_json['title'])
        if (verbose): print "Project created with slug %s" % (slugify(project_json['title']))
    else: 
        if (verbose): print "Updating existing local document collection"
    
    newproj.save()
    
    # Next add all the documents
    for doc_id in project_json['document_ids']:
        if (verbose): print "Handling document %s" % (doc_id)
        sync_document(doc_id, newproj.project_id, verbose)
    
    
    
# if we're running as a script
if __name__ == '__main__':

    #options stuff
    usage = "usage: %prog [options] document_cloud_project_id"
    parser = OptionParser(usage=usage)
    
    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
                  

    (options, args) = parser.parse_args()




    if len(args) > 0:
        project_id=int(args[0])
        create_project(project_id, options.verbose)
    else:
        print "Please enter a project id!\n"
        parser.print_help()    