# -*- coding: utf-8 -*-

from bibliotheca.core.testing import BIBLIOTHECA_CORE_INTEGRATION_TESTING
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestVocabularies(unittest.TestCase):
    layer = BIBLIOTHECA_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def vocabulary(self, name):
        # Look the vocabulary up by the name used in the content schemas
        # to also check the ZCML registration.
        factory = getUtility(
            IVocabularyFactory, name=f"bibliotheca.core.vocabularies.{name}"
        )
        return factory(self.portal)

    def titles(self, vocabulary):
        return {term.value: term.title for term in vocabulary}

    def test_colors(self):
        self.assertEqual(
            self.titles(self.vocabulary("colors_vocabulary")),
            {"couleur": "Couleur", "noiretbanc": "Noir & Blanc"},
        )

    def test_eventsdate(self):
        self.assertEqual(
            self.titles(self.vocabulary("eventsdate_vocabulary")),
            {"Naissance": "Naissance", "Mariage": "Mariage", "Deces": "Décès"},
        )

    def test_provinces(self):
        self.assertEqual(
            self.titles(self.vocabulary("provinces_vocabulary")),
            {
                "brabantwallon": "Brabant wallon",
                "hainaut": "Hainaut",
                "liege": "Liège",
                "luxembourg": "Luxembourg",
                "namur": "Namur",
            },
        )

    def test_municipal_entities(self):
        vocabulary = self.vocabulary("municipalentities_vocabulary")
        # The 262 Walloon municipalities, each listed once.
        self.assertEqual(len(vocabulary), 262)
        self.assertEqual(len(set(self.titles(vocabulary).values())), 262)
        term = vocabulary.getTermByToken("courtsaintetienne")
        self.assertEqual(term.value, "courtsaintetienne")
        self.assertEqual(term.title, "Court-Saint-Étienne")
        self.assertIn("liege", vocabulary)
        self.assertNotIn("bruxelles", vocabulary)
