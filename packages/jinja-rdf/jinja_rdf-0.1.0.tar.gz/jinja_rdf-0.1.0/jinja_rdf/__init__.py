from rdflib import Graph, URIRef
from rdflib.namespace import Namespace
from .rdf_property import (
    rdf_properties,
    rdf_inverse_properties,
    rdf_property,
    rdf_inverse_property,
)
from .rdf_resource import RDFResource
from .sparql_query import sparql_query


def register_filters(environment):
    """Register all jinja-rdf filters on a jinja environment."""
    environment.filters["properties"] = rdf_properties
    environment.filters["properties_inv"] = rdf_inverse_properties
    environment.filters["property"] = rdf_property
    environment.filters["property_inv"] = rdf_inverse_property
    environment.filters["query"] = sparql_query


def get_context(graph: Graph, resource: RDFResource | URIRef | str):
    """Get the context to pass to a jinja template render or stream function."""
    n = {
        prefix: Namespace(namespace)
        for prefix, namespace in graph.namespace_manager.namespaces()
    }
    namespaces = {prefix.upper(): namespace for prefix, namespace in n.items()}
    return {
        **namespaces,
        "resource": RDFResource(graph, resource, graph.namespace_manager),
        "graph": graph,
        "namespace_manager": graph.namespace_manager,
        "n": n,
    }
