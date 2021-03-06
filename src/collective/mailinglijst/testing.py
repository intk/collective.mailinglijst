import json
import os
import re
from collective.mailinglijst.interfaces import IMailinglijstSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from zope.configuration import xmlconfig
from mock import Mock
from mock import patch

DUMMY_API_KEY = u"abc-us1"
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'tests', 'data')


class MockRequestsException(Exception):
    """Exception raised in the requests mock.

    This makes it easier to distinguish between exceptions of the
    original and the patched module.
    """


class MockRequests(object):
    """Class used as mock replacement for the requests module.
    """

    @staticmethod
    def parse_arguments(*args, **kwargs):
        """Parse the arguments and return whatever we need.
        """
        if len(args) != 1:
            raise MockRequestsException(
                'Expected 1 argument, got {0}: {1}'.format(
                    len(args), args))
        # Check url
        url = args[0]
        mailinglijst_url = 'api.mailinglijst.com/3.0/'
        if mailinglijst_url not in url:
            raise MockRequestsException('Expected {0} in url {1}'.format(
                mailinglijst_url, url))
        endpoint = url.split(mailinglijst_url)[1]
        # Check auth
        auth = kwargs.get('auth')
        if not auth:
            raise MockRequestsException('Expected auth in keyword arguments.')
        expected_auth = ('apikey', DUMMY_API_KEY)
        if (not isinstance(auth, tuple) or len(auth) != 2 or
                expected_auth != auth):
            raise MockRequestsException(
                'Expected auth {0} in keyword arguments. Got {1}'.format(
                    expected_auth, auth))
        data = kwargs.get('data')
        # Load the data.
        if not data:
            raise MockRequestsException('Expected data in keyword arguments.')
        data = json.loads(data)
        if data:
            raise MockRequestsException('TODO: handle data.')
        return endpoint

    @staticmethod
    def post(*args, **kwargs):
        """This is a mock for post and get in the requests module.

        Return a json dictionary based on the end point.
        """
        endpoint = MockRequests.parse_arguments(*args, **kwargs)
        path = ''
        text = '{}'
        if not endpoint:
            path = os.path.join(TEST_DATA_DIR, 'account.json')
        elif endpoint == 'lists':
            path = os.path.join(
                TEST_DATA_DIR, 'lists.json')
        elif re.compile('lists/.*/interest-categories/.*/interests').match(
                endpoint):
            path = os.path.join(
                TEST_DATA_DIR, 'interests.json')
        elif re.compile('lists/.*/interest-categories').match(endpoint):
            path = os.path.join(
                TEST_DATA_DIR, 'lists_interest_categories.json')
        else:
            print('WARNING, unhandled endpoint in test: {0}'.format(endpoint))
        if path:
            with open(path) as datafile:
                text = datafile.read()
        # Return mock response with text.
        return Mock(text=text)

    get = post


class CollectiveMailinglijst(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Create patcher to mock the requests module that is imported in
        # locator.py only.
        self.requests_patcher = patch(
            'collective.mailinglijst.locator.requests', new_callable=MockRequests)
        # It looks like the patcher is started automatically, although the
        # documentation says you must start it explicitly.  Let's follow the
        # documentation.  Then we can also nicely stop it in tearDownZope.
        self.requests_patcher.start()

        # Load ZCML
        import collective.mailinglijst
        xmlconfig.file('configure.zcml',
                       collective.mailinglijst,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.mailinglijst:default')

        registry = getUtility(IRegistry)
        mailinglijst_settings = registry.forInterface(IMailinglijstSettings)
        mailinglijst_settings.api_key = DUMMY_API_KEY

    def tearDownZope(self, app):
        # Undo our requests patch.
        self.requests_patcher.stop()


COLLECTIVE_MAILCHIMP_FIXTURE = CollectiveMailinglijst()
COLLECTIVE_MAILCHIMP_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_MAILCHIMP_FIXTURE,),
    name="CollectiveMailinglijst:Integration")
COLLECTIVE_MAILCHIMP_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_MAILCHIMP_FIXTURE,),
    name="CollectiveMailinglijst:Functional")
