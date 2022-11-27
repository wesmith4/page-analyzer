import requests
import streamlit as st
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import TypedDict
import json
from wordcloud import WordCloud, STOPWORDS
from spacy import load

# Load the spaCy model
nlp = load("./models/en_core_web_sm/")


class PageMetaData(TypedDict):
    title_tag: str
    meta_description: str
    h1: str


@st.cache
def get_text_from_url(url: str) -> str:
    response = requests.get(url)
    return response.text


class Page:
    def __init__(self, url: str):
        self.url = url
        self.text = get_text_from_url(url)
        self.soup = BeautifulSoup(self.text, "html.parser")

    def get_soup(self) -> BeautifulSoup:
        return self.soup

    def get_metadata(self) -> PageMetaData:
        self.metadata: PageMetaData = {
            "title_tag": self.soup.find("title").text,
            "meta_description": self.soup.find(
                "meta", {"name": "description"}
            ).get("content"),
            "h1": self.soup.find("h1").text,
        }

        return self.metadata

    def get_headings(self, levels: list[str] = ["h2"]):
        return {
            level: list(map(
                lambda tag: tag.text,
                self.soup.find_all(level)
            )) for level in levels
        }

    def get_schema_tags(self) -> ResultSet:
        return self.soup.find_all(
            "script",
            {"type": "application/ld+json"}
        )

    def get_schema_objects(self) -> list[dict]:
        schema_script_tags = self.soup.find_all(
            "script",
            {"type": "application/ld+json"}
        )

        schema_objects: list[dict] = list(map(
            lambda tag: json.loads(tag.text),
            schema_script_tags
        ))

        return schema_objects

    def get_schema_object_from_tag(self, tag: Tag) -> dict:
        return json.loads(tag.text)

    def get_wordcloud(self) -> WordCloud:
        paragraphs = list(map(lambda tag: tag.text, self.soup.find_all("p")))
        text = " ".join(paragraphs)

        stopwords = set(STOPWORDS)

        cloud = WordCloud(stopwords=stopwords, max_words=40).generate(text)
        return cloud

    def get_entities(self, text: str):
        doc = nlp(text)
        return doc.ents

    def get_concatenated_paragraphs(self) -> str:
        paragraphs = list(map(
            lambda tag: tag.text.strip(),
            self.soup.find_all("p")
        ))
        return " ".join(paragraphs)
