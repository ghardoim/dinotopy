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
            set(map(lambda d: d.a["href"].split("/")[-1].split("-dinosaur-")[0] if d.a and "-dinosaur" in d.a["href"] else "", self.__resp)))) + ["sauropod"]
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
        return [i for info in list(map(lambda d: d.replace(":)", ")").replace("):", ")").split(":"), infos)) for i in info]

    def __get_index(self, infolist:list, start:str, isstart:bool=True) -> int:
        init, end = (0, 0) if isstart else (1, 2)

        return int([i + init if ": " in d else i + end for i, d in enumerate(infolist) if start in d][0])

    def __page_with_one_dino_get_interval_of(self, html_with_infos:BeautifulSoup, tag:str) -> list:

        infos = list(map(lambda d: d.text.lower().strip(), html_with_infos.find_all(tag)))
        html_text = html_with_infos.get_text().lower()
        look_for = "name:" if "name:" in html_text else "name" if "name" in html_text else "habitat:"
        begin, end = self.__get_index(infos, look_for), self.__get_index(infos, " characteristics", False)

        return self.__is_in_same_line(infos[begin:end]) if ": " in infos[begin:end][0] else self.__is_in_diferents_lines(infos[begin:end])

    def __parse_html(self, link:str, tagid:str) -> BeautifulSoup:
        return BeautifulSoup(rq.get(link).text, "html.parser").find("div", attrs={"id": tagid})

    def __save_infos_about(self, dinoname:str, paragraphs:list) -> None:
        with open(f"archives/{dinoname}.txt", "w", encoding="utf8") as dinofile:
            for item in map(lambda a: normalize("NFKD", a.text.lower().strip()), paragraphs): dinofile.write(f"{item}\n")

    def __get_info_outside_of(self, interval:list) -> list:
        infos = list(map(lambda d: d.text.lower().strip(), interval))
        return interval[:self.__get_index(infos, "name:")] + interval[self.__get_index(infos, " characteristics", False):]

    def __start_with_name(self, infos:list) -> bool:
        return infos[0].lower().strip().startswith("name")

    def __has_colon_space(self, infos:list) -> bool:
        return ": " in infos[0].strip().replace(u'\xa0', u' ')

    def extract_data(self):
        dinos = []
        for dinosaur in self.__resp:
            link, dino, infos, about = dinosaur.a["href"] if dinosaur.a else "", {}, [], []

            dinosaur = normalize("NFKD", dinosaur.text).strip().lower()
            dinosaur = dinosaur.split("-") if "-" in dinosaur else dinosaur.split(" ")

            dino["name"] = dinosaur[0].strip()
            dino["description"] = " ".join(dinosaur[1:]).strip()
            if not link: continue

            dino |= {"type of dinosaur": "".join(filter(lambda c: f"/{c}" in link, self.__dino_class))}
            try:
                match link:
                    case link if "carnivorous-" in link:
                        parsed_html = self.__parse_html(link, "list-sc_1-0")
                        dino |= {"name": list(filter(lambda h: dino["name"] in h,
                            map(lambda d: d.text.lower().strip(), parsed_html.find_all("h2"))))[0]}

                        about = list(filter(lambda d: dino["name"] in d.text.lower(),
                            parsed_html.find_all("h2")))[0].find_parent().find("figure").find_next_siblings("p")

                    case link if link.split("/")[3].startswith(f'{dino["name"]}-10'):
                        parsed_html = self.__parse_html(link, "mntl-sc-page_1-0")
                        if all(item in parsed_html.get_text().lower() for item in ["habitat", "historical period", "distinguishing characteristics"]):
                            infos = self.__page_with_one_dino_get_interval_of(parsed_html, "li" if "<li>" in str(parsed_html) else "p")
                            infos = list(map(lambda d: d.lower().replace("\n", "").strip(), infos))

                        about = list(filter(lambda a: a.text.lower().strip().startswith("about"), parsed_html.find_all("span")))
                        about = about[0].find_parent().find_next_siblings("p") if about else parsed_html.find_all("p")
                        about = self.__get_info_outside_of(about) if "<li>" not in str(parsed_html) and "name:" in str(parsed_html).lower() else about

                    case link if any([c in link for c in self.__dino_class]):
                        parsed_html = self.__parse_html(link, "list-sc__content_1-0")
                        title = list(filter(lambda d: dino["name"] in d.text.lower(), parsed_html.find_all("h2")))[0].find_parent()

                        infos = title.find_all("li") if "titanosaur-" in link else title.find_all("p", attrs={"class": "comp"})
                        infos = list(map(lambda d: d.text.strip().lower(), infos))
                        if not self.__start_with_name(infos): continue

                        begin = self.__get_index(infos, dino["name"])
                        begin = begin - 1 if self.__start_with_name(infos) and not self.__has_colon_space(infos) else begin
                        infos = infos[begin:self.__get_index(infos, " characteristics", False)]

                        about = title.find("figure").find_next_siblings("p")
                        about = self.__get_info_outside_of(about) if "<li>" not in str(parsed_html) else about
            except IndexError: continue

            if infos: dino |= self.__pack_of_dinos_info(self.__is_in_same_line(infos) if self.__has_colon_space(infos) else self.__is_in_diferents_lines(infos))
            if about: self.__save_infos_about(dinosaur[0].strip(), about)
            dinos.append(dino)
            print(link, dino, about)
            print("-" * 50)
            print()
        pd.json_normalize(dinos).to_excel("data/thoughtco-dataset.xlsx", index=False)
ThoughtCo().extract_data()