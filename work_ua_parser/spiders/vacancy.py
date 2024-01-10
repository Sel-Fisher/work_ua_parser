import scrapy
from scrapy.http import Response
from config import TECHNOLOGIES_NAME, EXPERIENCE_YEARS


class VacancySpider(scrapy.Spider):
    name = "vacancy"
    allowed_domains = ["www.work.ua"]
    start_urls = ["https://www.work.ua/"]

    def parse(self, response: Response, **kwargs):
        it_python_job_url = response.urljoin("/jobs-it-python/")
        yield response.follow(it_python_job_url, callback=self.parse_it_job_python)

    def parse_it_job_python(self, response: Response):
        vacancies_block = response.css("#pjax-job-list div[tabindex]")
        for vacancy in vacancies_block:
            vacancy_link = vacancy.css("h2 a::attr(href)").get()
            vacancy_detail_link = response.urljoin(vacancy_link)
            yield response.follow(vacancy_detail_link, callback=self.parse_single_vacancy)

        next_page = response.css('li.no-style.add-left-default a[href]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_it_job_python)

    def parse_single_vacancy(self, response: Response) -> dict:
        vacancy_experience = response.css(".card.wordwrap p.text-indent")[-1].css("p::text").getall()[1]
        vacancy_description = response.css("div.hovered-links#job-description").css("::text").getall()

        vacancy_experience_rendered = "".join(vacancy_experience).replace("\n", "").strip()
        vacancy_description_rendered = "".join(vacancy_description).replace("\r", "").replace("\n", "").strip()

        technologies = set("Python")
        for tech in TECHNOLOGIES_NAME:
            if tech.lower() in vacancy_description_rendered.lower():
                technologies.add(tech)
        technologies = list(technologies)
        experience = 0
        for exp, exp_in_num in EXPERIENCE_YEARS.items():
            if exp.lower() in vacancy_experience_rendered.lower():
                experience = exp_in_num
                break

        return {
            "technologies": technologies,
            "experience": experience
        }
