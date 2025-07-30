from rdflib.resource import Resource as RDFLibResource
from rdflib.util import from_n3
from rdflib import BNode, URIRef


class RDFResource(RDFLibResource):
    def __init__(self, graph, subject, namespace_manager=None):
        self.namespace_manager = namespace_manager
        super().__init__(graph, subject)

    def __getitem__(self, item):
        if isinstance(item, str) and not isinstance(item, URIRef):
            item = from_n3(item, nsm=self.namespace_manager)
        return super().__getitem__(item)

    def _cast(self, node):
        if isinstance(node, (BNode, URIRef)):
            return self._new(node)
        elif isinstance(node, (RDFLibResource)):
            return self._new(node.identifier)
        else:
            return node

    def n3(self):
        return self._identifier.n3()
