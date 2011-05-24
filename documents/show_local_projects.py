

import sys
from optparse import OptionParser
from django.core.management import setup_environ
from helpers import django_location
sys.path.append(django_location())

from myproject import settings
setup_environ(settings)

from myproject.documents.models import *




#options stuff
parser = OptionParser()
parser.add_option("-s", dest="search", help="Search project headlines")
                  
(options, args) = parser.parse_args()

#print "options = %s args = %s search = %s" % (options, args, options.search)                  

if (options.search): 
    collections = DocumentCollection.objects.filter(collection_headline__icontains=options.search)
else:
    collections = DocumentCollection.objects.all()

for collection in collections:
    print "Found local collection id: %s with headline: %s and project id %s" % (collection.id, collection.collection_headline, collection.project_id)