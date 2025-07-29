import logging
import re
import time
import xml.etree.ElementTree as et
from http.client import HTTPResponse
from http.client import IncompleteRead

from Bio import Entrez
from unidecode import unidecode

from . import config
from .formatting import format_date_str
from .schema import Abstract
from .schema import BookRecord
from .schema import ChapterRecord
from .schema import EntrezRecord
from .schema import Grant
from .schema import JournalRecord
from .schema import Person
from .schema import Section

logger = logging.getLogger("pub.tools")

STOPWORDS = [
    "a",
    "about",
    "again",
    "all",
    "almost",
    "also",
    "although",
    "always",
    "among",
    "an",
    "and",
    "another",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "between",
    "both",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "done",
    "due",
    "during",
    "each",
    "either",
    "enough",
    "especially",
    "etc",
    "for",
    "found",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "here",
    "how",
    "however",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "kg",
    "km",
    "made",
    "mainly",
    "make",
    "may",
    "mg",
    "might",
    "ml",
    "mm",
    "most",
    "mostly",
    "must",
    "nearly",
    "neither",
    "no",
    "nor",
    "obtained",
    "of",
    "often",
    "on",
    "our",
    "overall",
    "perhaps",
    "quite",
    "rather",
    "really",
    "regarding",
    "seem",
    "seen",
    "several",
    "should",
    "show",
    "showed",
    "shown",
    "shows",
    "significantly",
    "since",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "then",
    "there",
    "therefore",
    "these",
    "they",
    "this",
    "those",
    "through",
    "thus",
    "to",
    "upon",
    "use",
    "used",
    "using",
    "various",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "which",
    "while",
    "with",
    "within",
    "without",
    "would",
]
PUNC_STOPWORDS = [r"\&", r"\(", r"\)", r"\-", r"\;", r"\:", r"\,", r"\.", r"\?", r"\!", r" "]


class PubToolsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


IMSEntrezError = PubToolsError


def _parse_author_name(author: dict, investigator: bool = False) -> Person:
    fname = author.get("ForeName", "")
    # strip excess spaces like in
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=22606070&retmode=xml
    fname = " ".join([part for part in fname.split(" ") if part])
    identifiers = {source.attributes.get("Source", ""): str(source) for source in author.get("Identifier", [])}
    return Person(
        last_name=author.get("LastName", ""),
        first_name=fname,
        initial=author.get("Initials", ""),
        collective_name=author.get("CollectiveName", ""),
        suffix=author.get("Suffix", ""),
        investigator=investigator,
        identifiers=identifiers,
        affiliations=author.get("affiliations", []),
    )


def _parse_entrez_record(record: dict, escape: bool = True) -> JournalRecord | BookRecord | ChapterRecord | None:
    """convert this into our own data structure format
    Journal keys - MedlineCitation, PubmedData
    Book keys - BookDocument, PubmedBookData
    """
    if "PubmedData" in record:
        rec = _parse_entrez_journal_record(record)
    elif "PubmedBookData" in record:
        rec = _parse_entrez_book_record(record)
    else:
        return

    rec.process(escape)
    return rec


def _parse_entrez_book_record(record: dict) -> BookRecord:
    _type = "book"
    document = record.pop("BookDocument")
    book = document.pop("Book")

    authors = []
    if document.get("AuthorList", []) and document["AuthorList"][0].attributes["Type"] == "authors":
        for author in document["AuthorList"][0]:
            author["affiliations"] = []
            for aff in author.get("AffiliationInfo", []):
                author["affiliations"].append(aff["Affiliation"])
            authors.append(_parse_author_name(author))

    editors = []
    if book.get("AuthorList", []) and book["AuthorList"][0].attributes["Type"] == "editors":
        for author in book["AuthorList"][0]:
            author["affiliations"] = []
            for aff in author.get("AffiliationInfo", []):
                author["affiliations"].append(aff["Affiliation"])
            authors.append(_parse_author_name(author))

    language = document["Language"][0] if document.get("Language", "") else document["Language"]

    articleids = document.pop("ArticleIdList")
    article_ids = {}
    for aid in articleids:
        article_ids[aid.attributes["IdType"]] = aid

    abstract = document.get("Abstract", {}).get("AbstractText", "")
    abstract = [Abstract(text=abstract[0] if isinstance(abstract, list) else abstract, nlmcategory="", label="")]

    articletitle = document.get("ArticleTitle", "")

    locationlabel = document.get("LocationLabel", "")
    if locationlabel and locationlabel[0].attributes["Type"] == "chapter":
        _type = "chapter"
        title = articletitle
        booktitle = book.get("BookTitle", "")
    else:
        title = book.get("BookTitle", "")
        booktitle = ""

    publisher = ""
    pubplace = ""
    if book.get("Publisher", ""):
        publisher = book["Publisher"].get("PublisherName", "")
        pubplace = book["Publisher"].get("PublisherLocation", "")

    if pubdate := book.get("PubDate", ""):
        pubdate = format_date_str(
            " ".join([
                i
                for i in (
                    pubdate.get("Year", ""),
                    pubdate.get("Season", ""),
                    pubdate.get("Month", ""),
                    pubdate.get("Day", ""),
                )
                if i
            ])
        )

    volume = book.get("Volume", "")
    volumetitle = book.get("VolumeTitle", "")
    edition = book.get("Edition", "")
    series = book.get("CollectionTitle", "")
    isbn = book.get("Isbn", "")
    isbn = isbn[0] if isbn and isinstance(isbn, list) else isbn
    elocation = book.get("ELocationID", "")
    medium = book.get("Medium", "")
    reportnum = book.get("ReportNumber", "")

    pmid = document["PMID"]

    sections = []
    for section in document.get("Sections", []):
        section_title = section["SectionTitle"]
        if section.get("LocationLabel", ""):
            section_type = section["LocationLabel"].attributes["Type"]
            section_label = section["LocationLabel"]
        else:
            section_type = ""
            section_label = ""
        sections.append(Section(title=section_title, section_type=section_type, label=section_label))

    kwargs = {
        "title": title,
        "authors": authors,
        "volume": volume,
        "pubdate": pubdate,
        "pmid": pmid,
        "medium": medium,
        "abstract": abstract,
        "language": language,
        "editors": editors,
        "publisher": publisher,
        "pubplace": pubplace,
        "volumetitle": volumetitle,
        "edition": edition,
        "series": series,
        "isbn": isbn,
        "elocation": elocation,
        "reportnum": reportnum,
        "sections": sections,
        "article_ids": article_ids,
    }
    if _type == "book":
        klass = BookRecord
    else:
        klass = ChapterRecord
        kwargs["booktitle"] = booktitle
    return klass(**kwargs)


def _parse_entrez_journal_record(record: dict) -> JournalRecord:
    medline = record.pop("MedlineCitation")
    medlineinfo = medline.pop("MedlineJournalInfo")
    article = medline.pop("Article")
    journal = article.pop("Journal")
    pmdates = record["PubmedData"].pop("History")
    articleids = record["PubmedData"].pop("ArticleIdList")
    pubmodel = article.attributes["PubModel"]
    articledate = article.pop("ArticleDate")

    journal_title = journal["Title"]
    pubdate = journal["JournalIssue"].get("PubDate", {})
    volume = journal["JournalIssue"].get("Volume", "")
    issue = journal["JournalIssue"].get("Issue", "")

    medium = journal["JournalIssue"].attributes["CitedMedium"]
    pagination = article.get("Pagination", {}).get("MedlinePgn", "")
    pubdate = format_date_str(
        " ".join([
            i
            for i in (
                pubdate.get("MedlineDate", ""),
                pubdate.get("Year", ""),
                pubdate.get("Season", ""),
                pubdate.get("Month", ""),
                pubdate.get("Day", ""),
            )
            if i
        ])
    )
    title = article["ArticleTitle"]

    pmpubdates = {}
    for pmdate in pmdates:
        pmdate_str = format_date_str(
            " ".join([i for i in (pmdate.get("Year", ""), pmdate.get("Month", ""), pmdate.get("Day", "")) if i])
        )
        pmpubdates["pmpubdate_" + pmdate.attributes["PubStatus"].replace("-", "")] = pmdate_str

    authors = []
    for author in article.get("AuthorList", []):
        if author.attributes["ValidYN"] == "Y":
            author["affiliations"] = []
            for aff in author.get("AffiliationInfo", []):
                author["affiliations"].append(aff["Affiliation"])
            authors.append(_parse_author_name(author))
    investigators = medline.get("InvestigatorList", [])
    if investigators:
        investigators = investigators[0]  # list wrapped
    for investigator in investigators:
        if investigator.attributes["ValidYN"] == "Y":
            authors.append(_parse_author_name(investigator, investigator=True))
    authors = authors
    pmid = medline["PMID"]

    article_ids = {}
    for aid in articleids:
        article_ids[aid.attributes["IdType"]] = aid

    grants = []
    for grant in article.get("GrantList", []):
        grants.append(
            Grant(grantid=grant.get("GrantID", ""), acronym=grant.get("Acronym", ""), agency=grant.get("Agency", ""))
        )
    mesh = []
    for meshHeader in medline.get("MeshHeadingList", []):
        mesh.append(meshHeader["DescriptorName"])
    pubtypelist = list(article.get("PublicationTypeList", []))
    edate = ""
    for adate in articledate:
        if adate.attributes["DateType"] == "Electronic":
            edate = format_date_str(
                " ".join([
                    i
                    for i in (
                        adate.get("MedlineDate", ""),
                        adate.get("Year", ""),
                        adate.get("Season", ""),
                        adate.get("Month", ""),
                        adate.get("Day", ""),
                    )
                    if i
                ])
            )
    medlineta = medlineinfo.get("MedlineTA", "")
    nlmuniqueid = medlineinfo.get("NlmUniqueID", "")
    medlinecountry = medlineinfo.get("Country", "")
    medlinestatus = medline.attributes["Status"]

    abstracts = []
    if article.get("Abstract"):
        for abst in article["Abstract"]["AbstractText"]:
            text = abst
            if hasattr(abst, "attributes"):
                nlmcat = abst.attributes.get("NlmCategory", "")
                label = abst.attributes.get("Label", "")
            else:
                nlmcat = label = ""
            abstracts.append(Abstract(text=text, nlmcategory=nlmcat, label=label))

    pubstatus = record["PubmedData"].get("PublicationStatus", "")

    # dates
    pmpubdates = {}
    for pmdate in record["PubmedData"].get("History", []):
        dtype = pmdate.attributes.get("PubStatus")
        _pmdate = " ".join([d for d in (pmdate.get("Year"), pmdate.get("Month"), pmdate.get("Day")) if d])
        pmpubdates[f"pmpubdate_{dtype}"] = _pmdate

    return JournalRecord(
        title=title,
        abstract=abstracts,
        pmid=pmid,
        pubstatus=pubstatus,
        article_ids=article_ids,
        authors=authors,
        edate=edate,
        grants=grants,
        issue=issue,
        volume=volume,
        journal=journal_title,
        medium=medium,
        medlinecountry=medlinecountry,
        medlinestatus=medlinestatus,
        journal_abbreviation=medlineta,
        mesh=mesh,
        nlmuniqueid=nlmuniqueid,
        pagination=pagination,
        pmpubdates=pmpubdates,
        pubdate=pubdate,
        pubmodel=pubmodel,
        pubtypelist=pubtypelist,
    )


def get_publication(pmid: str | int, escape: bool = True) -> JournalRecord | BookRecord | ChapterRecord:
    """
    Get a single publication by ID. We don't use PubMed's convoluted data structure but instead return
    a dict with simple values. Most values are a string or list, but some like authors and grants are further
    dicts containing more components.

    PubMed contains both books and journals, and we parse both, with some difference in available keys.

    :param pmid: PubMed ID
    :param escape: used by `Entrez.parse` and `.read`. If true, will return as html for title and abstract fields
    :return: publication record
    """
    handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
    try:
        for rec in Entrez.parse(handle, escape=escape):
            return _parse_entrez_record(rec, escape)
    except ValueError:
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        data = Entrez.read(handle, escape=escape)
        record = data["PubmedArticle"] + data["PubmedBookArticle"]
        if record:
            return _parse_entrez_record(record[0], escape)
    finally:
        handle.close()


def get_publication_by_doi(doi: str, escape: bool = True) -> JournalRecord | BookRecord | ChapterRecord:
    """
    Shortcut for finding publication with DOI

    :param doi: DOI value
    :param escape: used by `Entrez.parse` and `.read`. If true, will return as html
    :return publicatin record
    """
    ids = find_publications(doi=doi)
    if int(ids["Count"]) == 1:
        return get_publication(ids["IdList"][0], escape)


def get_pmid_by_pmc(pmcid: str) -> str:
    """
    We can't search by PMC in PubMed, but we can get the PMID from the PMC database

    Unfortunately, BioPython does not appear able to parse this XML file so we have to do so manually.
    A full DOM parser is probably fine for a file of this size.
    """
    if pmcid.startswith("PMC"):
        pmcid = pmcid[3:]
    handle = Entrez.efetch(db="pmc", id=pmcid)
    if handle:
        data = handle.read()
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        root = et.fromstring(data)
        for el in root.findall(".//article-id"):
            if el.attrib.get("pub-id-type") == "pmid":
                return el.text.strip()
        # we found an article, but it has no PMID given
        # try to search PubMed with PMC as a general term
        search = find_publications(all=f"PMC{pmcid}")
        if search["Count"] == "1":
            return search["IdList"][0]


def get_publications(pmids: list, escape: bool = True):
    """
    We let Biopython do most of the heavy lifting, including building the request POST. Publications are
    fetched in chunks of config.MAX_PUBS as there does seem to be a limit imposed by NCBI. There is also
    a 3-request per second limit imposed by NCBI until we get an API key, but that should also be handled by
    Biopython. Retries are done automatically by Biopython.

    :param pmids: a list of PMIDs
    :param escape: used by Entrez.parse and .read. If true, will return as html
    :return: generator of parsed pubs as python dicts
    """
    # Make sure pmids is a list, since that's what Entrez expects (and sets, for example, are not sliceable).
    total_time = time.time()
    if isinstance(pmids, set):
        pmids = list(pmids)
    start = 0
    while start < len(pmids):
        pmid_slice = pmids[start : start + config.MAX_PUBS]
        timer = time.time()
        logger.info(f"Fetching publications {start} through {min(len(pmids), start + config.MAX_PUBS)}...")
        handle = Entrez.efetch(db="pubmed", id=pmid_slice, retmode="xml")
        data = Entrez.read(handle, escape=escape)
        logger.info(f"Fetched and read after {time.time() - timer:02}s")
        for record in data["PubmedArticle"] + data["PubmedBookArticle"]:
            yield _parse_entrez_record(record, escape)
        start += config.MAX_PUBS
    logger.info(f"Total publications retrieved in {time.time() - total_time:.02} seconds")


def find_pmids(query):
    """
    Perform an ESearch and extract the pmids

    :param query: a generated search term compliant with pubmed
    :return: a list of pmid strings
    """
    handle = Entrez.esearch(db="pubmed", term=query, datetype="pdat", retmode="xml", retmax="100000")
    try:
        return Entrez.read(handle).get("IdList", [])
    finally:
        handle.close()


def esearch_publications(query: str) -> JournalRecord | BookRecord | ChapterRecord:
    """
    Perform an ESearch based on a term

    :param query: a generated search term compliant with pubmed
    :return: ESearch record. The useful values here are going to be the WebEnv and QueryKey which you can pass
             to get_searched_publications
    """
    handle = Entrez.esearch(db="pubmed", term=query, datetype="pdat", retmode="xml", retmax="100000")
    return process_handle(handle)


def find_publications(
    all: str | None = None,  # noqa: A002
    author_ids: list[str] | None = None,
    authors: list[str] | None = None,
    title: str | None = None,
    journal: str | None = None,
    start: str | None = None,
    end: str | None = None,
    pmid: str | None = None,
    mesh: str | None = None,
    gr: str | None = None,
    ir: bool = False,
    affl=None,
    doi="",
    inclusive=False,
) -> list[EntrezRecord]:
    """
    You can use the resulting WebEnv and QueryKey values to call get_searched_publications
    https://www.ncbi.nlm.nih.gov/books/NBK3827/#_pubmedhelp_Search_Field_Descriptions_and_

    :param all: appends
    :param author_ids: a list of strings
    :param authors: a list of strings
    :param title: article title str. Stop words and punctuation will be removed
    :param journal: article journal str
    :param start: YYYY/MM/DD start date
    :param end: YYYY/MM/DD end date
    :param pmid: article pubmed id
    :param mesh: mesh keywords
    :param gr: grant number
    :param ir: investigator
    :param affl: author affiliation
    :param doi: doi id
    :param inclusive: if "OR", Authors are or'd. Default is and'd
    :return: ESearch record. The useful values here are going to be the WebEnv and QueryKey which you can pass
             to get_searched_publications
    """
    term = generate_search_string(all, author_ids, authors, title, journal, pmid, mesh, gr, ir, affl, doi, inclusive)
    if not start:
        start = "1500/01/01"
    if not end:
        end = "2099/01/01"
    handle = Entrez.esearch(
        db="pubmed", term=term, datetype="pdat", mindate=start, maxdate=end, retmode="xml", retmax="100000"
    )
    return process_handle(handle)


def generate_search_string(
    all: str | None = None,  # noqa: A002
    author_ids: list[str] | None = None,
    authors: list[str] | None = None,
    title: str | None = None,
    journal: str | None = None,
    pmid: str | None = None,
    mesh: str | None = None,
    gr: str | None = None,
    ir: str | None = None,
    affl: str | None = None,
    doi: str | None = None,
    inclusive: bool = False,
) -> str:
    """
    Generate the search string that will be passed to ESearch based on these criteria
    """
    search_strings = []
    if all:
        search_strings.append(all)
    if author_ids:
        auth_join = " OR " if inclusive == "OR" else " "
        search_strings.append(auth_join.join([f"{unidecode(a)}[auid]" for a in author_ids if a]))
    if authors:
        auth_join = " OR " if inclusive == "OR" else " "
        search_strings.append(auth_join.join([f"{unidecode(a)}[au]" for a in authors if a]))

    if title:
        for stop in STOPWORDS:
            comp = re.compile(rf"(\s)?\b{stop}\b(\s)?", re.IGNORECASE)
            title = comp.sub("*", title)
        for stop in PUNC_STOPWORDS:
            comp = re.compile(rf"(\s)?(\b)?{stop}(\b)?(\s)?", re.IGNORECASE)
            title = comp.sub("*", title)
        titlevals = [elem.strip() for elem in title.split("*")]
        search_strings.append((titlevals and "+".join([f"{unidecode(t)}[ti]" for t in titlevals if t])) or "")
    if journal:
        search_strings.append(f'"{unidecode(journal)}"[jour]')
    if pmid:
        if isinstance(pmid, list | tuple):
            search_strings.append(" OR ".join([f"{unidecode(pid)}[pmid]" for pid in pmid if pid]))
        else:
            search_strings.append(f"{pmid}[pmid]")
    if gr:
        search_strings.append(f"{gr}[gr]")
    if affl:
        search_strings.append(f"{affl}[ad]")
    if ir:
        search_strings.append(f"{ir}[ir]")
    if mesh:
        search_strings.append("+".join([f"{m}[mesh]" for m in mesh]))
    if doi:
        search_strings.append(f"{doi.replace('(', ' ').replace(')', ' ')}[doi]")

    return "+".join(search_strings)


def get_searched_publications(
    web_env: str, query_key: str, ids: list[str] | None = None, escape: bool = True
) -> list[JournalRecord | BookRecord | ChapterRecord]:
    """
    Get a bunch of publications from Entrez using WebEnv and query_key from EPost. Option to narrow
    down subset of ids
    """
    if isinstance(ids, str):
        ids = [ids]
    records = []
    query = {"db": "pubmed", "webenv": web_env, "query_key": query_key, "retmode": "xml"}
    if ids:
        query["ids"] = ids
    handle = Entrez.efetch(**query)
    try:
        for record in Entrez.parse(handle, escape=escape):
            record = _parse_entrez_record(record, escape)
            if record:
                records.append(record)
    except ValueError:  # newer Biopython requires this to be Entrez.read
        handle = Entrez.efetch(**query)
        data = Entrez.read(handle, escape=escape)
        for record in data["PubmedArticle"] + data["PubmedBookArticle"]:
            record = _parse_entrez_record(record, escape)
            # Entrez.read does not use the ids query key so we have to do this ourselves
            if record and ((ids and record["pmid"] in ids) or not ids):
                records.append(record)
    return records


def process_handle(handle: HTTPResponse, escape=True):
    """
    Use EPost to store our PMID results to the Entrez History server and get back the WebEnv and QueryKey values

    :param handle: Entrez http stream
    :param escape: escape HTML entitites
    :return: Entrez read handle value with WebEnv and QueryKey
    """
    try:
        record = Entrez.read(handle, escape)
        search_results = None
        if record["IdList"]:
            # If we have search results, send the ids to EPost and use WebEnv/QueryKey from now on
            search_results = Entrez.read(Entrez.epost("pubmed", id=",".join(record["IdList"])))
    except Exception as e:
        logger.info(f'Entrez.read failed: "{e}"')
        raise PubToolsError("Unable to connect to Entrez") from e
    else:
        if search_results:
            record["WebEnv"] = search_results["WebEnv"]
            record["QueryKey"] = search_results["QueryKey"]
    return record


def read_response(handle: HTTPResponse) -> str:
    """
    Fully reads an http stream from Entrez, taking into account IncompleteRead exceptions. Potentially useful for
    debugging

    :param handle: Entrez http stream
    :return: text of stream
    """
    data = ""
    while True:
        try:
            data += handle.read()
            break
        except IncompleteRead as ir:
            data += ir.partial
    return data
