from unicodedata import normalize
from bs4 import BeautifulSoup
import requests as rq
import pandas as pd

class ThoughtCo:
    def __init__(self) -> None:
        self.__url = "https://www.thoughtco.com/dinosaurs-a-to-z-1093748"
        self.__resp = list(filter(lambda dino: 100 > len(dino.text),
            BeautifulSoup(rq.get(self.__url).text, "html.parser").find("div", attrs={"id":"mntl-sc-page_1-0"}) \
                .find_all("span", class_="mntl-sc-block-heading__text")[1].find_all_next("p")))

        self.__dino_class = list(filter(lambda d: d and 2 >= len(d.split("-")),
            set(map(lambda d: d.a["href"].split("/")[-1].split("-dinosaur-")[0] if d.a and "-dinosaur" in d.a["href"] else "", self.__resp))))

        self.__dino_list = list(map(lambda dino: normalize("NFKD", dino.text).split("-")[0].strip(), self.__resp))

    @property
    def dinolist(self) -> list:
        return self.__dino_list

    def __pack_of_dinos_info(self, infos:list) -> dict:
        infos = list(map(lambda d: normalize("NFKD", d.strip()), infos))

        return dict(zip(infos[::2], infos[1::2]))

    def __is_in_diferents_lines(self, infos:list) -> list:
        return list(map(lambda d: d.replace(":", ""), infos))

    def __is_in_same_line(self, infos:list) -> list:
        return [i for info in list(map(lambda d: d.replace(":)", ")").split(":"), infos)) for i in info]

    def __get_index(self, infolist:list, start:str, isstart:bool=True) -> int:
        init, end = (0, 0) if isstart else (1, 2)

        return int([i + init if ": " in d else i + end for i, d in enumerate(infolist) if start in d][0])

    def __page_with_one_dino_get_interval_of(self, html_with_infos:BeautifulSoup, tag:str) -> list:

        infos = list(map(lambda d: d.text.lower().strip(), html_with_infos.find_all(tag)))
        html_text = html_with_infos.get_text().lower()
        look_for = "name:" if "name:" in html_text else "name" if "name" in html_text else "habitat:"
        begin, end = self.__get_index(infos, look_for), self.__get_index(infos, " characteristics", False)

        return self.__is_in_same_line(infos[begin:end]) if ": " in infos[begin:end][0] else self.__is_in_diferents_lines(infos[begin:end])

    def extract_data(self):
        dinos = []
        for dinosaur in self.__resp:
            link, dino, infos = dinosaur.a["href"] if dinosaur.a else "", {}, []

            dinosaur = normalize("NFKD", dinosaur.text).strip().lower()
            dinosaur = dinosaur.split("-") if "-" in dinosaur else dinosaur.split(" ")

            dino["name"] = dinosaur[0].strip()
            dino["description"] = " ".join(dinosaur[1:]).strip()
            if not link: continue

            # img = dinfo.find("figure")
            dino |= {"class": "".join(filter(lambda c: c in link, self.__dino_class))}
            parsed_html = BeautifulSoup(rq.get(link).text, "html.parser")

            try:
                match link:
                    case link if "carnivorous-" in link:
                        dino |= {"name": list(filter(lambda h: dino["name"] in h,
                            map(lambda d: d.text.lower().strip(), parsed_html.find_all("h2"))))[0]}

                    case link if link.split("/")[3].startswith(f'{dino["name"]}-10'):
                        parsed_html = parsed_html.find("div", attrs={"id":"mntl-sc-page_1-0"})

                        if all(item in parsed_html.get_text().lower() for item in ["habitat", "historical period", "distinguishing characteristics"]):
                            infos = self.__page_with_one_dino_get_interval_of(parsed_html, "li" if "<li>" in str(parsed_html) else "p")
                            infos = list(map(lambda d: d.lower().replace("\n", "").strip(), infos))

                    case link if "-pictures" in link:
                        parsed_html = parsed_html.find("div", attrs={"id":"list-sc__content_1-0"})
                        title = list(filter(lambda d: dino["name"] in d.text.lower(), parsed_html.find_all("h2")))[0]
                        infos = title.find_all_next("li") if "titanosaur-" in link else title.find_all_next("p", attrs={"class": "comp"})
                        infos = list(map(lambda d: d.text.strip().lower(), infos))
                        if not infos[0].startswith("name"): continue

                        infos = infos[self.__get_index(infos, dino["name"]):self.__get_index(infos, " characteristics", False)]
            except IndexError: continue

            if infos: dino |= self.__pack_of_dinos_info(self.__is_in_same_line(infos) if ": " in infos[0] else self.__is_in_diferents_lines(infos))
            print(dino)
            print("-" * 50)
            print()

            dinos.append(dino)
        pd.json_normalize(dinos).to_excel("data/thoughtco-dataset.xlsx", index=False)

ThoughtCo().extract_data()