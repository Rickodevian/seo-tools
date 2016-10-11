# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SeoItem(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	pass

class ReportItem(scrapy.Item):
	url = scrapy.Field()
	userAgent = scrapy.Field()
	trustFlow = scrapy.Field()
	citationFlow = scrapy.Field()
	pass

class BackLinkItem(scrapy.Item):
	backlinkUrlId = scrapy.Field()
	backlinkUrl = scrapy.Field()
	anchorHref = scrapy.Field()
	anchorText = scrapy.Field()
	pass
