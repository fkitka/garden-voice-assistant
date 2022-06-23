import spacy
from thefuzz import process

from garden_voice_assistant.scraper import all_plants


def get_info_from_text(text, param):
    res = process.extract(param, text)
    print(res)
    return res[0][0]


def _plant(text):
    res = process.extractOne(text, all_plants, score_cutoff=55)

    if (text in ["ziemia", "ziemi", "ziemię"] and res[0].lower() == "ziemniaki") or \
            (text in ["czas", "czasie"] and res[0].lower() == "czosnek") or \
            (text in ["uprawa", "uprawy", "uprawie", "upraw"] and res[0].lower() == "róża"):
        return None
    if res is not None:
        return res[0]


class TextProcessor:
    def __init__(self, text):
        self._nlp = spacy.load("pl_core_news_md")
        self._doc = self._nlp(text)

    def get_plant(self):
        for token in self._doc:
            if token.pos_ == "NOUN" and token.dep_ not in ["ROOT", "obl"] and _plant(token.text) is not None:
                res = _plant(token.text)
                return res

    def get_param(self):
        for token in self._doc:
            if (token.pos_ == "ADV" and token.dep_ == "advmod" and token.text.lower() == "kiedy") or \
                    (token.pos_ == "NOUN" and
                     process.extractOne(token.text, ["czas", "okres"], score_cutoff=70) is not None):
                return "kiedy"
            elif (token.pos_ == "NOUN" and
                  process.extractOne(token.text, ["ziemia", "podłoże", "gleba"], score_cutoff=70) is not None or
                  (token.pos_ == "ADV" and token.dep_ == "advmod" and token.text.lower() == "gdzie")):
                return "ziemia"
            elif (token.pos_ == "VERB" or token.pos_ == "NOUN") and token.dep_ == "ROOT" \
                    or (token.pos_ == "NOUN" and token.dep_ == "nsubj") and _plant(token.text) is None:
                return token.text
        return "opis"
