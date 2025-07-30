"""This module includes methods to handle graphs in the context of static site
generation and templating."""

from urllib.parse import urlsplit, urlunsplit, SplitResult
from rdflib import Graph, URIRef, BNode, IdentifiedNode
from rdflib.resource import Resource
from pathlib import Path, PurePosixPath
from hashlib import md5
from loguru import logger
from rdflib.namespace import RDF

from typing import TypeAlias

"""An IRI either as rdflib URIRef or as a NamedTuple as it is returned by
urllib.parse.urlsplit"""
IRIRef_or_Parts: TypeAlias = URIRef | SplitResult
Node_or_Parts: TypeAlias = IdentifiedNode | IRIRef_or_Parts

QUERY_SELECTION_RELATIVE = 'SELECT ?resourceIri { ?resourceIri ?p ?o . FILTER regex(str(?resourceIri), concat("^", str(?base_iri))) }'
QUERY_SELECTION_ALL = "SELECT ?resourceIri { ?resourceIri ?p ?o }"


def split_iris(*args):
    """Takes an arbitrary number of iri arguments either as str/URIRef or
    NamedTuple and return all as NamedTuple as returned by urlsplit."""
    for iri in args:
        if iri and not isinstance(iri, SplitResult):
            yield urlsplit(iri)
        else:
            yield iri


class IRIPath(PurePosixPath):
    """Mainly a wrapper for a PurePosixPath that preserves a trailing slash."""

    def __init__(self, *args):
        super().__init__(*args)
        self.trailing_slash = "/" if args[-1][-1] == "/" else ""

    def __str__(self):
        return super().__str__() + self.trailing_slash

    def __add__(self, name_extension: str):
        if self.trailing_slash:
            parts = self.parts
            extended_name = name_extension
        else:
            parts = self.parts[:-1]
            extended_name = self.parts[-1] + name_extension
        return self.with_segments(*parts, extended_name)


class GraphToFilesystemHelper:
    """Methods to convert nodes resp. IRIs to paths, based on a given confifuration."""

    def __init__(
        self,
        base_iri: str | IRIRef_or_Parts,
        base_path: None | Path = None,
        collect_blank: None | Path = None,
        collect_outside: None | Path = None,
    ):
        self.base_iri = base_iri
        self.base_path = base_path
        self.collect_blank = collect_blank
        self.collect_outside = collect_outside

    def node_to_path(
        self,
        node: Node_or_Parts,
    ) -> tuple[Path | None, str | None]:
        """Convert any identified node to a relative filesystem path.

        If the iri matches the base_iri, it is trimmed.
        If the iri does not match the base_iri resp. is not relative to it, the path
        will represent the complete iri and be put under collect_outside if it is
        specified.
        If the input is a blank node, the path will be relative to collect_blank if
        it is specified.

        Returns: the relative path and an anchor/fragment identifier if the iri
        includes a fragment identifier.
        """
        if not isinstance(node, BNode):
            return self.iri_to_path(node)
        elif self.collect_blank:
            return self.collect_blank / node, None
        return None, None

    def iri_to_path(
        self,
        iri: IRIRef_or_Parts,
    ) -> tuple[Path | None, str | None]:
        """Convert an IRI to a relative filesystem path and optionally a fragment idnetifier.

        If the iri matches the base_iri, it is trimmed.
        If the iri does not match the base_iri resp. is not relative to it:
        either, if collect_outside is set, the path will represent the complete iri
        and be put under collect_outside.
        Else None, None is returned.

        If a fragment identifier is detected it is split of the IRI and is
        returned in the second position of the tuple
        """
        iri, base_iri = split_iris(iri, self.base_iri)

        if self.iri_is_relative_to(iri):
            """iri is relative to the base. Just convert the remaining part."""
            resulting_path = IRIPath(iri.path).relative_to(base_iri.path)
            if self.base_path:
                resulting_path = self.base_path.joinpath(resulting_path)
            if iri.query:
                resulting_path += "?" + iri.query
            return resulting_path, self.get_fragment_id(iri)

        if self.collect_outside:
            """iri is not relative to the base. convert schema, netloc, path and query to a path."""
            resulting_path = IRIPath(f"{iri.schema}_{iri.netloc}") / iri.path
            if self.base_path:
                resulting_path = self.base_path.joinpath(resulting_path)
            return resulting_path, self.get_fragment_id(iri)

        return None, None

    def selection_to_nodes(
        self, selection: str | None = None, graph: Graph | None = None
    ):
        """Return a list of nodes based on a selection query.
        The selection query must bind a variable ?resourceIri.
        """
        if isinstance(selection, str) and selection.lower() == "none":
            return []

        if selection.get("preset") == "none":
            return []

        queries = []
        iri_list = []
        file_names = []

        if selection.get("file"):
            file_names += [selection["file"]]
        if selection.get("files"):
            file_names += selection["files"]

        for file_name in file_names:
            with open(file_name, "r") as file_object:
                iri_list += list(file_object)

        if selection.get("list"):
            iri_list += selection["list"]

        for iri in iri_list:
            yield URIRef(iri.strip())

        logger.debug(queries)
        if selection.get("query"):
            queries += [selection["query"]]
        if selection.get("queries"):
            queries += selection["queries"]
        if selection.get("preset") == "subject_all":
            queries += [QUERY_SELECTION_ALL]
        if (not queries and not iri_list) or (
            selection.get("preset") == "subject_relative"
        ):
            queries += [QUERY_SELECTION_RELATIVE]

        if queries and not graph:
            raise Exception(
                "No graph is provided but a query based selection is given."
            )

        for query in set(queries):
            logger.debug(f"Execute selection query: {query}")
            for row in graph.query(
                query, initBindings={"base_iri": URIRef(self.base_iri)}
            ):
                yield row.resourceIri

    def nodes_to_paths(self, nodes: list) -> tuple:
        """Return a list of nodes, paths, and fragments for the provided nodes.
        If no path is returned from node_to_path for a node, it is omitted.
        The returned tuple:
        - the node,
        - the path representing the node
        - optionally a fragment that was attached to the nodes iri."""
        for node in nodes:
            path, fragment = self.node_to_path(node)
            if path:
                yield node, path, fragment

    def get_fragment_id(
        self,
        iri: IRIRef_or_Parts,
        fallback_generate: bool = False,
    ) -> str | None:
        """Get the fragment identifier of an IRI or optionally generate an md5 sum
        of the iri to use as an identifier, if none is present.

        base_iri (default: None): Only return the frament identifier, if the iri is
        relative to this base, else fallback to md5 or None. (This can be used to
        only get fragment identifiers for iris on the current page.)
        fallback_generate (default: False): if true it will generate an md5 sum if
        not fragment identifier was found."""
        iri, base_iri = split_iris(iri, self.base_iri)

        fragment = iri.fragment

        if base_iri and not self.iri_is_relative_to(iri):
            fragment = ""
        if not fragment and fallback_generate:
            return md5(urlunsplit(iri))
        return fragment or None

    def iri_is_relative_to(self, iri: IRIRef_or_Parts):
        """Check if an IRI is relative to some base IRI."""
        iri, base_iri = split_iris(iri, self.base_iri)
        return base_iri[0:1] == iri[0:1] and IRIPath(iri.path).is_relative_to(
            base_iri.path
        )


class TemplateSelectionHelper:
    def __init__(
        self,
        graph: Graph,
        class_template_map: dict = {},
        instance_template_map: dict = {},
    ):
        self.graph = graph
        self.instance_template_map = {
            URIRef(iri): template for iri, template in instance_template_map.items()
        }
        self.class_template_map = {
            URIRef(iri): template for iri, template in class_template_map.items()
        }

    def get_template_for_resource(self, resource: URIRef | Resource):
        resource_iri = resource.identifier
        if self.instance_template_map.get(resource_iri):
            return self.instance_template_map.get(resource_iri)

        template_candidates = set()
        for rdf_type in resource[RDF.type]:
            logger.debug(rdf_type)
            template = self.class_template_map.get(rdf_type.identifier)
            if template:
                template_candidates.add(template)

        if len(template_candidates) > 1:
            logger.warning("More then one template candidate")

        if len(template_candidates) > 0:
            return template_candidates.pop()
