import json
import re
from io import BytesIO

import requests
import xml.etree.ElementTree as et

from .formatting import alphanum, format_date_str
import dataclasses


# DISCLAIMER: the authors do not use any of this anymore. Use at own risk, bug reports welcome


@dataclasses.dataclass
class IsbnData:
    book_title: str = ""
    language: str = ""
    publisher: str = ""
    authors: list = dataclasses.field(default_factory=list)
    editors: list = dataclasses.field(default_factory=list)
    abstract: str = ""
    pubdate: str = ""
    google_books_link: str = ""

    def get(self, key):  # dict like
        if hasattr(self, key):
            return self[key]

    def __getitem__(self, key):  # dict like
        return getattr(self, key)

    def __setitem__(self, key, value):  # dict like
        return setattr(self, key, value)


@dataclasses.dataclass
class IsbnOpener:
    api_key: str = ""
    root_url: str = ""  # for construction
    url: str = ""  # for displays
    name: str = "Default opener"

    def get_publication(self, isbn: str) -> IsbnData:
        """Should always return an IsbnData object"""
        return IsbnData()


class IsbnDbOpener(IsbnOpener):
    """This requires a paid service now, not fully tested"""

    root_url = "https://api.isbndb.com/{endpoint}/{term}"
    name = "ISBNdb"

    def url(self, term):
        return self.root_url.format(api_key=self.api_key, endpoint="book", term=term)

    def get_url(self, endpoint, term):
        url = self.root_url.format(endpoint=endpoint, term=term)
        headers = {"X-API-KEY": self.api_key}
        response = requests.get(url, headers=headers, timeout=2.0)
        if response.status_code == 200:
            return json.loads(response.text)

    def get_publication(self, isbn):
        data = IsbnData()
        isbn = alphanum(isbn)
        book = self.get_url(endpoint="book", term=isbn)
        if book and book.get("data"):
            book = book["data"][0]
            data["title"] = book.get("title_long") or book.get("title")
            data["language"] = book.get("language")
            data["authors"] = [b.get("name_latin") or b["name"] for b in book.get("author_data")]
            data["publisher"] = book.get("publisher_name")
            data["abstract"] = book["summary"]
            return data


class GoogleBooksAPIOpener(IsbnOpener):
    root_url = "https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={api_key}"
    name = "Google Books API"

    def url(self, isbn):
        return self.root_url.format(api_key=self.api_key, isbn=isbn)

    def get_url(self, isbn):
        response = requests.get(self.url(isbn), timeout=2.0)  # requests module fails to validate SSL cert?
        return response.json()

    def get_publication(self, isbn):
        data = IsbnData()
        isbn = alphanum(isbn)
        book = self.get_url(isbn)
        if book and book["totalItems"]:
            book = book["items"][0]["volumeInfo"]
            data["title"] = book["title"]
            data["language"] = book.get("language")
            data["authors"] = book.get("authors") or []
            data["publisher"] = book.get("publisher")
            data["abstract"] = book.get("description")
            if book.get("publishedDate"):
                data["pubdate"] = format_date_str(book["publishedDate"])
            data["google_books_link"] = book["previewLink"]
            return data


class WorldCatOpener(IsbnOpener):
    root_url = "http://classify.oclc.org/classify2/Classify?isbn={isbn}&summary=true"
    name = "WorldCat"

    def url(self, term):
        return self.root_url.format(isbn=term)

    def get_url(self, isbn):
        response = requests.get(self.root_url.format(isbn=isbn), timeout=2.0)
        if response.status_code == 200:
            return response.text

    def get_publication(self, isbn):
        data = IsbnData()
        isbn = alphanum(isbn)
        source = self.get_url(isbn)

        if source:
            tree = et.parse(BytesIO(source.encode("utf-8")))
            ns = "http://classify.oclc.org"

            authors = []
            editors = []
            root = tree.getroot()
            _authors = root.find(f"{{{ns}}}authors")
            if _authors and _authors is not None:
                for author in _authors.findall(f"{{{ns}}}author"):
                    author = author.text
                    brkt_pattern = r"\[(.*?)\]"
                    brkt = re.search(brkt_pattern, author)
                    if brkt:
                        brkt_value = brkt.group(1)
                        author_name = author.split(brkt.group())[0].strip()
                        # what values are allowed here? Just try for editor for now
                        for role in brkt_value.split(";"):
                            role = role.strip()
                            if role == "Editor" and author_name not in editors:
                                editors.append(author_name)
                            elif role == "Author" and author_name not in authors:
                                authors.append(author_name)
                    else:
                        authors.append(author)
                data["authors"] = authors
                data["editors"] = editors
                data["title"] = ""
                data["title"] = root.find(f"{{{ns}}}work").attrib["title"]
                return data
