import xml.etree.ElementTree as ET
from typing import Dict, Any, Callable, Tuple
from dec_graphs import Supernode, Superedge
from multilevelgraphs import MultilevelGraph


def _default_node_label_func(supernode: Supernode) -> str:
    return supernode['label'] if 'label' in supernode.attr else supernode.key

def _default_node_color_func(supernode: Supernode) -> tuple[str, str, str, str]:
    if 'color' in supernode.attr and isinstance(supernode['color'], Tuple) and len(supernode['color']) == 3 and \
            all((isinstance(c, int) and 0 <= c <= 255) for c in supernode['color']):
        return str(supernode['color'][0]), str(supernode['color'][1]), str(supernode['color'][2]), "1.0"
    elif supernode.supernode:
        hashcode = hash(supernode.supernode.key)
        return str((hashcode & 0xFF0000) >> 16), str((hashcode & 0x00FF00) >> 8), str(hashcode & 0x0000FF), "1.0"
    else:
        return "0", "0", "0", "1.0"

def _default_node_size_func(supernode: Supernode) -> str:
    if 'size' in supernode.attr:
        return str(supernode['size'])
    elif 'weight' in supernode.attr:
        return str(supernode['weight'])
    else:
        return str(((supernode.level if supernode.level else 0) + 1) * 10)

def _default_edge_color_func(edge: Superedge) -> tuple[str, str, str, str]:
    if 'color' in edge.attr and isinstance(edge['color'], Tuple) and len(edge['color']) == 3 and \
            all((isinstance(c, int) and 0 <= c <= 255) for c in edge['color']):
        return str(edge['color'][0]), str(edge['color'][1]), str(edge['color'][2]), "1.0"
    elif edge.tail.supernode and edge.head.supernode and edge.tail.supernode == edge.head.supernode:
        hashcode = hash(edge.tail.supernode.key)
        return str((hashcode & 0xFF0000) >> 16), str((hashcode & 0x00FF00) >> 8), str(hashcode & 0x0000FF), "1.0"
    else:
        return "0", "0", "0", "1.0"
def write_gexf(ml_graph: MultilevelGraph, file_path: str,
               node_label_func: Callable[[Supernode], str] = _default_node_label_func):
    writer = GEXFWriter()
    for supernode in ml_graph.get_graph(ml_graph.height(), deepcopy=False).nodes():
        _add_node_and_children(writer, supernode, node_label_func)
    for edge in ml_graph.edges:
        writer.add_edge(edge.id, edge.source.id, edge.target.id, {'weight': edge.weight})
    writer.write(file_path)


def _add_node_and_children(writer: 'GEXFWriter', supernode: Supernode, parent: ET.Element,
                           node_label_func: Callable[[Supernode], str],
                           node_color_func: Callable[[Supernode], Tuple[str, str, str]] = None,
                           node_size_func: Callable[[Supernode], str] = None):
    node_element = writer.add_node(node_id=supernode.key,
                                   label=node_label_func(supernode),
                                   color=node_color_func(supernode) if node_color_func else None,
                                   size=node_size_func(supernode) if node_size_func else None,
                                   attributes=supernode.attr)
    for child in supernode.dec.nodes():
        _add_node_and_children(writer, child, node_element, node_label_func, node_color_func, node_size_func)
        writer.add_edge(edge_id="("+child.key + ", " + supernode.key+")",
                        source_id=str(child.key),
                        target_id=str(supernode.key),
                        color=_default_node_color_func(child),
                        attributes={'relationship': 'hasSupernode'})


class GEXF:
    versions = {
        "1.3": {
            "NS_GEXF": 'http://gexf.net/1.3',
            "NS_VIZ": "http://www.gexf.net/1.3/viz",
            "NS_XSI": 'http://www.w3.org/2001/XMLSchema-instance',
            "SCHEMALOCATION": " ".join([
                'http://gexf.net/1.3,'
                'http://gexf.net/1.3/gexf.xsd']),
            "VERSION": "1.3",
        }
    }

    types: Dict[type, str] = dict([
        (int, "integer"),
        (float, "double"),
        (bool, "boolean"),
        (str, "string")
    ])


class GEXFWriter:
    def __init__(self, version: str = "1.3"):
        self.gexf = ET.Element('gexf',
                               {'xmlns': GEXF.versions[version]["NS_GEXF"],
                                'xmlns:viz': GEXF.versions[version]["NS_VIZ"],
                                'xmlns:xsi': GEXF.versions[version]["NS_XSI"],
                                'xsi:schemaLocation': GEXF.versions[version]["SCHEMALOCATION"],
                                'version': GEXF.versions[version]["VERSION"]})
        self.graph = ET.SubElement(self.gexf, 'graph', {'mode': 'static', 'defaultedgetype': 'directed'})
        self.node_attributes = ET.SubElement(self.graph, 'attributes', {'class': 'node'})
        self.edge_attributes = ET.SubElement(self.graph, 'attributes', {'class': 'edge'})
        self.nodes = ET.SubElement(self.graph, 'nodes')
        self.edges = ET.SubElement(self.graph, 'edges')
        self.nodes_attr_set = set()
        self.edges_attr_set = set()

    def add_node_attribute(self, attr_name: str, attr_type: type):
        if attr_name not in self.nodes_attr_set:
            ET.SubElement(self.node_attributes, 'attribute',
                          {'id': attr_name,
                           'title': attr_name.title(),
                           'type': GEXF.types.setdefault(attr_type, 'string')})
            self.nodes_attr_set.add(attr_name)

    def add_edge_attribute(self, attr_name: str, attr_type: type):
        if attr_name not in self.edges_attr_set:
            ET.SubElement(self.edge_attributes, 'attribute',
                          {'id': attr_name,
                           'title': attr_name.title(),
                           'type': GEXF.types.setdefault(attr_type, 'string')})
            self.edges_attr_set.add(attr_name)

    def add_node(self, node_id: str, label: str,
                 color: Tuple[str, str, str, str] = None,
                 size: str = None,
                 parent: ET.Element = None,
                 attributes: Dict[str, Any] = None) -> ET.Element:
        node = ET.Element('node', {'id': node_id, 'label': label})
        if attributes:
            attvalues = ET.SubElement(node, 'attvalues')
            for attr_name, value in attributes.items():
                self.add_node_attribute(attr_name, type(value))
                ET.SubElement(attvalues, 'attvalue', {'for': attr_name,
                                                      'value': value if type(value) in GEXF.types else str(value)})

        if parent is not None:
            if not parent.find('nodes'):
                ET.SubElement(parent, 'nodes')
            parent.find('nodes').append(node)
        else:
            self.nodes.append(node)

        return node

    def add_edge(self, edge_id: str, source_id: str, target_id: str,
                 color: tuple[str, str, str, str, str] = None,
                 attributes: Dict[str, Any] = None):
        edge = ET.SubElement(self.edges, 'edge', {'id': edge_id, 'source': source_id, 'target': target_id})
        if attributes:
            attvalues = ET.SubElement(edge, 'attvalues')
            for attr_id, value in attributes.items():
                self.add_edge_attribute(attr_id, type(value))
                ET.SubElement(attvalues, 'attvalue', {'for': attr_id, 'value': str(value)})

    def write(self, file_path):
        tree = ET.ElementTree(self.gexf)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
