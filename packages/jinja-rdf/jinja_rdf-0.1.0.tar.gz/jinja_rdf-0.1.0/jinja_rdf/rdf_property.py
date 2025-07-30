from rdflib import URIRef
from rdflib.resource import Resource as RDFLibResource
from rdflib.util import from_n3
from jinja2 import pass_context
from jinja2.runtime import Context
from .rdf_resource import RDFResource


@pass_context
def rdf_properties(
    context: Context, resource: RDFLibResource | URIRef, property: str | URIRef
):
    if isinstance(property, str) and not isinstance(property, URIRef):
        property = from_n3(property, nsm=context["namespace_manager"])
    if isinstance(resource, str) and not isinstance(resource, URIRef):
        resource = from_n3(resource, nsm=context["namespace_manager"])
    if isinstance(resource, URIRef):
        resource = RDFResource(context["graph"], resource, context["namespace_manager"])
    return resource.objects(property)


@pass_context
def rdf_inverse_properties(
    context: Context, resource: RDFLibResource | URIRef, property: str | URIRef
):
    if isinstance(property, str) and not isinstance(property, URIRef):
        property = from_n3(property, nsm=context["namespace_manager"])
    if isinstance(resource, str) and not isinstance(resource, URIRef):
        resource = from_n3(resource, nsm=context["namespace_manager"])
    if isinstance(resource, URIRef):
        resource = RDFResource(context["graph"], resource, context["namespace_manager"])
    return resource.subjects(property)


@pass_context
def rdf_property(
    context: Context, resource: RDFLibResource | URIRef, property: str | URIRef
):
    return next(rdf_properties(context, resource, property))


@pass_context
def rdf_inverse_property(
    context: Context, resource: RDFLibResource | URIRef, property: str | URIRef
):
    return next(rdf_inverse_properties(context, resource, property))
