"""User interface hinting during checkid_setup mode

As the UI extension is written as an extension to OpenID 2.0, no attempt at
compatibility with OpenID 1.0 is made.

The UI extension may perform the following functions:

- Expressing the user's language preference (openid.ui.lang)
- Request that authentication take place in a 450x500 popup window
  (openid.ui.mode='popup')
- Indicate that the user is logged in remotely but has not approved transparent
  login with the RP (x-has-session)

Section 5.1 of the standard (authentication response in a fragment) is not
addressed here.
"""

from openid.message import registerNamespaceAlias, \
     NamespaceAliasRegistrationError
from openid.extension import Extension
from openid import oidutil

try:
    basestring #pylint:disable-msg=W0104
except NameError:
    # For Python 2.2
    basestring = (str, unicode) #pylint:disable-msg=W0622

__all__ = [
    'ns_uri',
    'ns_uri_1_1',
    'supported',
    'Request',
    'Response',
]

ns_uri_1_1 = 'http://tippr.com/openid/2.0/ext/1.1'
ns_uri = ns_uri_1_1

try:
    registerNamespaceAlias(ns_uri_1_1, 'tippr')
except NamespaceAliasRegistrationError, e:
    oidutil.log('registerNamespaceAlias(%r, %r) failed: %s' % (ns_uri_1_1,
                                                               'tippr', str(e),))

def supported(endpoint):
    return endpoint.usesExtension(ns_uri_1_1)

class Request(Extension):

    ns_alias = 'tippr'

    def __init__(self, account_creation=None, desired_auth=None,
                 tippr_ns_uri=ns_uri):
        """Initialize an empty Tippr extension request"""
        Extension.__init__(self)
        self.ns_uri = tippr_ns_uri
        self.account_creation = account_creation
        self.desired_auth = desired_auth

    @classmethod
    def fromOpenIDRequest(cls, request):
        self = cls()
        message = request.message.copy()

        args = message.getArgs(self.ns_uri)
        self.parseExtensionArgs(args)

        return self

    def parseExtensionArgs(self, args, strict=False):
        account_creation_s = args.pop('account_creation', None)
        if account_creation_s is None:
            pass
        elif account_creation_s.lower() == 'true':
            self.account_creation = True
        elif account_creation_s.lower() == 'false':
            self.account_creation = False
        else:
            raise ValueError('Invalid argument for account_creation')

        self.desired_auth = args.pop('desired_auth', None)

        if args and strict:
            raise ValueError('unrecoginzed values %r' % (args,))

    def getExtensionArgs(self):
        args = {}
        if self.account_creation is not None:
            args['account_creation'] = 'true' if self.account_creation else 'false'
        if self.desired_auth:
            args['desired_auth'] = self.desired_auth

        return args

class Response(Extension):
    ns_alias = 'tippr'

    def __init__(self, facebook_token=None, signup_ip=None, channel_name=None, tippr_ns_uri=ns_uri):
        Extension.__init__(self)
        self.ns_uri = tippr_ns_uri

        self.signup_ip = signup_ip
        self.facebook_token = facebook_token
        self.channel_name = channel_name

    @classmethod
    def fromSuccessResponse(cls, success_response):
        self = cls()
        args = success_response.message.getArgs(self.ns_uri)

        self.facebook_token = args.pop('facebook_token', None)
        self.signup_ip = args.pop('signup_ip', None)
        self.channel_name = args.pop('channel_name', None)

        return self

    def getExtensionArgs(self):
        args = {}
        if self.facebook_token:
            args['facebook_token'] = self.facebook_token
        if self.signup_ip:
            args['signup_ip'] = self.signup_ip
        if self.channel_name:
            args['channel_name'] = self.channel_name
        return args

# vim: ai et sw=4 sts=4 ts=4
