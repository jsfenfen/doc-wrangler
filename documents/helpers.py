# set the django root here so we can import django code, etc, with sys.path.append(django_location())

def django_location():
    return '/your/django/root/'


## Exceptions -- ripped off from Ben Welsh's python-documentcloud

class CredentialsMissingError(Exception):
    """
    Raised if an API call is attempted without the required login credentials
    """
    pass


class CredentialsFailedError(Exception):
    """
    Raised if an API call fails because the login credentials are no good.
    """
    pass


class DoesNotExistError(Exception):
    """
    Raised when the user asks the API for something it cannot find.
    """
    pass
    
class LocalResourceNotExistError(Exception):
    """
    Raised when the user tries to add a local document to a local collection that doesn't exist
    """
    pass    

class DuplicateObjectError(Exception):
    """
    Raised when the user tries to add a duplicate to a distinct list.
    """
    pass
    
    




