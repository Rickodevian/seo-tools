# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import MySQLdb

class SeoPipeline(object):
	def process_item(self, item, spider):
		return item

class SitereportPipeline(object):
	def __init__(self, settings):
		self.mysqlHost = settings.get('MYSQL_HOST')
		self.mysqlUser = settings.get('MYSQL_USER')
		self.mysqlPasswd = settings.get('MYSQL_PASSWD')
		self.mysqlDBName = settings.get('MYSQL_DBNAME')
		pass

	@classmethod
	def from_crawler(cls, crawler):
		return cls(crawler.settings)

	def make_connection_MySQL(self):
		return MySQLdb.connect(
					self.mysqlHost,
					self.mysqlUser,
					self.mysqlPasswd,
					self.mysqlDBName,
				)
		pass

	def process_item(self, item, spider):
		db = self.make_connection_MySQL()
		cursor = db.cursor() 
		sql = "SELECT id FROM Backlinks WHERE url = '%s' " % item['url']
		cursor.execute(sql)
		urlExist = cursor.fetchone()
			
		if urlExist:
			sql = "UPDATE Backlinks SET citationFLow = %i, trustFlow = %i WHERE id = %i " \
			% (int(item['citationFlow']), int(item['trustFlow']), int(urlExist[0]))
			cursor.execute(sql)
			db.commit()
		db.close()
		return item

class BacklinkCheckerPipeline(object):
	def __init__(self, settings):
		self.mysqlHost = settings.get('MYSQL_HOST')
		self.mysqlUser = settings.get('MYSQL_USER')
		self.mysqlPasswd = settings.get('MYSQL_PASSWD')
		self.mysqlDBName = settings.get('MYSQL_DBNAME')
		pass

	@classmethod
	def from_crawler(cls, crawler):
		return cls(crawler.settings)

	def make_connection_MySQL(self):
		return MySQLdb.connect(
					self.mysqlHost,
					self.mysqlUser,
					self.mysqlPasswd,
					self.mysqlDBName,
				)
		pass

	def process_item(self, item, spider):
		db = self.make_connection_MySQL()
		cursor = db.cursor() 
		sql = "SELECT id FROM `BacklinksUrbanindo` WHERE backlinkId = %i AND urbanindoUrlHref = '%s' " \
		% (item['backlinkUrlId'], item['urbanindoUrlHref'])
		cursor.execute(sql)
		urlExist = cursor.fetchone()

		if urlExist is None:
			sql = "INSERT IGNORE INTO BacklinksUrbanindo(backlinkId, urbanindoUrlHref, urbanindoUrlText) VALUES(%i, '%s', '%s')" \
			% (item['backlinkUrlId'], item['urbanindoUrlHref'], item['urbanindoUrlText'])
			cursor.execute(sql)
			db.commit()
		db.close()
		return item
