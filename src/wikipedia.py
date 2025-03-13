from bs4 import BeautifulSoup
import requests as rq

class Wikipedia:
    def __init__(self) -> None:
        self.__url = "https://en.wikipedia.org/wiki/List_of_dinosaur_genera"
        self.__resp = BeautifulSoup(rq.get(self.__url).text, "html.parser").find("table", attrs={"id":"toc"}).find_all_next("ul")

        self.__terminologies = ["junior synonym", "nomen nudum", "nomen oblitum", "nomen manuscriptum", "preoccupied name", "nomen dubium"]

        dinos = list(filter(lambda d: d.a and d.a.has_attr("title") and d.a["title"].split(" ")[0] in d.text,  [li for ul in map(lambda ul: ul.find_all("li"), self.__resp) for li in ul]))
        # dinos.reverse()
        for d in dinos:
            print(d.a["title"].replace(" ", "_") in d.a["href"] and d.a["title"].split(" ")[0] in d.text, " | ", d.a["title"], " | ", d.a["href"], " | ", d.text)
            print(d.a["title"].replace(" ", "_"))
            print()

        self.__dino_list = []

    @property
    def dinolist(self) -> list:
        return self.__dino_list

print(Wikipedia().dinolist)