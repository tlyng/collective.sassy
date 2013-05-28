# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.sassy.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of collective.sassy into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.sassy is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.sassy'))

    def test_uninstall(self):
        """Test if collective.sassy is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.sassy'])
        self.assertFalse(self.installer.isProductInstalled('collective.sassy'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveSassyLayer is registered."""
        from collective.sassy.interfaces import ICollectiveSassyLayer
        from plone.browserlayer import utils
        self.failUnless(ICollectiveSassyLayer in utils.registered_layers())
