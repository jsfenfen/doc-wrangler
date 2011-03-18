from django.contrib import admin
from yourproject.documents.models import DocumentCollection, Document
  
class DocumentCollectionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'collection_slug': ('collection_headline',) }
     
    fieldsets = (
        ('Collection', {
            'fields': ('collection_headline', 'collection_slug',)
        }),
        ('Body', {
            'fields': ('collection_chatter', 'collection_backlink', 'backlink_headline','related_investigation',)
        }),
        ('Administration', {
             'fields': ('public',)
         }),
    )
  
class DocumentAdmin(admin.ModelAdmin):
    pass


admin.site.register(DocumentCollection, DocumentCollectionAdmin)                   
admin.site.register(Document, DocumentAdmin)