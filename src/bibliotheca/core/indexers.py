# -*- coding: utf-8 -*-
from bibliotheca.core.commentextender import ICommentExtenderFields
from plone.app.discussion.interfaces import IComment
from plone.indexer import indexer


@indexer(IComment)
def comment_picture_indexer(obj):
    # Récupérer l'objet étendu contenant le champ picture
    extender = ICommentExtenderFields(obj, None)
    if extender and extender.picture:
        return extender.picture
    return None
