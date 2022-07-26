from bs4 import BeautifulSoup
from tqdm import tqdm
import requests as rq
import pandas as pd

class NaturalHistoryMuseum:
    def __init__(self) -> None:
        self.__url = "https://www.nhm.ac.uk/discover/dino-directory"
        self.__dino_list = list(map(lambda dino: dino.text.strip().lower(), 
            BeautifulSoup(rq.get(f"{self.__url}/name/name-az-all.html").text, "html.parser") \
                .find_all("p", attrs={"class": "dinosaurfilter--name dinosaurfilter--name-unhyphenated"})))

    @property
    def dinolist(self) -> list:
        return self.__dino_list

    def __get_text_from(self, htmlsaur:BeautifulSoup, classaur:str) -> str:
        dino = htmlsaur.find(class_=f"dinosaur--{classaur}")
        return dino.text.lower().strip() if dino is not None else ""

    def __handle_html(self, htmlsaur:BeautifulSoup, classaur:str) -> dict:
        dino = self.__get_text_from(htmlsaur, classaur)        
        dino = dino.replace("\t", "").replace(",\n\n", ", ").replace("\n\n", "\n").split("\n")
        dino = list(map(lambda dino: dino.replace(":", "").strip(), dino))

        return dict(zip(dino[::2], dino[1::2]))

    def __save_infos_about(self, htmlsaur:BeautifulSoup, name:str) -> None:
            about = self.__get_text_from(htmlsaur, "content-container")
            if about:
                with open(f"archives/{name}.txt", "w", encoding="utf8") as dinofile:
                    for item in about.split("\n"): dinofile.write(f"{item.strip()}\n")

    def extract_data(self, download:bool=False) -> None:
        dinos = []
        for dinoname in tqdm(self.__dino_list):
            htmlsaur, dino = BeautifulSoup(rq.get(f"{self.__url}/{dinoname}.html").text, "html.parser"), {}

            dino["pronunciation"] = self.__get_text_from(htmlsaur, "pronunciation")
            dino["meaning"] = self.__get_text_from(htmlsaur, "meaning")[1:-1]
            dino["name"] = dinoname

            for item in ["description", "info", "taxonomy"]:
                dino |= self.__handle_html(htmlsaur, item)

            dinos.append(dino)
            if download: self.__save_infos_about(htmlsaur, dinoname)
        pd.json_normalize(dinos).to_excel("data/nhm-dataset.xlsx", index=False)

NaturalHistoryMuseum().extract_data()