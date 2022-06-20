from garden_voice_assistant.scraper import Scraper

if __name__ == '__main__':
    plant = input("Podaj rosline: ")

    scraper1 = Scraper("https://www.lovethegarden.com", "lovethegarden")
    print(scraper1.get_text(plant))
    # scraper2 = Scraper("https://zielonyogrodek.pl", "zielonyogrodek")
    # print(scraper2.get_text(plant))
