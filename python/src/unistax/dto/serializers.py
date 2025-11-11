"""DTO serializers."""

from abc import ABC, abstractmethod
from typing import Any
import json
import xml.etree.ElementTree as ET


class Serializer(ABC):
    """Base serializer interface."""

    @abstractmethod
    def serialize(self, data: Any) -> str:
        """Serialize data."""
        pass

    @abstractmethod
    def deserialize(self, data: str) -> Any:
        """Deserialize data."""
        pass


class JSONSerializer(Serializer):
    """JSON serializer."""

    def serialize(self, data: Any) -> str:
        """Serialize to JSON."""
        if hasattr(data, "to_dict"):
            return json.dumps(data.to_dict())
        return json.dumps(data)

    def deserialize(self, data: str) -> Any:
        """Deserialize from JSON."""
        return json.loads(data)


class XMLSerializer(Serializer):
    """XML serializer."""

    def serialize(self, data: Any) -> str:
        """Serialize to XML."""
        if hasattr(data, "to_dict"):
            data = data.to_dict()

        root = ET.Element("root")
        self._dict_to_xml(data, root)
        return ET.tostring(root, encoding="unicode")

    def deserialize(self, data: str) -> Any:
        """Deserialize from XML."""
        root = ET.fromstring(data)
        return self._xml_to_dict(root)

    def _dict_to_xml(self, data: dict, parent: ET.Element):
        """Convert dict to XML elements."""
        for key, value in data.items():
            child = ET.SubElement(parent, key)
            if isinstance(value, dict):
                self._dict_to_xml(value, child)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        item_elem = ET.SubElement(child, "item")
                        self._dict_to_xml(item, item_elem)
                    else:
                        item_elem = ET.SubElement(child, "item")
                        item_elem.text = str(item)
            else:
                child.text = str(value)

    def _xml_to_dict(self, element: ET.Element) -> dict:
        """Convert XML element to dict."""
        result = {}
        for child in element:
            if len(child) == 0:
                result[child.tag] = child.text
            else:
                result[child.tag] = self._xml_to_dict(child)
        return result
