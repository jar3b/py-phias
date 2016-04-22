# -*- coding: utf-8 -*-

from lxml import etree


class XMLParser:
    def __init__(self, parse_function):
        self.parse_function = parse_function

    @staticmethod
    def fast_iter(context, func, *args, **kwargs):
        for event, elem in context:
            # print event
            func(elem, *args, **kwargs)
            # It's safe to call clear() here because no descendants will be accessed
            elem.clear()
            # Also eliminate now-empty references from the root node to elem
            for ancestor in elem.xpath('ancestor-or-self::*'):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
        del context

    def parse_buffer(self, data_buffer, tag_name):
        context = etree.iterparse(data_buffer, events=('end',), tag=tag_name)
        self.fast_iter(context, lambda x: self.parse_function(x.attrib))
