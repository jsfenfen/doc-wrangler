from django.db import models
import re
  
  
class DocumentManager(models.Manager):
    def get_query_set(self):
        return super(DocumentManager, self).get_query_set().exclude(public=False).order_by('document_headline')
  
  
class DocumentCollection(models.Model):
    project_id = models.IntegerField(null=True, blank=True)
    collection_headline = models.CharField(max_length=255)
    collection_slug = models.SlugField(help_text="Do not alter this unless you know what you are doing.")
    collection_chatter = models.TextField(help_text="", null=True, blank=True)
    collection_backlink = models.URLField(help_text="This is a project-wide related article link, that can be pushed to each of the individual documents using docwrangler.push_project_url('project-slug').", verify_exists=False)
    backlink_headline = models.CharField(max_length=255)
    public = models.BooleanField(default=False, help_text="Check this box and it is live")   
     
    def get_absolute_url(self):
        return "/documents/%s/" % self.collection_slug
    def __unicode__(self):
        return self.collection_headline
     
    
## Pull the document cloud slug into its component parts  
dcslug = re.compile('(\d+?)\-(.+)')
     
class Document(models.Model):
    collection = models.ForeignKey(DocumentCollection)
    document_headline = models.CharField(max_length=255)
    document_description = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    related_article_url = models.CharField(max_length=255, null=True, blank=True)
    created_at =  models.DateTimeField(null=True, blank=True)
    updated_at =  models.DateTimeField(null=True, blank=True)
    contributor = models.CharField(max_length=63, null=True, blank=True)
    
    document_id = models.CharField("document cloud id", max_length=255, help_text="What is the documentcloud id for this document? Should look like something like: 10821-enforcementaction_test")
    public = models.BooleanField(default=False, help_text="Check this box and it is live")
    objects = models.Manager() 
    live_documents = DocumentManager()   
     
     
    def get_absolute_url(self):
        return "/documents/%s/%s/" % (self.collection.collection_slug, self.document_slug)
    def __unicode__(self):
        return self.collection.collection_headline + ": " + self.document_headline 
    def get_thumb(self):
        """Return the image url of the document"""
        slug_parts = dcslug.search(self.document_id)
        if (slug_parts):
  
            numeric_part = slug_parts.group(1)
            text_part = slug_parts.group(2)
            slug = "http://s3.documentcloud.org/documents/%s/pages/%s-p1-thumbnail.gif" % (numeric_part, text_part)
            return slug
        else:
            return None