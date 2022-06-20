import itertools
from bs4 import BeautifulSoup
import requests
from thefuzz import process


def get_url_content(url):
    res = requests.get(url)
    if not res.ok:
        raise Exception(res.content)

    return res.content


class Scraper:
    def __init__(self, url, page_type):
        self._base_url = url
        self._type = page_type
        self._set_type_dependent()

    def _set_type_dependent(self):
        if self._type == "lovethegarden":
            self._catalog = "/pl-pl/narzedzia/przewodnik-upraw"
            self._elem_class = "plant__title"
            self._elem_type = "h2"
            self._query_start = "?title="
        elif self._type == "zielonyogrodek":
            self._catalog = "/katalog-roslin"
            self._elem_class = "plant grid"
            self._elem_type = "article"
            self._query_start = "?q="

    def _set_soup(self, content):
        self._soup = BeautifulSoup(content, "html.parser")

    def _get_plant_url(self, plant_name):
        page_content = get_url_content(self._base_url + self._catalog + self._query_start + plant_name[:-1])
        self._set_soup(page_content)

        plants_urls = self._get_plants_urls()
        if not plants_urls:
            raise Exception("No plant found")

        plant_url = process.extract(plant_name, plants_urls)[0][0][1]
        return plant_url

    def _get_plants_urls(self):
        plants = self._soup.find_all(self._elem_type, {"class": self._elem_class})
        plant_urls = []
        for plant in plants:
            plant_a = plant.findChild("a")
            if plant_a:
                if self._type == "lovethegarden":
                    plant_urls.append([plant_a.get("title"), plant_a.get("href")])
                elif self._type == "zielonyogrodek":
                    title = plant_a.findNextSibling().findChild("div", {"class": "title"})
                    plant_urls.append([title.text.strip(), plant_a.get("href")])
        return plant_urls

    def get_text(self, plant_name):
        page_content = get_url_content(self._base_url + self._get_plant_url(plant_name))
        self._set_soup(page_content)
        content = self._soup.find_all("p")
        text_content = list(itertools.chain.from_iterable([p.text.strip().split(". ") for p in content]))
        return text_content
