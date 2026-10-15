# -*- coding: utf-8 -*-
from collective.faceted.map.utils import add_behavior
from collective.geolocationbehavior.geolocation import IGeolocatable
from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.testing import z2

import bibliotheca.core
import eea.facetednavigation


class BibliothecaCoreLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        self.loadZCML(name="testing.zcml", package=bibliotheca.core)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "bibliotheca.core:default")


BIBLIOTHECA_CORE_FIXTURE = BibliothecaCoreLayer()


BIBLIOTHECA_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(BIBLIOTHECA_CORE_FIXTURE,), name="BibliothecaCoreLayer:IntegrationTesting"
)


BIBLIOTHECA_CORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BIBLIOTHECA_CORE_FIXTURE,), name="BibliothecaCoreLayer:FunctionalTesting"
)


BIBLIOTHECA_CORE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(BIBLIOTHECA_CORE_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="BibliothecaCoreLayer:AcceptanceTesting",
)


class BibliothecaCoreFacetedMapLayer(PloneSandboxLayer):
    """A faceted map folder with two geolocated patrimoines and one without
    coordinates."""

    defaultBases = (BIBLIOTHECA_CORE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Loaded by z3c.autoinclude in production, not in tests.
        self.loadZCML(package=eea.facetednavigation)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "eea.facetednavigation:default")
        add_behavior("Folder", "eea.faceted.navigable")
        setRoles(portal, TEST_USER_ID, ["Manager"])
        folder = api.content.create(
            container=portal, type="Folder", id="map", title="Map"
        )
        api.content.get_view("faceted_subtyper", folder, portal.REQUEST).enable()
        IFacetedLayout(folder).update_layout("faceted-map")
        # eea default criteria only show Documents.
        criteria = ICriteria(folder)
        portal_type = next(c for c in criteria.values() if c.index == "portal_type")
        criteria.edit(portal_type.getId(), default=["patrimoine"])
        coordinates = {
            "Namur": Geolocation(latitude="50.4669", longitude="4.8675"),
            "Liège": Geolocation(latitude="50.6326", longitude="5.5797"),
            "Nowhere": None,
        }
        for title, geolocation in coordinates.items():
            patrimoine = api.content.create(
                container=folder, type="patrimoine", title=title
            )
            IGeolocatable(patrimoine).geolocation = geolocation
            patrimoine.reindexObject()


BIBLIOTHECA_CORE_FACETED_MAP_FIXTURE = BibliothecaCoreFacetedMapLayer()


BIBLIOTHECA_CORE_FACETED_MAP_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        BIBLIOTHECA_CORE_FACETED_MAP_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="BibliothecaCoreFacetedMapLayer:AcceptanceTesting",
)
