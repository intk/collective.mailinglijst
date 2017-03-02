# -*- coding: utf-8 -*-


class SerializationError(Exception):
    """ Raised if a method call contains parameters that cannot be serialized to
    XML. The object that caused the error is made available via the ``obj``
    attribute.
    """

    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        return '%s could not be serialized to json' % self.obj


class DeserializationError(Exception):
    """ Raised if Mailinglijst responds with anything other than valid XML.
    We use Mailinglijst's XML API exclusively so it is unlikely
    that this will be raised. The response that caused the error is
    made available via the ``obj`` attribute.
    """

    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        return '%s could not be deserialized' % self.obj


class PostRequestError(Exception):
    """ If any exception is made during the POST request to Mailinglijst's server,
    `PostRequestError` will be raised. It wraps the underlying exception
    object and makes it available via the ``exc`` attribute.
    """

    def __init__(self, exc):
        self.exc = exc

    def __str__(self):
        return 'Caught exc "%s" with error "%s"' % (type(self.exc), self.exc)


class MailinglijstException(Exception):
    """ If Mailinglijst returns an exception code as part of their response,
    this exception will be raised. Contains the unmodified ``code`` (int) and
    ``error`` (unicode) attributes returned by Mailinglijst.
    """

    def __init__(self, code, detail, errors=''):
        self.code = code
        self.detail = detail
        self.errors = errors

    def __str__(self):
        return 'Mailinglijst error code {0}: "{1}"\n{2}'.format(
            self.code, self.detail, self.errors)

        
