# -*- coding: utf-8 -*-
"""Module description

This module does great things.

Example:
    $ python3 great_things.py positional_argument --keyword_argument 1

Style guide: https://www.python.org/dev/peps/pep-0008/
"""

import os
import json
import yaml
import requests
from typing import List, Union

# Implementation constants
script_dirname, script_filename = os.path.split(os.path.abspath(__file__))
project_root_dir = os.path.dirname(script_dirname)


class CrossRefClient(object):

    def __init__(self, accept="text/x-bibliography; style=apa", timeout=3):
        """
        # Defaults to APA biblio style

        # Usage:
        s = CrossRefClient()
        print s.doi2apa("10.1038/nature10414")
        """
        self.headers = {"accept": accept}
        self.timeout = timeout

    def query(self, doi, q={}):
        if doi.startswith("https://"):
            url = doi
        else:
            url = "http://dx.doi.org/" + doi
        r = requests.get(url, headers = self.headers)
        return r

    def doi2apa(self, doi):
        self.headers["accept"] = "text/x-bibliography; style=apa"
        return self.query(doi).text

    def doi2turtle(self, doi):
        self.headers["accept"] = "text/turtle"
        return self.query(doi).text

    def doi2json(self, doi):
        self.headers["accept"] = "application/vnd.citationstyles.csl+json"
        return self.query(doi).json()

keys = ["indexed", "reference-count", "publisher", "issue", "funder", "content-domain", "published-print", "DOI", "type", "created", "update-policy", "source", "is-referenced-by-count", "title", "prefix", "volume", "author", "member", "published-online", "reference", "container-title", "original-title", "language", "link", "deposited", "score", "subtitle", "short-title", "issued", "references-count", "journal-issue", "alternative-id", "URL", "relation", "ISSN", "container-title-short", "article-number"]


def render_author_names(response):
    name = []
    for _item in response["author"]:
        given_in = _item["given"].split(" ")
        given = "".join([_name[0] + "." for _name in given_in])
        name.append(_item["family"] + ", " + given +", ")
    return "".join(name[0:-1]) + "and " + name[-1][0:-2]

def render_pub_date(response):
    if type(response.get("created").get("date-parts")) == list:
        if type(response.get("created").get("date-parts")[0]) == list:
            return str(response.get("created").get("date-parts")[0][0])
    return None

def render_title(response):
    if response.get("title") is not None:
        return response.get("title")
    return None

def is_preprint(response):
    return response.get("subtype") == "preprint"

def render_journal_title(response):
    if is_preprint(response):
        return response.get("institution")[0].get("name")

    if not len(response.get("container-title")):
        return None

    return response.get("container-title")

def render_journal_volume(response):
    if response.get("volume") is not None:
        return str(response.get("volume"))
    return None

def render_journal_issue(response):
    if response.get("issue") is not None:
        return str(response.get("issue"))
    return None


def render_journal_pages(response):
    if response.get("pages") is not None:
        return response.get("pages")
    if response.get("page") is not None:
        return response.get("page")
    return None

def render_doi(response):
    if response.get("DOI") is not None:
        return response.get("DOI")
    if response.get("URL") is not None:
        return response.get("URL")
    return None

def render_url(response):
    if response.get("URL") is not None:
        return response.get("URL")
    return None

def render_issn(response):
    if response.get("ISSN") is not None:
        return response.get("ISSN")
    return None

def get_publication_info(response: dict):
    authors = render_author_names(response)
    year = render_pub_date(response)
    title = render_title(response)
    journal = render_journal_title(response)
    volume = render_journal_volume(response)
    issue = render_journal_issue(response)
    pages = render_journal_pages(response)
    issn = render_issn(response)
    url = render_url(response)
    doi = render_doi(response)
    preprint = is_preprint(response)
    reference = {
        "authors": authors,
        "year": year,
        "title": title,
        "journal": journal,
        "volume": volume,
        "issue": issue,
        "pages": pages,
        "issn": issn,
        "url": url,
        "doi": doi,
        "preprint": preprint,
    }
    return get_html(reference)

def get_html(reference):
    authors = reference.get("authors")
    url = reference.get("url")
    year = reference.get("year")
    title = reference.get("title")
    journal = reference.get("journal")
    volume = reference.get("volume")
    issue = reference.get("issue")
    pages = reference.get("pages")
    doi = reference.get("doi")
    reference["html"] = "\n\t<li>\n\t\t<p>\n\t\t\t{}\n\t\t</p>\n\t</li>".format(fmt_citation(reference))
    return reference

def fmt_citation(citation: dict):
    fmt = "{authors} ({year}). <a href=\"{url}\" target=\"_blank\">{title}</a>. {journal}, {volume}({issue}), {pages}. {doi}"

    fmt_no_issue = "{authors} ({year}). <a href=\"{url}\" target=\"_blank\">{title}</a>. {journal}, {volume}, {pages}. {doi}"

    fmt_no_pages = "{authors} ({year}). <a href=\"{url}\" target=\"_blank\">{title}</a>. {journal}, {volume}({issue}). {doi}"

    fmt_no_issue_no_pages = "{authors} ({year}). <a href=\"{url}\" target=\"_blank\">{title}</a>. {journal}, {volume}. {doi}"

    fmt_no_volume_issue_no_pages = "{authors} ({year}). <a href=\"{url}\" target=\"_blank\">{title}</a>. {journal}. {doi}"

    if citation.get("volume") is None and citation.get("issue") is None and citation.get("pages") is None:
        return fmt_no_volume_issue_no_pages.format(**citation)
    if citation.get("issue") is None and citation.get("pages") is None:
        return fmt_no_issue_no_pages.format(**citation)
    if citation.get("issue") is None and citation.get("pages") is not None:
        return fmt_no_issue.format(**citation)
    if citation.get("pages") is None and citation.get("issue") is not None:
        return fmt_no_pages.format(**citation)
    return fmt.format(**citation)

def get_contributions_json(json_file) -> dict:
    with open(json_file, "rb") as j:
        d = json.load(j)
    return d

def write_contributions_json(json_file, contributions):
    with open(json_file, "w") as j:
        json.dump(contributions, j, indent=4)

def write_markdown(file, string):
    with open(file, "w") as markdown_file:
        markdown_file.write(string)

def get_config(config_file: str) -> dict:
    with open(config_file, "rb") as config_yaml:
        config = yaml.safe_load(config_yaml)
    return config

def get_config_section(config: dict, section: str) -> Union[None, List, dict]:
    return config.get(section)

def get_citation(doi: str) -> Union[None, str]:
    header = {"Accept": "text/x-bibliography; style=apa"}
    response = requests.get(doi, headers=header)
    if response.status_code == 200:
        return response.text
    else:
        return None

if __name__ == "__main__":
    config_file = os.path.join(
        project_root_dir.replace("assets", ""), "_config.yml"
    )
    contributions_json_file = os.path.join(
        script_dirname, "contributions.json"
    )
    publications_markdown_file = os.path.join(
        project_root_dir.replace("assets", ""), "publications.md"
    )
    preprints_markdown_file = os.path.join(
        project_root_dir.replace("assets", ""), "preprints.md"
    )
    dois = get_config_section(get_config(config_file), "dois")
    client = CrossRefClient()
    references = get_contributions_json(contributions_json_file)
    indexed_dois = [list(item.keys())[0] for item in references]
    detected_new_dois = False
    for doi in dois:
        if doi not in indexed_dois:
            print("Detected new DOI in _config.yml")
            detected_new_dois = True
            response = client.doi2json(doi)
            citation = get_publication_info(response)
            references.append({doi: citation})

    if detected_new_dois:
        write_contributions_json(contributions_json_file, references)
        publications_section = """[](#Publications)
## **Publications**
***
<ul>
"""
        preprint_section = """[](#pre-prints)
## **Pre-prints**
***
<ul>
"""
    if detected_new_dois:
        for doi in references:
            doi_key = list(doi.keys())[0]
            pub_info = doi[doi_key]
            if not pub_info.get("preprint"):
                publications_section+=pub_info.get("html")
            else:
                preprint_section+=pub_info.get("html")
        preprint_section+="\n</ul>"
        publications_section+="\n</ul>"
        write_markdown(publications_markdown_file, publications_section)
        write_markdown(preprints_markdown_file, preprint_section)
