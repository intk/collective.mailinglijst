# -*- coding: utf-8 -*-
import json
import logging
import requests
from urllib import quote
try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse
from collective.mailinglijst.interfaces import IMailinglijstSettings
from collective.mailinglijst.interfaces import IMailinglijstLocator
from plone.registry.interfaces import IRegistry
from zope.interface import implements
from zope.component import getUtility
from . exceptions import (
    SerializationError,
    DeserializationError,
    PostRequestError,
    MailinglijstException,
)

from .serializers import xml_deserialize

_marker = object()
logger = logging.getLogger('collective.mailinglijst')

LIST_ID = '3679'
LIST_NAME = "Mondriaanhuis"

class MailinglijstLocator(object):
    """Utility for Mailinglijst API calls.
    """

    implements(IMailinglijstLocator)
    key_account = "collective.mailinglijst.cache.account"
    key_lists = "collective.mailinglijst.cache.lists"

    def __init__(self, settings={}):
        """ Use settings if provided """
        self.registry = None
        self.settings = None
        self.api_root = None
        if settings:
            self.settings = settings

    def initialize(self):
        """ Load settings from registry and construct api root"""
        if self.registry is None:
            self.registry = getUtility(IRegistry)
        if self.settings is None:
            self.settings = self.registry.forInterface(IMailinglijstSettings)

        self.apikey = self.settings.api_key
        if not self.apikey:
            return
        parts = self.apikey.split('-')
        if not len(parts) > 1:
            # bad api key, allow to fix
            return

        self.api_root = "https://mailinglijst.nl/api"

    def _serialize_payload(self, payload):
        params = self.params.copy()
        params.update(payload)
        try:
            jsonstr = json.dumps(params)
            serialized = quote(jsonstr)
            return serialized
        except TypeError:
            raise SerializationError(payload)

    def _deserialize_response(self, text):
        """ Attempt to deserialize a JSON response from the server."""
        try:
            deserialized = xml_deserialize(text.encode('utf-8'))
        except ValueError:
            raise DeserializationError(text)
        
        #self._fail_if_mailinglijst_exc(deserialized)
        return deserialized

    def api_request(self, request_type='get', **kwargs):
        """ construct the request and do a get/post.
        """
        if not self.api_root:
            return []

        headers = {}
        url = urlparse.urljoin(self.api_root, '')

        # we provide a json structure with the parameters.
        payload = kwargs
        if request_type.lower() == 'post':
            request_method = requests.post
        else:
            request_method = requests.get
        try:
            resp = request_method(url, params=payload)
        except Exception, e:
            raise PostRequestError(e)

        decoded = self._deserialize_response(resp.text)

        return decoded

    def default_list_id(self):
        """ returns the first item in the list """
        """self.initialize()
        if self.settings.default_list:
            return self.settings.default_list
        lists = self.lists()
        if len(lists) > 0:
            return lists[0]['id']"""

        return LIST_ID
        

    def subscribe(self, list_id, email_address, **kwargs):
        """ API call to subscribe a member to a list. """
        self.initialize()
        
        opt_in_status = '1'
        if self.settings.double_optin:
            opt_in_status = '0'

        """if not email_type:
            email_type = self.settings.email_type"""
        
        endpoint = ''
        
        try:
            response = self.api_request(request_type='get',
                                        action="SUBSCRIBE",
                                        optin=opt_in_status,
                                        e=email_address,
                                        l=list_id,
                                        key=self.apikey,
                                        **kwargs)
        except MailinglijstException:
            raise
        except Exception, e:
            raise PostRequestError(e)

        api_resp = response['api']
        
        try:
            description = self.find_param('description', api_resp)
        except:
            description = ""

        if 'already member' in description:
            raise MailinglijstException(400, 'Already member of the list.', '')
        
        logger.info("Subscribed %s to list with id: %s." %
                    (email_address, list_id))
        logger.debug("Subscribed %s to list with id: %s.\n\n %s" %
                     (email_address, list_id, response))
        
        return response

    def find_param(self, param_name, list_params):
        for param in list_params:
            if param_name in param:
                return param[param_name][0]
        return ''

    def account(self):
        """ Get account details. This is cached as well """
        self.initialize()
        cache = self.registry.get(self.key_account, _marker)
        if cache and cache is not _marker:
            return cache
        return self._account()

    def _account(self):
        """ Actual API call to mailinglijsts api root.
        """
        try:
            return self.api_request(action="GET", key=self.apikey)
        except MailinglijstException:
            logger.exception("Exception getting account details.")
            return None


    """
    Not necessary
    """

    def lists(self):
        """ API list call. To lower the amount of requests we use a cache
            If the cache is empty we fetch it once from the Mailinglijst API.
        """

        """self.initialize()
        cache = self.registry.get(self.key_lists, _marker)
        if cache and cache is not _marker:
            return cache

        """
        return self._lists()
        
    def _lists(self):
        """
        try:
            # lists returns a dict with 'total' and 'data'. we just need data
            response = self.api_request('lists')
        except PostRequestError:
            return []
        if 'lists' in response:
            return response['lists']"""
        return [{'name': LIST_NAME, 'id': LIST_ID}]

    def groups(self, list_id=None):
        """ API call for interest-categories. This is also cached. """
        return []

        """
        if not list_id:
            return
        self.initialize()
        cache = self.registry.get(self.key_groups, _marker)
        if cache and cache is not _marker:
            groups = cache.get(list_id, _marker)
            if groups and groups is not _marker:
                return groups
        return self._groupings(list_id)"""


    def _groupings(self, list_id=None):
        return []

        """
        # Return combined list of interest categories with their group options.
        # We only support one interest category per list.
        # We take the top one.
        categories = self._interest_categories(list_id)
        if not categories or not categories['categories']:
            return categories
        # We could search for the category with the highest display_order key,
        # but for a test list I made, this was zero in both interest
        # categories...  So just take the first one.
        category = categories['categories'][0]
        category_id = category.get('id')
        interests = self._interests(list_id, category_id)
        categories['interests'] = interests.get('interests', [])
        return categories"""

    def _interest_categories(self, list_id=None):
        """API call to Mailinglijst to get interest categories.
        """

        """
        if not list_id:
            return
        url = 'lists/' + list_id + '/interest-categories'
        try:
            return self.api_request(url)
        except MailinglijstException:
            raise"""

        return

    def _interests(self, list_id=None, interest_category_id=None):
        """Actual API call to Mailinglijst service to get the group options.

        In api 1.3 this was given immediately with the list of interest
        categories.  In api 3.0 we need to get each interest category
        and ask for its interests/groups.
        """
        """if not list_id or not interest_category_id:
            return
        url = 'lists/{0}/interest-categories/{1}/interests'.format(
            list_id, interest_category_id)
        try:
            return self.api_request(url)
        except MailinglijstException:
            raise"""

        return

    def updateCache(self):
        """ Update cache of data from the mailinglijst server.  First reset
            our mailinglijst object, as the user may have picked a
            different api key.  Alternatively, compare
            self.settings.api_key and self.mailinglijst.apikey.
            Connecting will recreate the mailinglijst object.
        """
        
        """self.initialize()
        if not self.settings.api_key:
            return
        # Note that we must call the _underscore methods.  These
        # bypass the cache and go directly to mailinglijst, so we are
        # certain to have up to date information.
        account = self._account()
        groups = {}
        lists = self._lists()
        for mailinglijst_list in lists:
            list_id = mailinglijst_list['id']
            groups[list_id] = self._groupings(list_id=list_id)

        # Now save this to the registry, but only if there are
        # changes, otherwise we would do a commit every time we look
        # at the control panel.
        if type(account) is dict:
            if self.registry[self.key_account] != account:
                self.registry[self.key_account] = account
        if type(groups) is dict:
            if self.registry[self.key_groups] != groups:
                self.registry[self.key_groups] = groups
        if type(lists) is list:
            lists = tuple(lists)
            if self.registry[self.key_lists] != lists:
                # Note that unfortunately this happens far too often.
                # In the 'subscribe_url_long' key of an item you can
                # easily first see:
                # 'http://edata.us3.list-manage.com/subscribe?u=abc123',
                # and a second later:
                # 'http://edata.us3.list-manage1.com/subscribe?u=abc123',
                self.registry[self.key_lists] = lists"""
        pass


    """def _fail_if_mailinglijst_exc(self, response):
        # case: response is not a dict so it cannot be an error response
        if not isinstance(response, dict):
            return
        # case: response is a dict and may be an error response
        elif 'status' in response and 'detail' in response:
            exc = MailinglijstException(
                response['status'], response['detail'], response.get('errors'))
            logger.warn(exc)
            raise exc"""

