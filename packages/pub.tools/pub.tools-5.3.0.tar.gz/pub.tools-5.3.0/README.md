# Installation

    pip install pub.tools

To use this tool you are advised to create an Entrez account and use the associated email and API key.

    from Bio import Entrez
    Entrez.email = "myemailhere@imsweb.com"
    Entrez.tool = "pub.tools"
    Entrez.api_key = "mykeyhere"

Tools available:

* entrez - a wrapper API for BioPython
* citations - creates citations for 6 different types using IMS standards
* date - formats dates into our desired format

## Citations

Citations are based on a standard defined by PubMed https://www.ncbi.nlm.nih.gov/books/NBK7256/.
For some publication types, passing the italicize parameter with a True value will return
HTML with italic tagged journals or conference names.

You can easily create a citation from a retrieved PubMed record:

    >>> from pub.tools import entrez
    >>> from pub.tools import citations
    >>> if pub := entrez.get_publication(pmid=12345678):
    >>>     citations.publication_citation(publication=pub)

Alternatively, you can pass one of the following to the citation function:

1. An instance of one of the dataclasses in schema.py
2. Keyword arguments directly

## Journals

The journals module uses the PMC source file https://www.ncbi.nlm.nih.gov/pmc/journals/?format=csv
to construct a library of journals keyed by abbreviation or full title.