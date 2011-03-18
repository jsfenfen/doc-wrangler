"""
Routines to wrangle document cloud projects into a local DocumentCollection and vice versa.


$python manage.py shell

>>> from documents import docwrangler
>>> docwrangler.create_local_project(1234)

Reporters often leave out the related article URL, but this URL is the same for all the documents across the project. So alter it in the django admin: /admin/documents/documentcollection/1/

Then push the url back to dc documents:

>>> docwrangler.push_project_url('your-local-DocumentCollection-slug')

And publish the whole thing:

>>> docwrangler.publish_now('your-DocumentCollection-slug')

Or unpublish it 

>>> docwrangler.unpublish('your-DocumentCollection-slug')



"""

from datetime import datetime
from django.template.defaultfilters import slugify
from djangoproject.documents.models import *
from djangoproject.documents.utils import *



def push_project(this_collection_slug):
    """ copy a project that exists locally to document cloud """

    # will throw an error if the collection is missing.
    this_collection = DocumentCollection.objects.get(collection_slug=this_collection_slug)
    print "Got collection '%s'" % (this_collection)


    # get all local documents that are in the collection and have document cloud ids. If they don't have ids, we have no idea what's up with them. 

    contained_doc_ids = Document.objects.filter(collection=this_collection).values('document_id')

    doc_list = []

    for doc in contained_doc_ids:
        doc_list.append(doc['document_id'])

    print "Creating project with %s %s" % (this_collection.collection_headline, this_collection.collection_chatter)

   
    result = upload_project(this_collection.collection_headline, this_collection.collection_chatter)
    project_id_returned = result['project']['id']
    newid=-1
    try:
        newid = int(project_id_returned)
        print "Successfully created project %s" % (newid)
    except:
        print "Couldn't create project"
        assert False
    # it's succesful if it gives us back a project id. If it can't create the project (because it's a duplicate name, perhaps) it won't return one.


    result2 = put_existing_project(newid, doclist)
    print result2



def push_project_url(this_collection_slug):
    """ Reporters tend to not add the related article id -- possibly because they don't know it when they're annotating documents. . Sync the related article id to the local projects' related article id."""
    # will throw an error if the collection is missing.
    this_collection = DocumentCollection.objects.get(collection_slug=this_collection_slug)
    print "Got collection '%s'" % (this_collection)

    this_collection_link = this_collection.collection_backlink

    # get all local documents that are in the collection and have document cloud ids. If they don't have ids, we have no idea what's up with them. 

    contained_doc_ids = Document.objects.filter(collection=this_collection).values('document_id')
    linkparams = {
        'related_article':this_collection_link,
    }
    for dc_id in contained_doc_ids:
        theid = dc_id['document_id']
        print "trying to update document %s " % (theid)
        results = update_document(theid, linkparams)
        print results
        


def create_local_document(doc_id, local_project):
    """ create a new local document as part of a local project. Will update it if it already exists.
    """
    print "creating doc %s in project %s" % (doc_id, local_project)

    doc_json = get_doc_json(doc_id)['document']
    print doc_json

    
    # will break if dc stops using gmt. What's up with %z ? 
    created_at=datetime.strptime(doc_json['created_at'], "%a, %d %b %Y %H:%M:%S +0000")
    updated_at=datetime.strptime(doc_json['updated_at'], "%a, %d %b %Y %H:%M:%S +0000")

    newdoc, created = Document.objects.get_or_create(collection=local_project, document_headline=doc_json['title'],  document_description=doc_json['description'], document_id=doc_id, source=doc_json['source'], created_at=created_at, updated_at=updated_at, contributor=doc_json['contributor'])
    # it seems like related article isn't necessarily there ? 
    try: 
        newdoc.related_article_url=doc_json['related_article']
        newdoc.save()
    except:
        pass



def create_local_project(project_to_pull_id):
    """ create a new local project, then create individual documents
    Will fail if the unique id already exists so we don't overwrite local modifications
    """
    project_json="-1"
    result = get_project_json()
    print result
    for project in result['projects']:
        if project['id']==project_to_pull_id:
            project_json=project

    if (project_json=="-1"):
        raise Exception("Can't find project id %s" % (project_to_pull_id))

    new_project_id=project_json['id']
    headline=project_json['title']
    print "Creating new project: %s, id=%s \n from json: %s" % (headline, new_project_id, project_json) 

    newproj = DocumentCollection()
    newproj.project_id =  new_project_id
    newproj.collection_headline=headline
    newproj.collection_slug=slugify(unicode(headline))


    newproj.collection_chatter=project_json['description']
    newproj.save()

    for doc_id in project_json['document_ids']:
        create_local_document(doc_id, newproj)

def publish_now(local_project_slug):
    """ makes all parts of a project--both local and on dc--public """
    this_collection = DocumentCollection.objects.get(collection_slug=local_project_slug)
    this_collection.public=True
    this_collection.save()
    
    related_documents=Document.objects.filter(collection=this_collection)

    params = {
        'access':'public',
    }
    
    for doc in related_documents:
        doc.public=True
        doc.save()
        results = update_document(doc.document_id, params)
        print results
        

def unpublish(local_project_slug):
    """ makes all parts of a project--both local and on dc--public """
    this_collection = DocumentCollection.objects.get(collection_slug=local_project_slug)
    this_collection.public=False
    this_collection.save()

    related_documents=Document.objects.filter(collection=this_collection)

    params = {
        'access':'organization',
    }

    for doc in related_documents:
        doc.public=False
        doc.save()
        results = update_document(doc.document_id, params)
        print results


    