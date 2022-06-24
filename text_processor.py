import spacy
from thefuzz import process

from scraper import all_plants


def _extract_plant(text):
    res = process.extractOne(text, all_plants, score_cutoff=55)

    if (text in ["ziemia", "ziemi", "ziemię"] and res[0].lower() == "ziemniaki") or \
            (text in ["czas", "czasie"] and res[0].lower() == "czosnek") or \
            (text in ["uprawa", "uprawy", "uprawie", "upraw"] and res[0].lower() == "róża"
             or res[0].lower() == "żurawina"):
        return None
    if res is not None:
        return res[0]


class InputProcessor:
    def __init__(self, text):
        self._nlp = spacy.load("pl_core_news_md")
        self._doc = self._nlp(text)
        self._plant: str = ""
        self._param: str = ""

    def get_plant(self):
        for token in self._doc:
            if token.pos_ == "NOUN" and token.dep_ not in ["ROOT", "obl"] and _extract_plant(token.text) is not None:
                res = _extract_plant(token.text)
                self._plant = res
                return res

    def get_param(self):
        for token in self._doc:
            if (token.pos_ == "ADV" and token.dep_ == "advmod" and token.text.lower() == "kiedy") or \
                    (token.pos_ == "NOUN" and
                     process.extractOne(token.text, ["czas", "okres"], score_cutoff=70) is not None):
                self._param = token.text
                return "kiedy"
            elif token.pos_ == "ADV" and token.dep_ == "advmod" and token.text.lower() == "gdzie":
                return "gdzie"
            elif (token.pos_ == "NOUN" and
                  process.extractOne(token.text, ["ziemia", "podłoże", "gleba"], score_cutoff=70) is not None):
                self._param = token.text
                return "ziemia"
            elif (token.pos_ == "VERB" or token.pos_ == "NOUN") and token.dep_ == "ROOT" \
                    or (token.pos_ == "NOUN" and token.dep_ == "nsubj") and _extract_plant(token.text) is None:
                self._param = token.text
                if process.extractOne("sadzić", token.text)[1] > 60:
                    return "sadzić"
                return token.text
        return "opis"

    def get_plant_not_detailed(self):
        for token in self._doc:
            if token.pos_ == "NOUN" and token.dep_ in ["nmod", "nsubj", "obj"] and token.text != self._param:
                return token.text


class TextProcessor:
    def __init__(self, text, search_param):
        self._nlp = spacy.load("pl_core_news_md")
        self._param = search_param
        self._text = text

    def get_info_from_text(self):
        # for line in self._text:
        #     doc = self._nlp(line)
        #     for token in doc:
        #         print(token.text, token.pos_, "->", token.dep_, end=" ")
        #     print()
        #     print("--------------------------------------------------")

        res = process.extract(self._param, self._text)
        print(res)
        return res[0][0]