from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from zope.interface import implements
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ResourceRegistries.tools.BaseRegistry import BaseRegistryTool
from Products.ResourceRegistries.tools.BaseRegistry import Resource
from Products.ResourceRegistries import permissions

from collective.sassy.interfaces import ISCSSRegistry


CSS_COMPRESSION_METHODS = ('none', 'safe')
CSS_RENDER_METHODS = ('import', 'link', 'inline')

class SassyStylesheet(Resource):
    security = ClassSecurityInfo()

    def __init__(self, id, **kwargs):
        Resource.__init__(self, id, **kwargs)
        self._data['media'] = kwargs.get('media', 'screen')
        self._data['rel'] = kwargs.get('rel', 'stylesheet')
        self._data['rendering'] = kwargs.get('rendering', 'link')
        self._data['compression'] = kwargs.get('compression', 'safe')
        self._data['applyPrefix'] = kwargs.get('applyPrefix', False)

    security.declarePublic('getMedia')
    def getMedia(self):
        result = self._data['media']
        if result == "":
            result = None
        return result

    security.declareProtected(permissions.ManagePortal, 'setMedia')
    def setMedia(self, media):
        self._data['media'] = media

    security.declarePublic('getRel')
    def getRel(self):
        return self._data['rel']

    security.declareProtected(permissions.ManagePortal, 'setRel')
    def setRel(self, rel):
        self._data['rel'] = rel

    security.declarePublic('getTitle')
    def getTitle(self):
        result = self._data['title']
        if result == "":
            result = None
        return result

    security.declareProtected(permissions.ManagePortal, 'setTitle')
    def setTitle(self, title):
        self._data['title'] = title

    security.declarePublic('getRendering')
    def getRendering(self):
        return self._data['rendering']

    security.declareProtected(permissions.ManagePortal, 'setRendering')
    def setRendering(self, rendering):
        if rendering not in CSS_RENDER_METHODS:
            raise ValueError("Rendering method %s not valid, must be one of: %s" % (
                             rendering, ', '.join(CSS_RENDER_METHODS)))
        self._data['rendering'] = rendering

    security.declarePublic('getCompression')
    def getCompression(self):
        compression = self._data.get('compression', 'safe')
        if compression in config.CSS_COMPRESSION_METHODS:
            return compression
        return 'none'

    security.declareProtected(permissions.ManagePortal, 'setCompression')
    def setCompression(self, compression):
        if compression not in CSS_COMPRESSION_METHODS:
            raise ValueError("Compression method %s not valid, must be one of: %s" % (
                             compression, ', '.join(CSS_COMPRESSION_METHODS)))
        self._data['compression'] = compression

    security.declareProtected(permissions.ManagePortal, 'setApplyPrefix')
    def setApplyPrefix(self, applyPrefix):
        self._data['applyPrefix'] = applyPrefix

    security.declarePublic('getApplyPrefix')
    def getApplyPrefix(self):
        return self._data.get('applyPrefix', False)

InitializeClass(SassyStylesheet)


class SCSSRegistryTool(BaseRegistryTool):
    """A Plone registry for managing the linking to scss files."""

    security = ClassSecurityInfo()

    id = 'portal_scss'
    meta_type = 'SCSS Stylesheets Registry'
    title = 'SCSS Registry'

    implements(ISCSSRegistry)

    #
    # ZMI stuff
    #

    manage_cssForm = PageTemplateFile('www/scssconfig', globals())

    filename_base = 'ploneStyles'
    filename_appendix = '.css'
    merged_output_prefix = u''
    cache_duration = 7
    resource_class = SassyStylesheet


    #
    # Private Methods
    #

    security.declarePrivate('clearSassyStylesheets')
    def clearSassyStylesheets(self):
        self.clearResources()

    security.declarePrivate('finalizeContent')
    def finalizeContent(self, resource, content):
        """Finalize the resource content."""
        compression = resource.getCompression()
        if compression != 'none' and not self.getDebugMode():
            orig_url = "%s/%s?original=1" % (self.absolute_url(), resource.getId())
            content = "/* %s */\n%s" % (orig_url, self._compileSCSS(content, compression))

    #
    # ZMI Methods
    #
    security.declareProtected(permissions.ManagePortal, 'manage_addSassyStylesheet')
    def manage_addSassyStylesheet(self, id, expression='', media='screen',
                                  rel='stylesheet', title='', rendering='link',
                                  enabled=False, cookable=True, compression='safe',
                                  cacheable=True, REQUEST=None,
                                  conditionalcomment='', authenticated=False,
                                  applyPrefix=False, bundle='default'):
        """Register a sassystylesheet from a TTW request."""
        self.registerSassyStylesheet(id, expression, media, rel, title,
                                     rendering, enabled, cookable, compression,
                                     cacheable, conditionalcomment, authenticated,
                                     applyPrefix=applyPrefix, bundle=bundle)

        if REQUEST:
            REQUEST.RESPONSE.redirct(REQUEST['HTTP_REFERER'])

    security.declareProtected(permissions.ManagePortal, 'manage_saveSassyStylesheets')
    def manage_saveSassyStylesheets(self, REQUEST=None):
        """Save sassystylesheets from ZMI.

        Updates the whole sequence. For editing and reordering.
        """
        debugmode = REQUEST.get('debugmode', False)
        self.setDebugMode(debugmode)
        records = REQUEST.get('sassystylesheets', [])
        records.sort(lambda a, b: a.sort - b.sort)
        self.resources = ()
        sassystylesheets = []
        for r in records:
            scss = self.resource_class(
                r.get('id'),
                expression=r.get('expression', ''),
                media=r.get('media', 'screen'),
                rel=r.get('rel', 'stylesheet'),
                title=r.get('title', ''),
                rendering=r.get('rendering', 'link'),
                enabled=r.get('enabled', True),
                cookable=r.get('cookable', False),
                cacheable=r.get('cacheable', True),
                compression=r.get('compression', 'safe'),
                conditionalcomment=r.get('conditionalcomment',''),
                authenticated=r.get('authenticated', False),
                applyPrefix=r.get('applyPrefix', False),
                bundle=r.get('bundle', 'default'))
            sassystylesheets.append(scss)
        self.resources = tuple(sassystylesheets)
        self.cookResources()
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(permissions.ManagePortal, 'manage_removeSassyStylesheet')
    def manage_removeSassyStylesheet(self, id, REQUEST=None):
        """Remove sassystylesheet from the ZMI."""
        self.unregisterResource(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    #
    # Protected Methods
    #

    security.declareProtected(permissions.ManagePortal, 'registerSassyStylesheet')
    def registerSassyStylesheet(self, id, expression='', media='screen',
                                rel='stylesheet', title='', rendering='link',
                                enabled=1, cookable=True, compression='safe',
                                cacheable=True, conditionalcomment='',
                                authenticated=False, skipCooking=False,
                                applyPrefix=False, bundle='default'):
        """Register a sassystylesheet."""
        sassystylesheet = self.resource_class(
            id,
            expression=expression,
            media=media,
            rel=rel,
            title=title,
            rendering=rendering,
            enabled=enabled,
            cookable=cookable,
            compression=compression,
            cacheable=cacheable,
            conditionalcomment=conditionalcomment,
            authenticated=authenticated,
            applyPrefix=applyPrefix,
            bundle=bundle)
        self.storeResource(sassystylesheet, skipCooking=skipCooking)

    security.declareProtected(permissions.ManagePortal, 'updateSassyStylesheet')
    def updateSassyStylesheet(self, id, **data):
        sassystylesheet = self.resourcesDict().get(id, None)
        if sassystylesheet is None:
            raise ValueError('Invalid Resource id %s' % (id,))

        if data.get('expression', None) is not None:
            sassystylesheet.setExpression(data['expression'])
        if data.get('authenticated', None) is not None:
            sassystylesheet.setAuthenticated(data['authenticated'])
        if data.get('media', None) is not None:
            sassystylesheet.setMedia(data['media'])
        if data.get('rel', None) is not None:
            sassystylesheet.setRel(data['rel'])
        if data.get('title', None) is not None:
            sassystylesheet.setTitle(data['title'])
        if data.get('rendering', None) is not None:
            sassystylesheet.setRendering(data['rendering'])
        if data.get('enabled', None) is not None:
            sassystylesheet.setEnabled(data['enabled'])
        if data.get('cookable', None) is not None:
            sassystylesheet.setCookable(data['cookable'])
        if data.get('compression', None) is not None:
            sassystylesheet.setCompression(data['compression'])
        if data.get('cacheable', None) is not None:
            sassystylesheet.setCacheable(data['cacheable'])
        if data.get('conditionalcomment',None) is not None:
            sassystylesheet.setConditionalcomment(data['conditionalcomment'])
        if data.get('applyPrefix',None) is not None:
            sassystylesheet.setApplyPrefix(data['applyPrefix'])
        if data.get('bundle', None) is not None:
            sassystylesheet.setBundle(data['bundle'])

    security.declareProtected(permissions.ManagePortal, 'getCompressionOptions')
    def getCompressionOptions(self):
        """Compression methods for use in ZMI forms."""
        return CSS_COMPRESSION_METHODS

    security.declareProtected(permissions.ManagePortal, 'getExternalCompressionOptions')
    def getExternalCompressionOptions(self):
        """Compression methods for use in ZMI forms."""
        return CSS_COMPRESSION_METHODS

    security.declareProtected(permissions.ManagePortal, 'getContentType')
    def getContentType(self):
        """Return the registry content type."""
        return 'text/css;charset=utf-8'


InitializeClass(SCSSRegistryTool)
