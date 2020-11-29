import json
from pathlib import Path

from jinja2 import (
    Environment,
    select_autoescape,
    FileSystemLoader,
)
from scrapy.crawler import CrawlerProcess

from pets.pets.spiders.pets import PetsSpider


def main():
    pets_data_file = Path("pets.json")
    if not pets_data_file.exists():
        process = CrawlerProcess(settings={"FEEDS": {"pets.json": {"format": "json"}}})
        process.crawl(PetsSpider)
        process.start()

    with pets_data_file.open() as f:
        pet_data = json.load(f)

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("pets.html.jinja")
    html: str = template.render(pet_data=pet_data)
    with open("pets.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
