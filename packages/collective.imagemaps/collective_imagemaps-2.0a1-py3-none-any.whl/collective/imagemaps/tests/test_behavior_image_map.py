# -*- coding: utf-8 -*-
from collective.imagemaps.behaviors.image_map import IImageMapMarker
from collective.imagemaps.testing import (
    COLLECTIVE_IMAGEMAPS_INTEGRATION_TESTING  # noqa,
)
from plone.app.testing import setRoles, TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility

import unittest


class ImageMapIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_IMAGEMAPS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_behavior_image_map(self):
        behavior = getUtility(IBehavior, 'collective.imagemaps.image_map')
        self.assertEqual(
            behavior.marker,
            IImageMapMarker,
        )
