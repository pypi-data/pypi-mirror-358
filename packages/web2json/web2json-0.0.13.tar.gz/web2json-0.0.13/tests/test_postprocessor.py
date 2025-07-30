import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from web2json.postprocessor import PostProcessor


def test_postprocessor_recovers_url_on_invalid_json():
    preprocessed = "download ftp://example.com/file.txt"
    pp = PostProcessor({"ftp_download": r"(ftp://\S+)"})
    result = pp.process("not json", preprocessed)
    assert result == {"ftp_download": "ftp://example.com/file.txt"}


def test_postprocessor_nested_field():
    preprocessed = "Dataset Developer (https://example.com)"
    pp = PostProcessor({"dataset_developer.affiliation_url": r"(https://[^\s)]+)"})
    result = pp.process("{}", preprocessed)
    assert result == {"dataset_developer": {"affiliation_url": "https://example.com"}}


def test_postprocessor_does_not_override(monkeypatch):
    response = json.dumps({"ftp_download": "ftp://existing.com/file.txt"})
    preprocessed = "ftp://example.com/file.txt"
    pp = PostProcessor({"ftp_download": r"(ftp://\S+)"})
    result = pp.process(response, preprocessed)
    assert result["ftp_download"] == "ftp://existing.com/file.txt"


def test_postprocessor_extracts_notable_features():
    html = (
        "Notable Features\n"
        "First item\n"
        "Second item\n"
        "Contacts"
    )
    pp = PostProcessor()
    result = pp.process("{}", html)
    assert result == {"notable_features": ["First item", "Second item"]}


def test_postprocessor_extracts_categories_keywords():
    html = (
        "Categories\n"
        "Land:\n"
        "Plate Tectonics\n"
        "People:\n"
        "History\n"
        "Water:\n"
        "Tsunamis\n"
        "Keywords\n"
        "Earthquakes\n"
        "History\n"
        "Oceans\n"
        "Tsunamis\n"
        "Wave Heights\n"
        "Contacts"
    )
    pp = PostProcessor()
    result = pp.process("{}", html)
    assert result["categories"] == {
        "Land": ["Plate Tectonics"],
        "People": ["History"],
        "Water": ["Tsunamis"],
    }
    assert result["keywords"] == [
        "Earthquakes",
        "History",
        "Oceans",
        "Tsunamis",
        "Wave Heights",
    ]


def test_postprocessor_overrides_categories_keywords():
    html = (
        "Categories\n"
        "Land:\n"
        "Plate Tectonics\n"
        "People:\n"
        "History\n"
        "Water:\n"
        "Tsunamis\n"
        "Keywords\n"
        "Earthquakes\n"
        "History\n"
        "Oceans\n"
        "Tsunamis\n"
        "Wave Heights\n"
        "Contacts"
    )
    response = json.dumps({"categories": {"SOS": ["Other"]}, "keywords": ["one"]})
    pp = PostProcessor()
    result = pp.process(response, html)
    assert result["categories"] == {
        "Land": ["Plate Tectonics"],
        "People": ["History"],
        "Water": ["Tsunamis"],
    }
    assert result["keywords"] == [
        "Earthquakes",
        "History",
        "Oceans",
        "Tsunamis",
        "Wave Heights",
    ]


def test_postprocessor_last_link_match():
    html = (
        "Dataset Developer\n"
        "Permalink (https://example.com/perma)\n"
        "Org (https://org.com)\n"
        "Name"
    )
    pp = PostProcessor({"dataset_developer.affiliation_url": r"Dataset Developer.*?Permalink.*?\(https?://[^\\s)]+\).*?\((https?://[^\\s)]+)\)"})
    result = pp.process("{}", html)
    assert result == {
        "dataset_developer": {
            "affiliation_url": "https://org.com",
            "affiliation": "Org",
            "name": "Name",
        }
    }


def test_postprocessor_extracts_date_and_contacts():
    html = (
        "Added to the Catalog\n"
        "24 Aug. 2022\n"
        "Dataset Developer\n"
        "Org (https://org.com)\n"
        "Jane Doe\n"
        "Dataset Vis Developer\n"
        "Org2 (https://org2.com)\n"
        "John Smith"
    )
    pp = PostProcessor({
        "dataset_developer.affiliation_url": r"Org \((https?://[^\\s)]+)\)",
        "vis_developer.affiliation_url": r"Org2 \((https?://[^\\s)]+)\)"
    })
    result = pp.process("{}", html)
    assert result["date_added"] == "24 Aug. 2022"
    assert result["dataset_developer"] == {
        "affiliation": "Org",
        "name": "Jane Doe",
        "affiliation_url": "https://org.com",
    }
    assert result["vis_developer"] == {
        "affiliation": "Org2",
        "name": "John Smith",
        "affiliation_url": "https://org2.com",
    }


def test_postprocessor_description():
    html = (
        "Description\n"
        "Permalink (https://perma)\n"
        "This is the text.\n"
        "Contacts"
    )
    pp = PostProcessor()
    result = pp.process("{}", html)
    assert result["description"] == "This is the text."


def test_postprocessor_css_selectors():
    html = "<dl><dt><span>Download</span></dt><dd><a class='ftp' href='ftp://x'>F"\
           "TP</a><a class='vid' href='movie.mov'>Vid</a></dd></dl>"
    pp = PostProcessor(css_selectors={
        "ftp_download": {"selector": "a.ftp", "attr": "href"},
        "movie_preview": {"selector": "a.vid", "attr": "href"},
    })
    result = pp.process("{}", preprocessed="irrelevant", html=html)
    assert result["ftp_download"] == "ftp://x"
    assert result["movie_preview"] == "movie.mov"


def test_postprocessor_css_list():
    html = "<ul id='feat'><li>A</li><li>B</li></ul>"
    pp = PostProcessor(css_selectors={"notable_features": {"selector": "ul#feat li", "list": True}})
    result = pp.process("{}", preprocessed="", html=html)
    assert result["notable_features"] == ["A", "B"]
