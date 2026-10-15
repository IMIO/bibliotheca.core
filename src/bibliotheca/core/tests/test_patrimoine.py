# -*- coding: utf-8 -*-
from bibliotheca.core.content.patrimoine import fileSize
from bibliotheca.core.content.patrimoine import InvalidFileSizeError
from bibliotheca.core.interfaces import IBibliothecaCoreLayer
from bibliotheca.core.testing import BIBLIOTHECA_CORE_INTEGRATION_TESTING
from bibliotheca.core.upgrades.upgrades import reindex_patrimoine_searchable_text
from collective.geolocationbehavior.geolocation import IGeolocatable
from collective.taxonomy import generated
from collective.taxonomy.factory import registerTaxonomy
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.dexterity.schema import SchemaInvalidatedEvent
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.field import NamedFile
from plone.namedfile.file import NamedBlobFile
from zope.event import notify
from zope.interface import alsoProvides

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


class TestPatrimoineSearch(unittest.TestCase):
    layer = BIBLIOTHECA_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def create(self, **fields):
        return api.content.create(
            container=self.portal,
            type="patrimoine",
            title="Patrimoine",
            **fields,
        )

    def find(self, text):
        return [brain.getObject() for brain in api.content.find(SearchableText=text)]

    def add_villages_taxonomy(self):
        # Without the taxonomy, collective.taxonomy generates and keeps an
        # empty "villages" schema: drop it before and after the test.
        self.drop_generated_villages_schema()
        self.addCleanup(self.drop_generated_villages_schema)
        taxonomy = registerTaxonomy(
            self.portal, name="villages", title="Villages", default_language="fr"
        )
        taxonomy.registerBehavior(
            field_title="Villages", field_description="", default_language="fr"
        )
        taxonomy.add("fr", "bouge-id", "/Bouge")

    def drop_generated_villages_schema(self):
        delattr(generated, "villages")
        notify(SchemaInvalidatedEvent("patrimoine"))

    def test_find_by_text_field(self):
        patrimoine = self.create(nature_du_bien="Calvaire")
        self.assertEqual(self.find("Calvaire"), [patrimoine])

    def test_owner_data_not_searchable(self):
        # The owner data is hidden from visitors: the search must not reveal
        # which patrimoine belongs to a person.
        self.create(
            owner_name="Jean Dupont",
            owner_email="jean.dupont@example.org",
            owner_phone="0471123456",
        )
        self.assertEqual(self.find("Dupont"), [])
        self.assertEqual(self.find("jean.dupont@example.org"), [])
        self.assertEqual(self.find("0471123456"), [])

    def test_upgrade_reindexes_searchable_text(self):
        patrimoine = self.create()
        patrimoine.nature_du_bien = "Calvaire"
        self.assertEqual(self.find("Calvaire"), [])
        reindex_patrimoine_searchable_text(self.portal.portal_setup)
        self.assertEqual(self.find("Calvaire"), [patrimoine])

    def test_find_by_rich_text_without_html(self):
        patrimoine = self.create(
            informations=RichTextValue(
                "<p>Chapelle <strong>romane</strong></p>", "text/html", "text/html"
            )
        )
        self.assertEqual(self.find("romane"), [patrimoine])
        self.assertEqual(self.find("strong"), [])

    def test_find_by_subject(self):
        patrimoine = self.create(subject=("vitrail",))
        self.assertEqual(self.find("vitrail"), [patrimoine])

    def test_find_by_taxonomy_term_caption(self):
        # The patrimoine type uses the "villages" taxonomy behavior: the
        # caption of the term is indexed, not its identifier.
        self.add_villages_taxonomy()
        patrimoine = self.create(taxonomy_villages=["bouge-id"])
        self.assertEqual(self.find("Bouge"), [patrimoine])
        self.assertEqual(self.find("bouge-id"), [])


class TestPatrimoineView(unittest.TestCase):
    layer = BIBLIOTHECA_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.request, IBibliothecaCoreLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.patrimoine = api.content.create(
            container=self.portal, type="patrimoine", title="Patrimoine"
        )

    def render(self):
        # plone.autoform only checks the read permissions of the fields
        # when the request has an authenticated user, as in production.
        self.request["AUTHENTICATED_USER"] = api.user.get_current()
        return self.patrimoine.restrictedTraverse("@@view")()

    def login_as_visitor(self):
        api.user.create(
            email="visitor@example.org", username="visitor", password="secret12345"
        )
        api.user.grant_roles(username="visitor", obj=self.patrimoine, roles=["Reader"])
        login(self.portal, "visitor")

    def test_owner_data_visible_to_editors(self):
        self.patrimoine.owner_name = "Jean Dupont"
        self.patrimoine.owner_email = "jean.dupont@example.org"
        html = self.render()
        self.assertIn("Jean Dupont", html)
        self.assertIn("jean.dupont@example.org", html)

    def test_owner_data_hidden_from_visitors(self):
        self.patrimoine.owner_datas = "Privé"
        self.patrimoine.owner_name = "Jean Dupont"
        self.patrimoine.owner_email = "jean.dupont@example.org"
        self.login_as_visitor()
        html = self.render()
        self.assertNotIn("Jean Dupont", html)
        self.assertNotIn("jean.dupont@example.org", html)
        self.assertNotIn("Données relatives au propriétaire", html)

    def test_section_title_only_when_the_next_field_has_a_value(self):
        self.assertNotIn("Identification de l’élément", self.render())
        self.patrimoine.nature_du_bien = "Calvaire"
        self.assertIn("Identification de l’élément", self.render())

    def test_fieldset_legend_only_when_a_field_has_a_value(self):
        self.assertNotIn("<legend>Publication</legend>", self.render())
        self.patrimoine.auteur = "Victor Hugo"
        html = self.render()
        self.assertIn("<legend>Publication</legend>", html)
        self.assertIn("Victor Hugo", html)

    def test_pdf_only_when_there_is_a_file(self):
        self.assertNotIn('id="form-widgets-fichier_pdf"', self.render())
        self.patrimoine.fichier_pdf = NamedBlobFile(
            data=b"%PDF-1.4", filename="notice.pdf"
        )
        self.assertIn('id="form-widgets-fichier_pdf"', self.render())

    def test_coordinates_only_when_geolocated(self):
        self.assertNotIn("Coordinates", self.render())
        IGeolocatable(self.patrimoine).geolocation = Geolocation(
            latitude="50.4669", longitude="4.8675"
        )
        html = self.render()
        self.assertIn("Coordinates", html)
        self.assertIn("50.4669", html)
