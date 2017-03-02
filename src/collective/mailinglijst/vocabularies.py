
from zope.component import getUtility
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from collective.mailinglijst.interfaces import IMailinglijstLocator


def available_lists(context):
    mailinglijst = getUtility(IMailinglijstLocator)
    lists = mailinglijst.lists()
    if not lists:
        return SimpleVocabulary([])
    return SimpleVocabulary([
        SimpleTerm(value=li['id'], title=li['name']) for li in lists]
    )


def interest_groups(context):
    mailinglijst = getUtility(IMailinglijstLocator)
    if 'list_id' in context.REQUEST:
        # list_id URL parameter
        list_id = context.REQUEST['list_id']
    elif 'form.widgets.list_id' in context.REQUEST.form:
        # list_id form parameter
        list_id = context.REQUEST.form['form.widgets.list_id']
    else:
        # If no id param has been provided just take the first list.
        list_id = mailinglijst.default_list_id()
        if not list_id:
            return SimpleVocabulary([])
    groups = mailinglijst.groups(list_id=list_id)
    if not groups:
        return SimpleVocabulary([])
    # Each category has a list of options/groups/interests.  We only support
    # one interest category per list.  We take the first one.  We have stored
    # this in the interests key.
    interests = groups.get('interests')
    if not interests:
        return SimpleVocabulary([])
    return SimpleVocabulary([
        SimpleTerm(
            value=group['id'].encode("utf-8"),
            title=group['name']
        ) for group in interests
    ])"""


def email_type(context):
    terms = []
    terms.append(
        SimpleTerm(
            value='text',
            token='text',
            title='Plain text',
        )
    )
    terms.append(
        SimpleTerm(
            value='html',
            token='html',
            title='HTML',
        )
    )
    return SimpleVocabulary(terms)



