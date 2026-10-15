# -*- coding: utf-8 -*-

from bibliotheca.core.commentextender import CommentExtenderFields
from bibliotheca.core.commentextender import ICommentExtenderFields
from bibliotheca.core.indexers import comment_picture_indexer
from bibliotheca.core.testing import BIBLIOTHECA_CORE_INTEGRATION_TESTING
from plone.app.discussion.comment import Comment
from zope.component import getGlobalSiteManager

import unittest


class TestCommentPictureIndexer(unittest.TestCase):
    layer = BIBLIOTHECA_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.comment = Comment()

    def index(self):
        return comment_picture_indexer(self.comment)()

    def register_extender(self):
        # The ICommentExtenderFields adapter is disabled in configure.zcml:
        # register it for the duration of the test only.
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(CommentExtenderFields, (Comment,), ICommentExtenderFields)
        self.addCleanup(
            gsm.unregisterAdapter,
            CommentExtenderFields,
            (Comment,),
            ICommentExtenderFields,
        )

    def test_none_without_extender(self):
        self.assertIsNone(self.index())

    def test_none_without_picture(self):
        self.register_extender()
        self.comment.picture = None
        self.assertIsNone(self.index())

    def test_returns_picture(self):
        self.register_extender()
        picture = object()
        self.comment.picture = picture
        self.assertIs(self.index(), picture)
