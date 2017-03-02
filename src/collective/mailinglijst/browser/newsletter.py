# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from zope.interface import Invalid
from zope.interface import implements
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component.hooks import getSite
from zope.component import getUtility

from z3c.form import form, field, button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.interfaces import ActionExecutionError
from z3c.form.interfaces import WidgetActionExecutionError
from z3c.form.interfaces import HIDDEN_MODE

from plone.registry.interfaces import IRegistry
from plone.z3cform.layout import wrap_form
from plone.z3cform.fieldsets import extensible

from collective.mailinglijst import _
from collective.mailinglijst.exceptions import MailinglijstException
from collective.mailinglijst.interfaces import IMailinglijstLocator
from collective.mailinglijst.interfaces import IMailinglijstSettings
from collective.mailinglijst.interfaces import INewsletterSubscribe


class NewsletterSubcriber(object):
    implements(INewsletterSubscribe, IAttributeAnnotatable)
    title = u""


class NewsletterSubscriberForm(extensible.ExtensibleForm, form.Form):
    fields = field.Fields(INewsletterSubscribe)
    ignoreContext = True
    id = "newsletter-subscriber-form"
    label = _(u"Subscribe to newsletter")

    def updateActions(self):
        super(NewsletterSubscriberForm, self).updateActions()
        self.actions['subscribe'].addClass('context')

    def updateFields(self):
        super(NewsletterSubscriberForm, self).updateFields()
        
        """self.fields['email_type'].widgetFactory = \
            RadioFieldWidget"""

    def updateWidgets(self):
        super(NewsletterSubscriberForm, self).updateWidgets()
        # Show/hide mail format option widget
        registry = getUtility(IRegistry)
        mailinglijst_settings = registry.forInterface(IMailinglijstSettings)
        
        """if not mailinglijst_settings.email_type_is_optional:
            self.widgets['email_type'].mode = HIDDEN_MODE"""
        # Retrieve the list id either from the request/form or fall back to
        # the default_list setting.
        if 'list_id' in self.context.REQUEST:
            list_id = self.context.REQUEST['list_id']
        elif 'form.widgets.list_id' in self.request.form:
            list_id = self.request.form['form.widgets.list_id']
        else:
            list_id = mailinglijst_settings.default_list

        self.widgets['list_id'].mode = HIDDEN_MODE
        self.widgets['list_id'].value = list_id


    @button.buttonAndHandler(_(u"subscribe_to_newsletter_button",
                               default=u"Subscribe"),
                             name='subscribe')
    def handleApply(self, action):
        data, errors = self.extractData()
        if 'email' not in data:
            return
        
        mailinglijst = getUtility(IMailinglijstLocator)
        # Retrieve list_id either from a hidden field in the form or fetch
        # the first list from mailinglijst.
        if 'list_id' in data and data['list_id'] is not None:
            list_id = data['list_id']
        else:
            list_id = mailinglijst.default_list_id()

        # Use email_type if one is provided by the form, if not choose the
        # default email type from the control panel settings.
        """if 'email_type' in data:
            email_type = data['email_type']
        else:
            email_type = 'HTML'"""
        
        # Subscribe to Mailinglijst list
        try:
            mailinglijst.subscribe(
                list_id=list_id,
                email_address=data['email']
            )
        except MailinglijstException as error:
            return self.handle_error(error, data)

        registry = getUtility(IRegistry)
        mailinglijst_settings = registry.forInterface(IMailinglijstSettings)
        
        if mailinglijst_settings.double_optin:
            message = _(
                u"We have to confirm your email address. In order to " +
                u"finish the newsletter subscription, click on the link " +
                u"inside the email we just send you.")
        else:
            message = _(
                u"You have been subscribed to our newsletter succesfully.")

        IStatusMessage(self.context.REQUEST).addStatusMessage(
            message, type="info")

        portal = getSite()
        self.request.response.redirect(portal.absolute_url())

    def handle_error(self, error, data):
        if error.code == 400:
            error_msg = _(
                u"mailinglijst_error_msg_already_subscribed",
                default=u"Could not subscribe to newsletter. "
                        u"Either the email '${email}' is already subscribed "
                        u"or something else is wrong. Try again later.",
                mapping={u"email": data['email']})
            translated_error_msg = self.context.translate(error_msg)
            raise WidgetActionExecutionError(
                'email',
                Invalid(translated_error_msg)
            )
        elif error.code == 220:
            error_msg = _(
                u"mailinglijst_error_msg_banned",
                default=u"Could not subscribe to newsletter. "
                        u"The email '${email}' has been banned.",
                mapping={u"email": data['email']})
            translated_error_msg = self.context.translate(error_msg)
            raise WidgetActionExecutionError(
                'email',
                Invalid(translated_error_msg)
            )
        else:
            error_msg = _(
                u"mailinglijst_error_msg",
                default=u"Could not subscribe to newsletter. "
                        u"Please contact the site administrator: "
                        u"'${error}'",
                mapping={u"error": error})
            translated_error_msg = self.context.translate(error_msg)
            raise ActionExecutionError(
                Invalid(translated_error_msg)
            )

NewsletterView = wrap_form(NewsletterSubscriberForm)
