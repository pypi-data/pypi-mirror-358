import warnings
from collections.abc import Callable
from functools import wraps
from io import StringIO

import deprecation
from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning
from lxml import etree as et

from .config import VERSION
from .schema import Abstract
from .schema import BookRecord
from .schema import ChapterRecord
from .schema import EntrezRecord
from .schema import JournalRecord
from .schema import Person

WRAPPER_TAG = "span"
PUNC_ENDINGS = (".", "?", "!")


def formatted_citation(func: Callable):
    """The purpose here is to fix bad HTML tags from PubMed (or just Biopython?) where there are escaped
    HTML entities and unescaped ampersands
    """

    @wraps(func)
    def wrapper(**kwargs):
        text = func(**kwargs)
        try:
            et.XML(text)
        except et.XMLSyntaxError:
            # try to escape ampersands, prevent double escape
            _marker = "$$_pubtools_"
            escape_vals = ["amp", "lt", "gt", "quot"]

            # set these aside so we can replace &
            for val in escape_vals:
                text = text.replace(f"&{val};", f"{_marker}{val};")

            text = text.replace("&", "&amp;")

            # put them back
            for val in escape_vals:
                text = text.replace(f"{_marker}{val};", f"&{val};")
        if kwargs.get("use_abstract"):
            return text.replace("\n", "").strip()
        else:
            return text.strip()

    return wrapper


def punctuate(text: str, punctuation: str, space: str = "") -> str:
    """Applies a punctuation mark to the text, with `space` used for certain punctuation"""
    with warnings.catch_warnings(action="ignore", category=MarkupResemblesLocatorWarning):
        soup = BeautifulSoup(text, "html.parser")
        element = soup.find("a")  # the inside of a link may end in a period
    if not text:
        return text
    if (
        (punctuation in PUNC_ENDINGS and text[-1] in PUNC_ENDINGS)
        or (element and element.get_text()[-1] in PUNC_ENDINGS)
        or (punctuation not in PUNC_ENDINGS and text[-1] == punctuation)
    ):
        return text + space
    elif text[-1] == " ":
        return punctuate(text.strip(), punctuation, space)
    else:
        return text + punctuation + space


def period(text: str) -> str:
    return punctuate(text, ".", " ")


def comma(text: str) -> str:
    return punctuate(text, ",", " ")


def colon(text: str) -> str:
    return punctuate(text, ":", " ")


def colon_no_space(text: str) -> str:
    return punctuate(text, ":", "")


def semi_colon(text: str) -> str:
    return punctuate(text, ";", " ")


def semi_colon_no_space(text: str) -> str:
    return punctuate(text, ";", "")


@deprecation.deprecated(
    deprecated_in="5.0", removed_in="6.0", current_version=VERSION, details="Use `citation_author` instead."
)
def cookauthor(author: Person | dict, suffix: bool = True):
    return citation_author(author, use_suffix=suffix)


def citation_author(author: Person | dict, use_suffix: bool = True) -> str:
    """combine authors into one string"""
    if not isinstance(author, Person):
        author = {
            "last_name": author.get("lname") or author.get("last_name"),
            "first_name": author.get("fname") or author.get("first_name"),
            "collective_name": author.get("cname") or author.get("collective_name"),
            "initial": author.get("iname") or author.get("initial"),
            "suffix": author.get("suffix") or author.get("suffix"),
        }
        return citation_author(Person(**author), use_suffix=use_suffix)
    initial = author.initial if author.initial else (author.first_name[0].upper() if author.first_name else "")
    lname = author.collective_name or author.last_name
    parts = [lname, initial]
    if use_suffix and author.suffix:
        parts.append(author.suffix)
    return " ".join([p.rstrip() for p in parts if p])


def citation_editors(editors: list[Person]) -> str:
    """combine editors into one string and pluralize if appropriate"""
    plural = "s" if len(editors) > 1 else ""
    editors = ", ".join([citation_author(e).replace(",", " ") for e in editors])
    return period(f"{editors}, editor{plural}")


@formatted_citation
def book_citation(
    authors: list[Person | dict] = (),
    editors: list[Person | dict] = (),
    title: str = "",
    pubdate: str = "",
    pagination: str = "",
    edition: str = "",
    series: str = "",
    pubplace: str = "",
    publisher: str = "",
    html: bool = False,
    publication: BookRecord = None,
    **kwargs,
) -> str:
    """book citation

    You can pass each field separately, or pass an EntrezRecord object
    """
    if publication:
        return book_citation(**publication.asdict(), html=html)
    out = StringIO()
    if html:
        out.write(f'<{WRAPPER_TAG} class="citation">')
    if editors and not authors:
        out.write(citation_editors(editors))
    if authors:
        out.write(period(", ".join([citation_author(a) for a in authors])))
    if title:
        out.write(period(title))
    if edition:
        out.write(period(edition))
    if editors and authors:
        out.write(citation_editors(editors))
    if pubplace:
        if publisher:
            out.write(colon(pubplace))
        else:
            out.write(period(pubplace))
    if publisher:
        out.write(semi_colon(publisher)) if pubdate else out.write(period(publisher))
    if pubdate:
        out.write(period(pubdate))
    if pagination:
        out.write(f"p. {period(pagination)}")
    if series:
        out.write(f"({series})")
    out = out.getvalue().strip()
    if html:
        out += f"</{WRAPPER_TAG}>"
    return out


@formatted_citation
def chapter_citation(
    authors: list[Person | dict] = (),
    editors: list[Person | dict] = (),
    title: str = "",
    pubdate: str = "",
    pagination: str = "",
    edition: str = "",
    series: str = "",
    pubplace: str = "",
    publisher: str = "",
    booktitle: str = "",
    html: bool = False,
    publication: ChapterRecord = None,
    **kwargs,
) -> str:
    """book chapter citation


    You can pass each field separately, or pass an EntrezRecord object
    """
    if publication:
        return chapter_citation(**publication.asdict(), html=html)
    out = StringIO()
    if html:
        out.write(f'<{WRAPPER_TAG} class="citation">')
    if editors and not authors:
        out.write(citation_editors(editors))
    if authors:
        out.write(period(", ".join([citation_author(a).replace(",", " ") for a in authors])))
    if title:
        out.write(period(title))
    if edition or editors or booktitle:
        out.write("In: ")
    if editors and authors:
        out.write(citation_editors(editors))
    if booktitle:
        out.write(period(booktitle))
    if edition:
        out.write(period(edition))
    if pubplace:
        if publisher:
            out.write(colon(pubplace))
        else:
            out.write(period(pubplace))
    if publisher:
        if pubdate:
            out.write(semi_colon(publisher))
        else:
            out.write(period(publisher))
    if pubdate:
        out.write(period(pubdate))
    if pagination:
        out.write(f"p. {period(pagination)}")
    if series:
        out.write(f"({series})")
    out = out.getvalue().strip()
    if html:
        out += f"</{WRAPPER_TAG}>"
    return out


@formatted_citation
def conference_citation(
    authors: list[Person | dict] = (),
    editors: list[Person | dict] = (),
    title: str = "",
    pubdate: str = "",
    pagination: str = "",
    pubplace: str = "",
    place: str = "",
    conferencename: str = "",
    conferencedate: str = "",
    publisher: str = "",
    html: bool = False,
    publication: EntrezRecord = None,
    **kwargs,
) -> str:
    """conference citation

    You can pass each field separately, or pass an EntrezRecord object
    """
    if publication:
        return conference_citation(**publication.asdict(), html=html)
    out = StringIO()
    if html:
        out.write(f'<{WRAPPER_TAG} class="citation">')
    if editors and not authors:
        out.write(citation_editors(editors))
    if authors:
        out.write(period(", ".join([citation_author(a).replace(",", " ") for a in authors])))
    if title:
        out.write(period(title))
    if editors and authors:
        out.write(citation_editors(editors))
    if conferencename and html:
        out.write(semi_colon(f"<i>Proceedings of {conferencename}</i>"))
    elif conferencename:
        out.write(semi_colon(f"Proceedings of {conferencename}"))
    if conferencedate:
        if place or pubdate or publisher:
            out.write(semi_colon(conferencedate))
        else:
            out.write(period(conferencedate))
    if place:
        out.write(period(place))
    if pubplace:
        if publisher or pubdate:
            out.write(colon(pubplace))
        else:
            out.write(period(pubplace))
    if publisher:
        if pubdate:
            out.write(semi_colon(publisher))
        else:
            out.write(period(publisher))
    if pubdate:
        out.write(period(pubdate))
    if pagination:
        out.write(f"p. {period(pagination)}")
    out = out.getvalue().strip()
    if html:
        out += f"</{WRAPPER_TAG}>"
    return out


@formatted_citation
def journal_citation(
    authors: list[Person | dict] = (),
    title: str = "",
    journal: str = "",
    pubdate: str = "",
    volume: str = "",
    issue: str = "",
    pagination: str = "",
    abstract: list[Abstract] | None = None,
    pubmodel: str = "Print",
    edate: str = "",
    doi: str = "",
    pmid: str = "",
    journal_abbreviation: str = "",
    use_abstract: bool = False,
    html: bool = False,
    link: bool = False,
    publication: JournalRecord = None,
    **kwargs,
) -> str:
    """journal citation"""
    if publication:
        return journal_citation(**publication.asdict(), html=html, use_abstract=use_abstract, link=link)
    if journal_abbreviation:
        journal = journal_abbreviation
    if not abstract:
        abstract = {}
    out = StringIO()
    if html:
        out.write(f'<{WRAPPER_TAG} class="citation">')
    if authors:
        out.write(period(", ".join([citation_author(a).replace(",", " ") for a in authors if a])))
    if title:
        if link and pmid:
            out.write(
                period(f'<a class="citation-pubmed-link" href="https://pubmed.ncbi.nlm.nih.gov/{pmid}/">{title}</a>')
            )
        else:
            out.write(period(title))
    if journal and html:
        out.write(f"<i>{journal.strip()}</i> ")
    elif journal:
        out.write(period(journal.strip()))

    if pubmodel in ("Print", "Electronic", "Print-Electronic"):  # use the publication date
        date = pubdate
    elif pubmodel in ("Electronic-Print", "Electronic-eCollection"):  # use the electronic date
        date = edate
    else:
        date = pubdate or edate

    if date:
        if pagination and not (volume or issue):
            out.write(colon(date))
        elif volume or issue:
            out.write(semi_colon_no_space(date))
        else:
            out.write(period(date))
    if volume:
        if pagination and not issue:
            out.write(colon_no_space(volume))
        elif pagination:
            out.write(volume)
        else:
            out.write(period(volume))
    if issue:
        if pagination:
            out.write(colon_no_space(f"({issue})"))
        else:
            out.write(period(f"({issue})"))
    if pagination:
        out.write(period(pagination))
    if pubmodel in ("Print-Electronic",) and edate:
        out.write("Epub " + period(edate))
    if pubmodel in ("Electronic-Print",) and pubdate:
        out.write("Print " + period(pubdate))
    if pubmodel in ("Electronic-eCollection",):
        if pubdate and doi:
            out.write(f"doi: {doi}. eCollection {period(pubdate)}")
        elif pubdate:
            out.write(f"eCollection {period(pubdate)}")

    if use_abstract:
        out.write("<br/>")
        abstracts = []
        for seg in abstract:
            abst = seg.get("label") or ""
            abst += (abst and ": ") or ""
            abst += seg.get("text") or ""
            if abst:
                abstracts.append(f"<p>{abst}</p>")
        abstract = " ".join(abstracts)
        if abstract:
            out.write(
                f'<div class="citationAbstract"><p class="abstractHeader"><strong>Abstract</strong></p>{abstract}</div>'
            )
    out = out.getvalue().strip()
    if html:
        out += f"</{WRAPPER_TAG}>"
    return out


@formatted_citation
def monograph_citation(
    authors: list[Person | dict] = (),
    title: str = "",
    pubdate: str = "",
    series: str = "",
    pubplace: str = "",
    weburl: str = "",
    reportnum: str = "",
    publisher: str = "",
    serieseditors: list[str] = (),
    html: bool = False,
    publication: EntrezRecord = None,
    **kwargs,
) -> str:
    """book chapter citation"""
    if publication:
        return monograph_citation(**publication.asdict(), html=html)
    out = StringIO()
    if html:
        out.write(f'<{WRAPPER_TAG} class="citation">')
    if serieseditors and not authors:
        out.write(
            period(
                f"{', '.join([e.replace(',', ' ') for e in serieseditors])}, "
                f"editor{'s' if len(serieseditors) > 1 else ''}"
            )
        )
    if authors:
        out.write(semi_colon(", ".join([citation_author(a).replace(",", " ") for a in authors])))
    if title:
        out.write(period(title))
    if series:
        out.write(period(series))
    if serieseditors and authors:
        out.write(
            period(
                f"{', '.join([e.replace(',', ' ') for e in serieseditors])}, "
                f"editor{'s' if len(serieseditors) > 1 else ''}"
            )
        )
    if pubplace:
        if publisher:
            out.write(colon(pubplace))
        elif pubdate:
            out.write(semi_colon(pubplace))
        else:
            out.write(period(pubplace))
    if publisher:
        if pubdate:
            out.write(semi_colon(publisher))
        else:
            out.write(period(publisher))
    if pubdate:
        out.write(period(pubdate))
    if reportnum:
        out.write(period(reportnum))
    if weburl:
        out.write(f"Available at {weburl}.")
    out = out.getvalue().strip()
    if html:
        out += f"</{WRAPPER_TAG}>"
    return out


@formatted_citation
def report_citation(
    authors: list[Person | dict] = (),
    editors: list[Person | dict] = (),
    title: str = "",
    pubdate: str = "",
    pagination: str = "",
    series: str = "",
    pubplace: str = "",
    weburl: str = "",
    reportnum: str = "",
    publisher: str = "",
    html: bool = False,
    publication: EntrezRecord = None,
    **kwargs,
) -> str:
    """book chapter citation"""
    if publication:
        return report_citation(**publication.asdict(), html=html)
    out = StringIO()
    if html:
        out.write(f'<{WRAPPER_TAG} class="citation">')
    if editors and not authors:
        out.write(citation_editors(editors))
    if authors:
        out.write(period(", ".join([citation_author(a).replace(",", " ") for a in authors])))
    if title:
        out.write(period(title))
    if series:
        out.write(period(series))
    if editors and authors:
        out.write(citation_editors(editors))
    if pubplace:
        if publisher:
            out.write(colon(pubplace))
        elif pubdate:
            out.write(semi_colon(pubplace))
        else:
            out.write(period(pubplace))
    if publisher:
        if pubdate:
            out.write(semi_colon(publisher))
        else:
            out.write(period(publisher))
    if pubdate:
        out.write(period(pubdate))
    if reportnum:
        out.write(period(reportnum))
    if pagination:
        out.write(period(f"p. {pagination}"))
    if weburl:
        out.write(f"Available at {weburl}.")
    out = out.getvalue().strip()
    if html:
        out += f"</{WRAPPER_TAG}>"
    return out


@formatted_citation
def publication_citation(
    publication: JournalRecord | BookRecord | ChapterRecord,
    html: bool = False,
    use_abstract: bool = False,
    link: bool = False,
) -> str:
    """Undefined publication type. Only usable with pub types that can be retrieved from Pubmed.
        Example usage:

        .. code-block:: python

            from pub.tools import entrez
            from pub.tools import citations
            if pub := entrez.get_publication(pmid=12345678):
                 citations.publication_citation(publication=pub)

    Optional parameters:
        html = will render the citation with html tags
        use_abstract = will include the abstract after the citation (requires html=True)
        link = will include PubMed link (requires html=True and pmid)
    """
    pub_types = {"journal": journal_citation, "book": book_citation, "chapter": chapter_citation}
    return pub_types[publication.pub_type](publication=publication, html=html, use_abstract=use_abstract, link=link)
