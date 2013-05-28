# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.sassy.testing import IntegrationTestCase
from Products.CMFCore.utils import getToolByName


class TestInstall(IntegrationTestCase):
    """Test installation of collective.sassy into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.sassy is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.sassy'))

    def test_uninstall(self):
        """Test if collective.sassy is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.sassy'])
        self.assertFalse(self.installer.isProductInstalled('collective.sassy'))

    def test_tool_installed(self):
        tool = getToolByName(self.portal, 'portal_scss')
        self.assertTrue(tool != None)

    def test_debug(self):
        tool = getToolByName(self.portal, 'portal_scss')
        context = self.portal
        resources = tool.getEvaluatedResources(context)
        import pdb; pdb.set_trace( )
