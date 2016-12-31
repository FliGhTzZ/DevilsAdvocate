# config.py

from authomatic.providers import oauth2, oauth1, gaeopenid

CONFIG = {
    
    'tw': { # Your internal provider name
           
        # Provider class
        'class_': oauth1.Twitter,
        
        # Twitter is an AuthorizationProvider so we need to set several other properties too:
        'consumer_key': '########################',
        'consumer_secret': '########################',
    },
    
    'fb': {
           
        'class_': oauth2.Facebook,
        
        # Facebook is an AuthorizationProvider too.
        'consumer_key': '1047695655357905',
        'consumer_secret': '9854636ffe81faa9458f57c13ea7eacf',
        
        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['public_profile'],
    },
    
    'gae_oi': {
           
        # OpenID provider based on Google App Engine Users API.
        # Works only on GAE and returns only the id and email of a user.
        # Moreover, the id is not available in the development environment!
        'class_': gaeopenid.GAEOpenID,
    }
}
