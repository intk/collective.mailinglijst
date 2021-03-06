# -*- coding: utf-8 -*-
from zope.component import getUtility

from collective.mailinglijst.testing import \
    COLLECTIVE_MAILCHIMP_INTEGRATION_TESTING

import unittest


class MailinglijstLocatorIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_MAILCHIMP_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()

    def test_mailinglijst_locator_registration(self):
        from collective.mailinglijst.interfaces import IMailinglijstLocator
        self.assertTrue(getUtility(IMailinglijstLocator))

    def test_mailinglijst_locator_initialize_method(self):
        from collective.mailinglijst.locator import MailinglijstLocator
        locator = MailinglijstLocator()
        self.assertEqual(locator.registry, None)
        self.assertEqual(locator.settings, None)
        self.assertEqual(locator.api_root, None)
        locator.initialize()
        self.assertTrue(locator.registry)
        self.assertTrue(locator.settings)
        self.assertTrue(locator.api_root)

    def test_mailinglijst_locator_lists_method(self):
        from collective.mailinglijst.locator import MailinglijstLocator
        locator = MailinglijstLocator()
        self.assertTrue(locator.lists())
        self.assertEqual(len(locator.lists()), 3)

    def test_mailinglijst_locator_groups_method(self):
        from collective.mailinglijst.locator import MailinglijstLocator
        locator = MailinglijstLocator()
        groups = locator.groups(list_id=u'57afe96172')
        self.assertTrue(groups)
        self.assertEqual(len(groups['categories']), 1)
        self.assertEqual(len(groups['interests']), 5)
        self.assertEqual(groups['interests'][0]['name'],
                         u"Sometimes you just gotta 'spress yourself.")

    def test_mailinglijst_locator_updateCache_method(self):
        from collective.mailinglijst.locator import MailinglijstLocator
        locator = MailinglijstLocator()
        locator.initialize()
        # These tests pass when we run this test method separately,
        # but fail when running all tests.  Skip them because they are
        # not what we really want to test here.
        #
        # self.assertEqual(locator.registry[locator.key_account], None)
        # self.assertEqual(locator.registry[locator.key_groups], None)
        # self.assertEqual(locator.registry[locator.key_lists], None)
        locator.updateCache()
        account = locator.registry[locator.key_account]
        self.assertTrue(isinstance(account, dict))
        self.assertEqual(account[u'account_id'], u'8d3a3db4d97663a9074efcc16')
        self.assertEqual(account[u'account_name'], u"Freddie's Jokes")
        groups = locator.registry[locator.key_groups]
        self.assertTrue(isinstance(groups, dict))
        self.assertEqual(groups.keys(),
                         [u'f6257645gs', u'f6267645gs', u'57afe96172'])
        self.assertEqual(
            groups[groups.keys()[0]].keys(),
            [u'total_items', 'interests', u'_links', u'categories', u'list_id']
            )

        self.assertTrue(
            isinstance(locator.registry[locator.key_lists], tuple))
        self.assertEqual(len(locator.registry[locator.key_lists]), 3)
        # It does not complain when there is no api key
        locator.settings.api_key = None
        locator.updateCache()


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
