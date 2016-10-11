# -*- coding: utf-8 -*-
import scrapy
import MySQLdb

from seo.items import BackLinkItem
from scrapy.http import Request
from datetime import datetime
from scrapy.selector import Selector

class BacklinkcheckerSpider(scrapy.Spider):
	name = "backlinkChecker"
	url = 'http://www.urbanindo.com'
	error_code = [403, 404]

	custom_settings = {
		'ITEM_PIPELINES' : {
			'seo.pipelines.BacklinkCheckerPipeline' : 300
		}
	}

	def __init__(self, url=None, *args, **kwargs):
		if url is not None:
			self.url = url
			pass
		pass

	def start_requests(self):
		return [
			Request(
				url=self.url,
				callback=self.parse_request
			)
		]
		pass

	def parse_request(self, response):
		item = BackLinkItem()
		insertedAnchorHrefs = []

		urlId = self.get_backlink_url_id(response)
		innerAnchors = response.xpath('//a[contains(@href, "urbanindo.com") or contains(@href, "urban.id")]').extract()
		for c in xrange(0, len(innerAnchors)):
			anchorText = Selector(text=str(innerAnchors[c])).xpath('//text()[not(*)] | text()').extract();
			if len(anchorText) != 0:
				anchorHref = Selector(text=str(innerAnchors[c])).xpath('//@href').extract();
				item['backlinkUrlId'] = urlId
				item['backlinkUrl'] = response.url
				item['anchorHref'] = anchorHref[0]
				item['anchorText'] = anchorText[0]
				insertedAnchorHrefs.append(anchorHref[0]);
				print item
				yield item
			pass
		self.delete_removed_backlink_urls(urlId, insertedAnchorHrefs)
		pass

	def delete_removed_backlink_urls(self, urlId, anchorHref):
		db = self.make_connection_MySQL()
		cursor = db.cursor()
		sql = "SELECT id, anchorHref FROM `BacklinksUrbanindo` WHERE backlinkId = %i " % urlId
		cursor.execute(sql)
		anchorHrefOld = cursor.fetchall()

		for x in xrange(0, len(anchorHrefOld)):
			if anchorHrefOld[x][1] not in anchorHref:
				sql = "DELETE FROM `BacklinksUrbanindo` WHERE id = %i " % anchorHrefOld[x][0]
				cursor.execute(sql)
				pass
			pass
		db.commit()
		db.close()

	def get_backlink_url_id(self, response):
		db = self.make_connection_MySQL()
		cursor = db.cursor()
		sql = "SELECT id, url, htmlContent FROM `Backlinks` WHERE url = '%s'" % response.url
		cursor.execute(sql)
		result = cursor.fetchone()
		db.close()

		if result:
			urlId = self.update_existing_backlink(response, result)
		else :
			urlId = self.insert_new_backlink(response)
		return urlId

	def insert_new_backlink(self, response):
		active = self.is_url_active(response.status)

		db = self.make_connection_MySQL()
		cursor = db.cursor()
		sql = "INSERT INTO Backlinks(url, urlStatus, lastResponseStatus, htmlContent) VALUES('%s', %i, %i, '%s')"\
		% (response.url, active, response.status, db.escape_string(str(response.body)))
		cursor.execute(sql)
		db.commit()
		db.close()
		return cursor.lastrowid

	def update_existing_backlink(self, response, sqlResult):
		active = self.is_url_active(response.status)
		urlId = sqlResult[0]
		htmlContent = sqlResult[2]

		if str(response.body) != htmlContent:
			db = self.make_connection_MySQL()
			cursor = db.cursor()
			sql = "UPDATE Backlinks SET urlStatus = %i, lastResponseStatus = %i, htmlContent = '%s' WHERE id = %i "\
			% (active, response.status, db.escape_string(str(response.body)), urlId)
			cursor.execute(sql)
			db.commit()
			db.close()
			pass

		return urlId

	def get_datetime_now(self):
		return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

	def is_url_active(self, status):
		if status not in self.error_code:
			return 1
		else:
			return 0

	def make_connection_MySQL(self):
		return MySQLdb.connect(
					self.settings['MYSQL_HOST'],
					self.settings['MYSQL_USER'],
					self.settings['MYSQL_PASSWD'],
					self.settings['MYSQL_DBNAME'],
				)
		pass
