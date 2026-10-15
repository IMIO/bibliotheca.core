# -*- coding: utf-8 -*-
from bibliotheca.core.content.patrimoine import fileSize
from bibliotheca.core.content.patrimoine import InvalidFileSizeError
from bibliotheca.core.testing import BIBLIOTHECA_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.field import NamedFile
from plone.namedfile.file import NamedBlobFile

import unittest


class TestPatrimoine(unittest.TestCase):
    layer = BIBLIOTHECA_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.patrimoine = api.content.create(
            container=self.portal, type="patrimoine", title="Patrimoine"
        )

    def test_filesize(self):
        # original value in patrimoine : 30000000
        file = NamedFile()
        file.data = "0" * 30000000
        self.patrimoine.fichier_pdf = NamedBlobFile(
            data=file.data, filename="bigfile.pdf"
        )
        self.assertTrue(fileSize(self.patrimoine.fichier_pdf))
        file = NamedFile()
        file.data = "0" * 30000001
        self.patrimoine.fichier_pdf = NamedBlobFile(
            data=file.data, filename="bigfile.pdf"
        )
        with self.assertRaises(InvalidFileSizeError):
            self.assertRaises(
                InvalidFileSizeError, fileSize(self.patrimoine.fichier_pdf)
            )
