import itertools
import re
from typing import Union, Iterator

import requests
from bs4 import BeautifulSoup

from jinja2 import Environment, FileSystemLoader, select_autoescape


class Scraper:
    def __init__(self, url: Union[str, Iterator[str]], *args, **kwargs):
        self.url = url
        self.args = args
        self.kwargs = kwargs

    def get_data(self, mapping_function):
        if isinstance(self.url, str):
            urls = [self.url]
        else:
            urls = self.url

        response_history = ""
        for url in urls:
            response = requests.get(url)
            if not response.ok or response.text == response_history:
                break
            response_history = response.text
            soup = BeautifulSoup(response.content, "html.parser")
            pet_data_raw = soup.find_all(*self.args, **self.kwargs)
            yield from map(
                mapping_function,
                pet_data_raw,
            )


def main():
    pet_data = [
        Scraper(
            "http://www.austinhumanesociety.org/feline-friends/", "li", class_="pet"
        ).get_data(
            lambda data: {
                "name": data.h3.string.strip(),
                "gender": data.p.contents[2].strip(),
                "breed": data.p.contents[4].strip(),
                "age": data.p.contents[6].strip(),
                "weight": data.p.contents[8].strip(),
                "page": data.a.get("href"),
                "picture": re.search(
                    r"background-image:\surl\(([^)]*)\);", data.div.get("style")
                ).group(1),
            }
        ),
        Scraper(
            (
                f"https://www.austinpetsalive.org/adopt/cats/p{page}"
                for page in range(1, 25)
            ),
            "div",
            class_="large-tile mr-auto ml-auto mb-50 relative",
        ).get_data(
            lambda data: {
                "name": data.find("h3").a.string.strip(),
                "gender": data.find("ul").contents[3].string.strip(),
                "breed": data.find("ul").contents[5].string.strip(),
                "age": " ".join(data.find("ul").contents[1].stripped_strings),
                "weight": "See details",
                "page": data.find("h3").a.get("href"),
                "picture": data.find("img").get("src"),
            }
        ),
    ]

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("pets.html.jinja")
    html: str = template.render(pet_data=itertools.chain.from_iterable(pet_data))
    with open("pets.html", "w") as f:
        f.write(html)
