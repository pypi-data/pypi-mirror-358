import csv
import dataclasses
import logging
import os
import smtplib
from email.mime.text import MIMEText

import requests
from Bio import Entrez

from .config import JOURNAL_FAILURE_WARNING

logger = logging.getLogger("pub.tools")

JOURNAL_DATA_DIR = os.path.join(os.path.expanduser("~"), ".pubmed")
JOURNAL_DATA_FILE = os.path.join(JOURNAL_DATA_DIR, "journals.csv")

base_path = os.path.dirname(os.path.realpath(__file__))


@dataclasses.dataclass(frozen=True)
class JournalData:
    title: str
    abbr: str
    pissn: str
    eissn: str
    publisher: str
    locator: str
    latest: str
    earliest: str
    freeaccess: str
    openaccess: str
    participation: str
    deposit: str
    url: str


@dataclasses.dataclass(frozen=True)
class AllJournalData:
    atoj: dict[str, str]  # abbreviation -> journal
    jtoa: dict[str, str]  # journal -> abbreviation
    dates: dict[str, tuple[str, str]]  # start and end dates
    full: dict[str, JournalData]


def fetch_journals() -> AllJournalData:
    """
    Gets all journal info from NCBI. This will be cached

    :return: dict
    """
    url = "https://cdn.ncbi.nlm.nih.gov/pmc/home/jlist.csv"

    def _parse_journals(text):
        _atoj = {}
        _jtoa = {}
        dates = {}
        full = {}
        reader = csv.reader(text.split("\n"))
        header = False

        for row in reader:
            if not header:
                header = True
                continue
            if row:
                (
                    title,
                    abbr,
                    pissn,
                    eissn,
                    publisher,
                    locator,
                    latest,
                    earliest,
                    freeaccess,
                    openaccess,
                    participation,
                    deposit,
                    url,
                ) = row
                latest = latest.split(" ")[-1]
                earliest = earliest.split(" ")[-1]
                _atoj[abbr.lower()] = title
                _jtoa[title.lower()] = abbr
                dates[abbr.lower()] = (earliest, latest)
                full[abbr.lower()] = JournalData(*row)
        return AllJournalData(atoj=_atoj, jtoa=_jtoa, dates=dates, full=full)

    response = requests.get(url, timeout=5.0)
    if response.status_code == 200:
        _text = response.text
        with open(JOURNAL_DATA_FILE, "wb") as f:
            f.write(_text.encode("utf-8"))
        return _parse_journals(_text)
    else:
        logger.warning("Could not retrieve journal source, falling back to cache")
        if Entrez.email and JOURNAL_FAILURE_WARNING:
            mailer = smtplib.SMTP("smtp.imsweb.com")
            msg = MIMEText(f"pub.tools could not retrieve journal data from {url}. Check if this source is valid.")
            msg["Subject"] = "[pub.tools] unable to get journal data"
            msg["From"] = "noreply@imsweb.com"
            msg["To"] = "wohnlice@imsweb.com"
            mailer.sendmail(msg["From"], msg["To"], msg.as_string())
            mailer.quit()
        with open(JOURNAL_DATA_FILE, "rb") as f:
            _text = f.read()
        return _parse_journals(_text.decode("utf-8"))


try:
    os.makedirs(JOURNAL_DATA_DIR)
except FileExistsError:
    pass
journals = fetch_journals()


def get_source(cache: bool = False) -> AllJournalData:
    """get source dictionary of journals and abbreviations"""
    global journals
    if not cache:
        try:
            journals = fetch_journals()
        except requests.exceptions.HTTPError:
            pass
        except requests.exceptions.ProxyError:
            pass
    return journals


def get_abbreviations(cache: bool = True) -> dict[str, str]:
    """get the mapping for abbreviation -> journal title"""
    return get_source(cache).atoj


def get_journals(cache: bool = True) -> dict[str, str]:
    """get the mapping for journal -> abbreviation"""
    return get_source(cache).jtoa


def get_dates(cache: bool = True) -> dict[str, tuple[str, str]]:
    """get date range per journal abbreviation

    :param cache:
    :return: dict
    """
    return get_source(cache).dates


def atoj(abbrv: str, cache: bool = True) -> str:
    """get journal title from abbreviation"""
    data = get_abbreviations(cache)
    return data.get(abbrv.lower())


def jtoa(journal: str, cache: bool = True) -> str:
    """get abbreviation from journal title

    :param journal:
    :param cache:
    :return: str
    """
    data = get_journals(cache)
    return data.get(journal.lower())


def atodates(abbrv: str, cache: bool = True) -> tuple[str, str]:
    """get date range from journal abbreviation

    :param abbrv:
    :param cache:
    :return:
    """
    data = get_dates(cache)
    return data.get(abbrv.lower())
