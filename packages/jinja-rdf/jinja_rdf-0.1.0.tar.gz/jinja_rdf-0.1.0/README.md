# Jinja RDF

> [!WARNING]
>
> This project is still under development, the interface are unstable and might break in future versions.

This project aims at providing the necessary means to render contents of and RDF Graph with [RDFLib](https://rdflib.readthedocs.io/) in a [Jinja](https://jinja.palletsprojects.com/en/3.0.x/) (jinja2) template.

## Data Model

Provide wrappers around the RDFLib classes to efficiently use the objects in a template.

- `RDFResource`
- `get_context()`
  - `resource`
  - `graph`
  - `namespace_manager`
  - `n`
  - `namespaces`

## Filters

`register_filters()`

- `property`
- `property_inv`
- `properties`
- `properties_inv`
- `query`

## Related Projects

This project just provides the methods and classes to use RDF graphs to build pages with jinja.
To use these methods there are two implementations with different use cases:

### Kisumu

[kisumu](https://github.com/AKSW/kisumu)

A simple command line tool and library to render a template + an RDF graph -> a static document.

### MkRdf

[MkRdf](https://github.com/AKSW/mkrdf)

A MkDocs plugin to render static sites or individual pages in a site with data from an RDF graph.

### Jekyll RDF

[Jekyll RDF](https://github.com/AKSW/jekyll-rdf)

[Read about the relation](https://github.com/AKSW/mkrdf/blob/main/README.md#jekyll-rdf) and [how to migrate](https://github.com/AKSW/mkrdf/blob/main/README.md#migrate-from-jekyll-rdf).
