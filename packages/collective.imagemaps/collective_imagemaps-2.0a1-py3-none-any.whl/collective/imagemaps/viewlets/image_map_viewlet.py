# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import ViewletBase
from Products.CMFPlone.utils import safe_unicode

class ImageMapViewlet(ViewletBase):
    def update(self):
        self.imagemap = getattr(self.context, "imagemap", "")

    def index(self):
        return safe_unicode(self.imagemap) or u""
