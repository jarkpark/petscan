import scrapy


class PetsSpider(scrapy.Spider):
    name = "pets"
    allowed_domains = ["austinhumanesociety.org", "austinpetsalive.org"]

    def start_requests(self):
        sites = [
            {
                "url": "http://www.austinhumanesociety.org/feline-friends/",
                "callback": self.parse_austin_humane_society,
            },
            {
                "url": "https://www.austinpetsalive.org/adopt/cats",
                "callback": self.parse_austin_pets_alive,
            },
        ]
        for site in sites:
            yield scrapy.Request(url=site["url"], callback=site["callback"])

    def parse(self, response):
        pass

    def parse_austin_humane_society(self, response):
        for pet in response.css("div#squeeze li.pet"):
            yield {
                "name": pet.css("h3::text").get(),
                "gender": pet.css("p::text")[1].get(),
                "breed": pet.css("p::text")[2].get(),
                "age": pet.css("p::text")[3].get(),
                "weight": pet.css("p::text")[4].get(),
                "page": pet.css("a::attr(href)").get(),
                "picture": pet.css("div.custom-main-image::attr(style)").re(
                    r"url\((.*)\)"
                )[0],
            }

    def parse_apa_details(self, response):
        pet_data = response.meta["results"]
        weight = response.css("div.row.justify-center div")[2].css("h6::text")[1].get()
        pet_data["weight"] = weight
        yield pet_data

    def parse_austin_pets_alive(self, response):
        for pet in response.css(
            "div.row.justify-center div.large-tile.mr-auto.ml-auto"
        ):
            pet_data_partial = {
                "name": pet.css("a.orange::text").get(),
                "gender": pet.css("ul.list-unstyled li::text")[2].get(),
                "breed": pet.css("ul.list-unstyled li::text")[3].get(),
                "age": " ".join(
                    age_part.strip()
                    for age_part in pet.css("ul.list-unstyled li::text")[:2].getall()
                ),
                "page": pet.css("a.orange::attr(href)").get(),
                "picture": pet.css("a.img-holder.relative img::attr(src)").get(),
            }
            yield scrapy.Request(
                pet.css("a.orange::attr(href)").get(),
                callback=self.parse_apa_details,
                meta={"results": pet_data_partial},
            )

        next_page = response.css("div.pagination a.forward::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_austin_pets_alive)
