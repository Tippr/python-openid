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
    'ns_uri_1_0',
    'supported',
    'Request',
    'Response',
]

UI_MODE_CHECK_SESSION = 'x-has-session'

ns_uri_1_0 = 'http://specs.openid.net/extensions/ui/1.0'
ns_uri = ns_uri_1_0

try:
    registerNamespaceAlias(ns_uri_1_0, 'ui')
except NamespaceAliasRegistrationError, e:
    oidutil.log('registerNamespaceAlias(%r, %r) failed: %s' % (ns_uri_1_0,
                                                               'ui', str(e),))

def supported(endpoint):
    return endpoint.usesExtension(ns_uri_1_0)

class Request(Extension):

    ns_alias = 'ui'

    def __init__(self, langs=None, ui_mode=None, check_session=None, icon=None,
                 ui_ns_uri=ns_uri):
        """Initialize an empty UI hinting request"""
        Extension.__init__(self)
        self.ns_uri = ui_ns_uri
        if check_session and ui_mode not in (None, UI_MODE_CHECK_SESSION):
            raise ValueError( \
                "invalid combination of ui_mode %r / check_session %r" \
                % (ui_mode, check_session))
        if check_session:
            ui_mode = UI_MODE_CHECK_SESSION
        self.ui_mode = ui_mode
        self.icon = icon
        self.langs = langs

    @classmethod
    def fromOpenIDRequest(cls, request):
        self = cls()
        message = request.message.copy()

        args = message.getArgs(self.ns_uri)
        self.parseExtensionArgs(args)

        return self

    def parseExtensionArgs(self, args, strict=False):
        langs = args.pop('lang', None)
        self.langs = [ lang.strip() for lang in langs.split(',') ] if langs else None
        self.icon = args.pop('icon', None)
        self.ui_mode = args.pop('mode', None)
        if args and strict:
            raise ValueError('unrecoginzed values %r' % (args,))

    def getExtensionArgs(self):
        args = {}
        if self.ui_mode is not None:
            args['mode'] = self.ui_mode
        if self.langs:
            args['lang'] = ','.join(self.langs)
        if self.icon is not None:
            args['icon'] = 'true'

        return args

class Response(Extension):
    ns_alias = 'ui'

    def __init__(self, has_session=None, ui_ns_uri=ns_uri):
        Extension.__init__(self)

        self.ns_uri = ui_ns_uri
        self.has_session = has_session

    @classmethod
    def fromSuccessResponse(cls, success_response):
        self = cls()
        args = success_response.message.getArgs(self.ns_uri)

        mode = args.pop('mode', None)
        if mode == None:
            self.has_session = False
        else:
            if mode == UI_MODE_CHECK_SESSION:
                self.has_session = True
            else:
                raise ValueError('mode %r not valid in response', mode)

        return self

    def getExtensionArgs(self):
        if self.has_session:
            return {'mode': UI_MODE_CHECK_SESSION}
        else:
            return {}
