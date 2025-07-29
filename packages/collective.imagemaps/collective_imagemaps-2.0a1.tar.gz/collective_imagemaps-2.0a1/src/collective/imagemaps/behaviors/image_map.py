# -*- coding: utf-8 -*-

from collective.imagemaps import _
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from Products.CMFPlone.utils import safe_hasattr
from zope.component import adapter
from zope.interface import implementer, Interface, provider


class IImageMapMarker(Interface):
    pass


@provider(IFormFieldProvider)
class IImageMap(model.Schema):
    """
    """

    imagemap = schema.SourceText(
        title=_(u"Image Map Markup",),
        description=_(u"Insert your image map markup here.",),
        default=u"",
        required=False,
        readonly=False,
    )


@implementer(IImageMap)
@adapter(IImageMapMarker)
class ImageMap(object):
    def __init__(self, context):
        self.context = context

    @property
    def imagemap(self):
        if safe_hasattr(self.context, "imagemap"):
            return self.context.imagemap or ""
        return None

    @imagemap.setter
    def imagemap(self, value):
        self.context.imagemap = value
