import spacy
from spacy.matcher import Matcher
from thefuzz import process

from scraper import all_plants


def _extract_plant(text):
    res = process.extractOne(text, all_plants, score_cutoff=70)
    if res is None:
        return None

    if (text == "ziemia" and res[0].lower() == "ziemniaki") or \
            (text == "czas" and res[0].lower() == "czosnek") or \
            (text == "uprawa" and res[0].lower() == "róża"
             or res[0].lower() == "żurawina"):
        return None

    if res is not None:
        return res[0]


def _get_when():
    pattern1 = [{'LEMMA': "kiedy"}]
    pattern2 = [{'LEMMA': "czas"}]
    pattern3 = [{'LEMMA': "okres"}]
    pattern4 = [{'LEMMA': "pora"}]
    return [pattern1, pattern2, pattern3, pattern4]


def _get_where():
    pattern1 = [{'LEMMA': "miejsce"}]
    pattern2 = [{'LEMMA': "gdzie"}]
    return [pattern1, pattern2]


def _get_soil():
    pattern1 = [{'LEMMA': "gleba"}]
    pattern2 = [{'LEMMA': "podłoże"}]
    pattern3 = [{'LEMMA': "ziemia"}]
    return [pattern1, pattern2, pattern3]


def _get_usage():
    pattern1 = [{'LEMMA': "stosować"}]
    pattern2 = [{'LEMMA': "zastosowanie"}]
    return [pattern1, pattern2]


def _get_problems():
    pattern1 = [{'LEMMA': "problem"}]
    pattern2 = [{'LEMMA': "wymagać"}]
    pattern3 = [{'LEMMA': "choroba"}]
    return [pattern1, pattern2, pattern3]


def _get_care():
    pattern1 = [{'LEMMA': "pielęgnować"}]
    pattern2 = [{'LEMMA': "pielęgnacja"}]
    return [pattern1, pattern2]


def _get_planting():
    pattern1 = [{'LEMMA': "sadzić"}]
    pattern2 = [{'LEMMA': "sadząc"}]
    pattern3 = [{'LEMMA': "posadzić"}]
    pattern4 = [{'LEMMA': "zasadzić"}]
    return [pattern1, pattern2, pattern3, pattern4]


class InputProcessor:
    def __init__(self, text):
        self._nlp = spacy.load("pl_core_news_md")
        self._doc = self._nlp(text)
        self._plant: str = ""
        self._param: str = ""

    def get_plant(self):
        for token in self._doc:
            if token.pos_ == "NOUN" and token.dep_ not in ["ROOT", "obl"] and\
                    _extract_plant(token.lemma_.lower()) is not None:
                res = _extract_plant(token.lemma_)
                self._plant = res
                return res

    def get_param(self):
        for token in self._doc:
            if (token.pos_ == "ADV" and token.dep_ == "advmod" and token.text.lower() == "kiedy") or \
                    (token.pos_ == "NOUN" and
                     token.lemma_ in ["czas", "okres"]):
                self._param = token.text.lower()
                return "kiedy"
            elif token.pos_ == "ADV" and token.dep_ == "advmod" and token.text.lower() == "gdzie":
                return "gdzie"
            elif (token.pos_ == "NOUN" and
                  token.lemma_.lower() in ["ziemia", "podłoże", "gleba"]):
                self._param = token.text.lower()
                return "ziemia"
            elif (token.pos_ == "VERB" or token.pos_ == "NOUN") and token.dep_ == "ROOT" \
                    or (token.pos_ == "NOUN" and token.dep_ == "nsubj") and\
                    _extract_plant(token.lemma_.lower()) is None:
                self._param = token.text.lower()

                if process.extractOne(token.lemma_, ["sadzić"], score_cutoff=70) is not None:
                    return "sadzić"

                return token.lemma_.lower()

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
        self._matcher = Matcher(self._nlp.vocab)

    def get_info_from_text(self):
        found = []
        if self._param == "kiedy":
            patterns = _get_when()
        elif self._param == "gdzie":
            patterns = _get_where()
        elif self._param == "ziemia":
            patterns = _get_soil()
        elif self._param in ["zastosowanie", "zastosować", "stosować"]:
            patterns = _get_usage()
        elif self._param in ["problem", "wymagać"]:
            patterns = _get_problems()
        elif process.extractOne(self._param, ["pielęgnować"], score_cutoff=80) is not None:
            patterns = _get_care()
        elif process.extractOne(self._param, ["sadzić"], score_cutoff=80) is not None:
            patterns = _get_planting()
        else:
            patterns = []

        doc = self._nlp(". ".join(self._text))
        self._matcher.add("found", patterns)
        matches = self._matcher(doc)
        for _, start, end in matches:
            found.append(str(doc[start:end]))

        if not found:
            raise Exception("No information found")

        lines = []
        for token in found:
            for line in self._text:
                if token in line:
                    lines.append(line)
                    self._text.remove(line)

        return ". ".join(lines)
