from typing import Callable, BinaryIO, Dict, Any

from lxml import etree
from lxml.etree import Element, iterparse


class XMLParser:
    __slots__ = ['parse_function']
    parse_function: Callable[[Dict[str, Any]], None]

    def __init__(self, parse_function: Callable[[Dict[str, Any]], None]):
        self.parse_function = parse_function  # type: ignore

    @staticmethod
    def fast_iter(context: iterparse, func: Callable[[Element], None], *args: Any, **kwargs: Any) -> None:
        for event, elem in context:
            func(elem)  # , *args, **kwargs
            # It's safe to call clear() here because no descendants will be accessed
            elem.clear()
            # Also eliminate now-empty references from the root node to elem
            for ancestor in elem.xpath('ancestor-or-self::*'):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
        del context

    def parse_buffer(self, data_buffer: BinaryIO, tag_name: str) -> None:
        context = etree.iterparse(data_buffer, events=('end',), tag=tag_name)
        self.fast_iter(context, lambda x: self.parse_function(x.attrib))
