from scraper import Scraper
from text_processor import InputProcessor, TextProcessor
import pyttsx3 as tts
import speech_recognition as sr


def voice_assistant(in_txt):
    ipr = InputProcessor(in_txt)
    plant = ipr.get_plant()
    if plant is None:
        plant = ipr.get_plant_not_detailed()

    param = ipr.get_param()
    print(plant, param)
    try:
        scraper1 = Scraper("https://www.lovethegarden.com", "lovethegarden")
        txt = scraper1.get_text(plant)
        tpr = TextProcessor(txt, param)
        res = tpr.get_info_from_text()
        print("Lovethegarden")
    except Exception:
        try:
            scraper2 = Scraper("https://zielonyogrodek.pl", "zielonyogrodek")
            txt = scraper2.get_text(plant)
            tpr = TextProcessor(txt, param)
            res = tpr.get_info_from_text()
            print("Zielonyogrodek")
        except Exception:
            res = "Nie znam odpowiedzi"
    print(res)
    return res


if __name__ == '__main__':
    TTS = tts.init()
    TTS.setProperty('volume', 0.7)
    TTS.setProperty('rate', 190)
    TTS.setProperty('voice', 'polish')

    STT = sr.Recognizer()
    print('''Napisz pytanie i naciśnij Enter
    albo naciśnij Enter i zadaj pytanie.''')
    while True:
        text = input(">>")
        if len(text) > 0:
            answer = voice_assistant(text)
            TTS.say(answer)
            TTS.runAndWait()

        else:
            with sr.Microphone() as source:
                print("slucham ...")
                audio = STT.listen(source)
                try:
                    text = STT.recognize_google(audio, language='pl_PL')
                    print(text)
                    answer = voice_assistant(text)
                    TTS.say(answer)
                    TTS.runAndWait()

                except sr.UnknownValueError:
                    print('Nie rozumiem')
                except sr.RequestError as e:
                    print('Error:', e)
