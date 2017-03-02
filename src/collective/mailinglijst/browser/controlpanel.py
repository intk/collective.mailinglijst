from zope.interface import Invalid
from z3c.form.interfaces import WidgetActionExecutionError
from zope.component import getUtility
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ..exceptions import (
    PostRequestError,
    MailinglijstException
)

from plone.app.registry.browser import controlpanel
try:
    from plone.protect.interfaces import IDisableCSRFProtection
except ImportError:
    # BBB for old plone.protect, default until at least Plone 4.3.7.
    IDisableCSRFProtection = None
from zope.interface import alsoProvides

from collective.mailinglijst.interfaces import IMailinglijstSettings
from collective.mailinglijst.interfaces import IMailinglijstLocator
from collective.mailinglijst import _


class MailinglijstSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IMailinglijstSettings
    label = _(u"Mailinglijst settings")
    description = _(u"""""")

    def update(self):
        self.updateCache()
        super(MailinglijstSettingsEditForm, self).update()

    def updateFields(self):
        super(MailinglijstSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(MailinglijstSettingsEditForm, self).updateWidgets()

    def updateCache(self):
        mailinglijst = getUtility(IMailinglijstLocator)
        mailinglijst.updateCache()


class MailinglijstSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = MailinglijstSettingsEditForm
    index = ViewPageTemplateFile('controlpanel.pt')

    def mailinglijst_account(self):
        if IDisableCSRFProtection is not None:
            alsoProvides(self.request, IDisableCSRFProtection)
        mailinglijst = getUtility(IMailinglijstLocator)
        try:
            return mailinglijst.account()
        except PostRequestError:
            return []
        except MailinglijstException, error:
            raise WidgetActionExecutionError(
                Invalid(
                    u"Could not fetch account details from Mailinglijst. " +
                    u"Please check your Mailinglijst API key: %s" % error
                )
            )

    """def available_lists(self):
        if IDisableCSRFProtection is not None:
            alsoProvides(self.request, IDisableCSRFProtection)
        mailinglijst = getUtility(IMailinglijstLocator)
        try:
            return mailinglijst.lists()
        except MailinglijstException, error:
            raise WidgetActionExecutionError(
                Invalid(
                    u"Could not fetch available lists from Mailinglijst. " +
                    u"Please check your Mailinglijst API key: %s" % error
                )
            )"""
