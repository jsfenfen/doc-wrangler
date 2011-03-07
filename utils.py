import MultipartPostHandler
import base64
import urllib2
import simplejson

# set up openers
post_opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
get_opener =  urllib2.build_opener()

# credentials
login=''
password = ''

# auth string to reuse
auth = base64.encodestring('%s:%s' % (login, password))[:-1]

# where document cloud is
url_base = "https://www.documentcloud.org/"

def get_json(url_to_read):
    request = urllib2.Request(url_to_read)
    request.add_header('Authorization','Basic %s' % auth)
    return (simplejson.load(get_opener.open(request)))
    
def post_json(url_to_put, params):
    request = urllib2.Request(url_to_put, params)
    request.add_header('Authorization','Basic %s' % auth)
    return (simplejson.load(post_opener.open(request)))
    
def get_project_json():
    """Get the json representation of all projects

    # show all documents in projects
    
    result = get_project_json()
    for project in result['projects']:
        print "Got project %s '%s'" % (project['id'], project['title'])
        for document in project['document_ids']:
            print "\tincludes doc %s" % (document)
    
    """
    projects_url = "%sapi/projects.json" % (url_base)
    return get_json(projects_url)

def get_doc_json(doc_id):
    """ Get the json representation of a document 
    
    result = get_doc_json('29138-goddardiv')
    print "retrieved %s title: %s" (result['document']['id'], result['document']['title'])
    
    """
    doc_url = "%sapi/documents/%s.json" % (url_base, doc_id)
    return get_json(doc_url) 
    
def upload_document(thefile, params):
    """ Params is a dictionary of parameters that looks like this:
    
    params = {
    'title':'a title',
    'description':'description',
    }
    
    It doesn't include the file, which is passed in separately and added below
    For full details see here: https://www.documentcloud.org/#help/api 
    Return value is the json representation of the new file
    
    
    myparams = {
    'title':'this is the itle',
    'description':'this is the description',
    }
    myfile = "doc1.pdf"
    result=upload_document(myfile, myparams)
    print result
    
    """
    # Add a filehandle to the parameters
    params['file']= open(thefile, 'rb')
    upload_url = "%sapi/upload.json" % (url_base)
    return post_json(upload_url, params)

def update_document(doc_id, params):
    """ Params is a dictionary of parameters that looks like this:

    params = {
    'title':'a title',
    'description':'description',
    'access':'private',
    }

    For full details see here: https://www.documentcloud.org/#help/api 
    Return value is the json representation of the altered document

    
    myparams = {
    'related_article':'http://my/news/story.html',
    }
    myid = '12345-my-doc-slug'
    result = update_document(myid, myparams)
    print result

    """
    # set the method to be put. See DC docs. 
    params['_method']='put'
    upload_url = "%sapi/documents/%s.json" % (url_base, doc_id)
    request = urllib2.Request(upload_url, params)
    request.add_header('Authorization','Basic %s' % auth)

    return post_json(upload_url, params)
    

