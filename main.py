from garden_voice_assistant.scraper import Scraper
import pyttsx3 as tts
import speech_recognition as sr


def voice_assistant(text):
    try:
        scraper1 = Scraper("https://www.lovethegarden.com", "lovethegarden")
        res = scraper1.get_text(text)
        res = res[4]
    except Exception:
        try:
            scraper2 = Scraper("https://zielonyogrodek.pl", "zielonyogrodek")
            res = scraper2.get_text(text)
            res = res[4]
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
