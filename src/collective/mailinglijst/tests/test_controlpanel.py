from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from plone.registry import Registry

from plone.app.testing import logout

from collective.mailinglijst.testing import \
    COLLECTIVE_MAILCHIMP_INTEGRATION_TESTING

from collective.mailinglijst.interfaces import IMailinglijstSettings

import unittest


class TestMailinglijstSettingsControlPanel(unittest.TestCase):

    layer = COLLECTIVE_MAILCHIMP_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = Registry()
        self.registry.registerInterface(IMailinglijstSettings)

    def test_mailinglijst_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="mailinglijst-settings")
        view = view.__of__(self.portal)
        self.failUnless(view())

    def test_mailinglijst_controlpanel_view_protected(self):
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(
            Unauthorized,
            self.portal.restrictedTraverse,
            '@@mailinglijst-settings'
        )

    def test_mailinglijst_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.failUnless(
            'mailinglijst' in [
                a.getAction(self)['id']
                for a in self.controlpanel.listActions()
            ]
        )

    def test_record_api_key(self):
        record = self.registry.records[
            'collective.mailinglijst.interfaces.IMailinglijstSettings.api_key']
        self.failUnless('api_key' in IMailinglijstSettings)
        self.assertEquals(record.value, u"")


class ControlpanelFunctionalTest(unittest.TestCase):

    layer = COLLECTIVE_MAILCHIMP_INTEGRATION_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

    def test_empty_form(self):
        self.browser.open("%s/mailinglijst-settings" % self.portal_url)
        self.assertTrue("Mailinglijst settings" in self.browser.contents)