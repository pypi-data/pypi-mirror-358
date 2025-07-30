from rdflib import URIRef
from rdflib.resource import Resource as RDFLibResource
from rdflib import Graph
from rdflib.util import from_n3
from jinja2 import pass_context
from jinja2.runtime import Context


@pass_context
def sparql_query(
    context: Context, input: RDFLibResource | Graph | URIRef, query: str, **kwargs
):
    if isinstance(input, Graph):
        graph = input
        resourceIri = input.identifier
    if isinstance(input, RDFLibResource):
        graph = input.graph
        resourceIri = input.identifier
    if isinstance(input, URIRef):
        graph = context["graph"]
        resourceIri = input
    namespaces = None
    if context["namespace_manager"]:
        namespaces = dict(context["namespace_manager"].namespaces())
    return graph.query(
        query,
        initBindings={
            **{k: from_n3(v) for k, v in kwargs.items()},
            "resourceIri": resourceIri,
            "resourceUri": resourceIri,
            "graphIri": graph.identifier,
        },
        initNs=namespaces,
    )
