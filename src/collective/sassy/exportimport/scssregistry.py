from collective.sassy.interfaces import ISCSSRegistry

from Products.ResourceRegistries.exportimport.resourceregistry import \
    ResourceRegistryNodeAdapter, importResRegistry, exportResRegistry


_FILENAME = 'scssregistry.xml'
_REG_ID = 'portal_scss'
_REG_TITLE = 'SCSS Stylesheet registry'


def importSCSSRegistry(context):
    """
    Import SCSS registry
    """
    return importResRegistry(context, _REG_ID, _REG_TITLE, _FILENAME)


def exportSCSSRegistry(context):
    """
    Export SCSS registry
    """
    return exportResRegistry(context, _REG_ID, _REG_TITLE, _FILENAME)


class SCSSRegistryNodeAdapter(ResourceRegistryNodeAdapter):
    """
    Node importer and exporter for SCSSRegistry.
    """

    __used_for__ = ISCSSRegistry
    registry_id = _REG_ID
    resource_type = 'sassystylesheet'
    register_method = 'registerSassyStylesheet'
    update_method = 'updateSassyStylesheet'
