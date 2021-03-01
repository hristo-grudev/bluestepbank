import scrapy

from scrapy.loader import ItemLoader
from ..items import BluestepbankItem
from itemloaders.processors import TakeFirst


class BluestepbankSpider(scrapy.Spider):
	name = 'bluestepbank'
	start_urls = ['https://www.bluestepbank.com/press/press-releases/']

	def parse(self, response):
		post_links = response.xpath('//li[@class="List-item u-marginBsm"]')
		for post in post_links:
			url = post.xpath('./a/@href').get()
			date = post.xpath('.//i[@class="u-textXSmall"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//div[@class="Pager"]/a[@class="Pager-link Pager-next"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="Article-column"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BluestepbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
