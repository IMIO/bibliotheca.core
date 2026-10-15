# -*- coding: utf-8 -*-

from bibliotheca.core.browser.faceted.map import FacetedMapView
from bibliotheca.core.testing import BIBLIOTHECA_CORE_INTEGRATION_TESTING
from io import BytesIO
from PIL import Image
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobImage

import json
import unittest


def make_image(width=800, height=600):
    data = BytesIO()
    Image.new("RGB", (width, height), "red").save(data, "PNG")
    return NamedBlobImage(data=data.getvalue(), filename="image.png")


class TestFacetedMapView(unittest.TestCase):
    layer = BIBLIOTHECA_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.patrimoine = api.content.create(
            container=self.portal, type="patrimoine", title="Patrimoine"
        )
        self.view = FacetedMapView(self.portal, self.request)

    def test_get_images_without_image(self):
        self.assertEqual(self.view.get_images(self.patrimoine), "")

    def test_get_images_returns_mini_scale_url(self):
        self.patrimoine.image = make_image()
        url = self.view.get_images(self.patrimoine)
        self.assertTrue(url.startswith(f"{self.patrimoine.absolute_url()}/@@images/"))
        scale = self.patrimoine.restrictedTraverse("@@images").scale("image", "mini")
        self.assertEqual(url, scale.url)
        self.assertLessEqual(scale.width, 200)

    def test_map_configuration_reflects_registry(self):
        records = {
            "fullscreen_control": True,
            "locate_control": False,
            "zoom_control": True,
            "show_minimap": False,
            "show_add_marker": False,
            "show_geosearch": True,
            "geosearch_provider": "openstreetmap",
            "default_map_layer": "OpenStreetMap.Mapnik",
            "map_layers": ["OpenStreetMap.Mapnik", "Esri.WorldImagery"],
            "default_latitude": 50.4,
            "default_longitude": 4.4,
        }
        for name, value in records.items():
            api.portal.set_registry_record(f"geolocation.{name}", value)

        config = json.loads(self.view.map_configuration())

        self.assertEqual(
            config,
            {
                "fullscreencontrol": True,
                "locatecontrol": False,
                "zoomcontrol": True,
                "minimap": False,
                "addmarker": False,
                "geosearch": True,
                "geosearch_provider": "openstreetmap",
                "default_map_layer": "OpenStreetMap.Mapnik",
                "map_layers": [
                    {"title": "OpenStreetMap Mapnik", "id": "OpenStreetMap.Mapnik"},
                    {"title": "Esri World Imagery", "id": "Esri.WorldImagery"},
                ],
                "latitude": 50.4,
                "longitude": 4.4,
            },
        )

    def test_map_configuration_without_map_layers(self):
        api.portal.set_registry_record("geolocation.map_layers", [])
        config = json.loads(self.view.map_configuration())
        self.assertEqual(config["map_layers"], [])
