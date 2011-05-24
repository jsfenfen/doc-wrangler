import MultipartPostHandler
import base64
import urllib2
from urllib import urlencode
import simplejson

from helpers import CredentialsFailedError, DoesNotExistError

# related commands (can be run via fab):
#  show_projects.py
#  show_local_projects.py [-s searchterm]
#  pull_project.py  project_id 
#  pull_document.py document_id [project_id - default is none]
#  push_project_url.py project_id
#  publish_local.py project_id
#  publish_now.py project_id
#  unpublish_now.py project_id

class dochandler(object):
    """ Super thin wrapper for document cloud that returns json """ 
    

    def __init__(self, login, password):
        self.login = login
        self.password = password
        
        # where document cloud is
        self.url_base = "https://www.documentcloud.org/"
        
        # set up openers
        self.post_opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
        self.get_opener =  urllib2.build_opener()
        
        # auth string to reuse
        self.auth = base64.encodestring('%s:%s' % (login, password))[:-1]
        
        

    def get_json(self, url_to_read):
        request = urllib2.Request(url_to_read)
        request.add_header('Authorization','Basic %s' % self.auth)


        try:
            response = self.get_opener.open(request)
        except urllib2.URLError as e:    
            
            if e.code == 404:
                raise DoesNotExistError("The resource you've requested does not exist or is unavailable without the proper credentials.")
            elif e.code == 401:
                raise CredentialsFailedError("The resource you've requested requires proper credentials.")
            else:
                raise e

        return (simplejson.load(response))
    
    def post_json(self, url_to_put, params):
        request = urllib2.Request(url_to_put, params)
        request.add_header('Authorization','Basic %s' % self.auth)
        
        try:
            response = self.post_opener.open(request)
            #response = request_method(request)
            #except urllib2.HTTPError as (e):
        except urllib2.URLError as e:    
            
            if e.code == 404:
                raise DoesNotExistError("The resource you've requested does not exist or is unavailable without the proper credentials.")
            elif e.code == 401:
                raise CredentialsFailedError("The resource you've requested requires proper credentials.")
            else:
                raise e
        
        return (simplejson.load(response))
    
    def get_project_json(self):
        """Get the json representation of all projects visible to the credentials given to the handler. If bad credentials are given, this will be a list of the most recent public projects.   """
        projects_url = "%sapi/projects.json" % (self.url_base)
        return self.get_json(projects_url)

    def get_doc_json(self, doc_id):
        """ Get the json representation of a document """
        doc_url = "%sapi/documents/%s.json" % (self.url_base, doc_id)
        return self.get_json(doc_url) 
    
    def upload_document(self, thefile, params):
        """ Upload a document """
        # Add a filehandle to the parameters
        params['file']= open(thefile, 'rb')
        upload_url = "%sapi/upload.json" % (self.url_base)
        return self.post_json(upload_url, params)


    def update_document(self, doc_id, params):
        """ Overwrite a document cloud document.
        Params is a dictionary of parameters that looks like this:

        params = {
        'title':'a title',
        'description':'description',
        'access':'private',
        }

        For full details see here: https://www.documentcloud.org/#help/api 
        Return value is the json representation of the altered document

        """
        # set the method to be put. See DC docs. 
        params['_method']='put'
        upload_url = "%sapi/documents/%s.json" % (self.url_base, doc_id)
        print "using url: %s" % (upload_url)
        request = urllib2.Request(upload_url, params)
        request.add_header('Authorization','Basic %s' % self.auth)

        return self.post_json(upload_url, params)


    def upload_project(self, title, description, document_list):
        """ Create a new project with a title and description. """

        params = [
        ('title',title),
        ('description',description),
        ]
        for d in document_list:
            params.append(('document_ids[]',d))

        encoded_params = urlencode(params)

        upload_url = "%sapi/projects.json" % (self.url_base)
        request = urllib2.Request(upload_url, params)
        request.add_header('Authorization','Basic %s' % auth)
        return self.post_json(upload_url, encoded_params)