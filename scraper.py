import itertools
from bs4 import BeautifulSoup
import requests
from thefuzz import process
import re


def get_url_content(url):
    res = requests.get(url)
    if not res.ok:
        raise Exception(res.status_code)

    return res.content


def _clean(text):
    text = re.sub('\n ', '', str(text))
    text = re.sub('\n', ' ', str(text))
    text = re.sub("'s", '', str(text))
    text = re.sub("-", ' ', str(text))
    text = re.sub("— ", '', str(text))
    text = re.sub('\"', '', str(text))

    return text


def _sentences(text):
    text = re.split('[.?]', text)
    clean_sent = []
    for sent in text:
        clean_sent.append(sent)
    return clean_sent


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
        content = ""
        if self._type == "lovethegarden":
            content = self._soup.find("article", {"class": "node--plant-full"}).find_all("p")
        elif self._type == "zielonyogrodek":
            content = self._soup.find("div", {"class": "article-text"}).find_all("p")

        text_content = " ".join(list([p.text for p in content]))
        text_content = _clean(text_content)
        text_content = _sentences(text_content)
        return text_content

    def get_all_plants(self):
        page_content = ""
        if self._type == "lovethegarden":
            page_content = get_url_content(self._base_url + self._catalog + "/?field_plant_category_target_id=All" + "&"
                                           + "page=" + str(0))

        self._set_soup(page_content)
        plants_names = []
        max_page_num = self._get_max_page_num()
        for i in range(max_page_num):
            if self._type == "lovethegarden":
                page_content = get_url_content(self._base_url + self._catalog + "/?field_plant_category_target_id=All" +
                                               "&" + "page=" + str(i))

            self._set_soup(page_content)
            plants = self._soup.find_all(self._elem_type, {"class": self._elem_class})
            for plant in plants:
                plant_a = plant.findChild("a")
                if plant_a:
                    if self._type == "lovethegarden":
                        plants_names.append(plant_a.get("title"))

        return plants_names

    def _get_max_page_num(self):
        res = ""

        if self._type == "lovethegarden":
            res = self._soup.find("li", {"class": "pager-listitem--icon-next"}) \
                .findPreviousSibling() \
                .findChild("a") \
                .getText()

        return int(res.strip())


all_plants = Scraper("https://www.lovethegarden.com", "lovethegarden").get_all_plants()
all_plants = list(map(lambda x: x.lower(), all_plants))
