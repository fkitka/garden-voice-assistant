import itertools
from bs4 import BeautifulSoup
import requests
from thefuzz import process


def get_url_content(url):
    res = requests.get(url)
    if not res.ok:
        raise Exception(res.status_code)

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

    def get_all_plants(self):
        page_content = ""
        if self._type == "lovethegarden":
            page_content = get_url_content(self._base_url + self._catalog + "/?field_plant_category_target_id=All" + "&"
                                           + "page=" + str(0))
        # elif self._type == "zielonyogrodek":
        #     page_content = get_url_content(self._base_url + self._catalog + "/strona/" + str(0 * 30))
        self._set_soup(page_content)
        plants_names = []
        max_page_num = self._get_max_page_num()
        for i in range(max_page_num):
            if self._type == "lovethegarden":
                page_content = get_url_content(self._base_url + self._catalog + "/?field_plant_category_target_id=All" +
                                               "&" + "page=" + str(i))
            # elif self._type == "zielonyogrodek":
            #     page_content = get_url_content(self._base_url + self._catalog + "/strona/" + str(i * 30))
            self._set_soup(page_content)
            plants = self._soup.find_all(self._elem_type, {"class": self._elem_class})
            for plant in plants:
                plant_a = plant.findChild("a")
                if plant_a:
                    if self._type == "lovethegarden":
                        plants_names.append(plant_a.get("title"))
                    # elif self._type == "zielonyogrodek":
                    #     title = plant_a.findNextSibling().findChild("div", {"class": "title"})
                    #     plants_names.append(title.text.strip())
        return plants_names

    def _get_max_page_num(self):
        res = ""

        if self._type == "lovethegarden":
            res = self._soup.find("li", {"class": "pager-listitem--icon-next"}) \
                .findPreviousSibling() \
                .findChild("a") \
                .getText()
        # elif self._type == "zielonyogrodek":
        #     res = self._soup.find("nav", {"class": "pagination"}) \
        #         .findChild("div") \
        #         .findChildren("a") \
        #         .pop() \
        #         .getText()

        return int(res.strip())


all_plants = Scraper("https://www.lovethegarden.com", "lovethegarden").get_all_plants()
all_plants = list(map(lambda x: x.lower(), all_plants))
