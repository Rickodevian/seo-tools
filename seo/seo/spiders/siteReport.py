# -*- coding: utf-8 -*-
import scrapy
import re
import MySQLdb
import base64

from seo.items import ReportItem
from scrapy.http import Request, FormRequest
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TimeoutError, TCPTimedOutError

class SitereportSpider(scrapy.Spider):
	name = "siteReport"
	allowed_domains = ["majestic.com"]
	login_page = 'https://majestic.com/account/login'
	logout_page = 'https://majestic.com/account/logout'
	site_report_page = 'https://majestic.com/reports/site-explorer?folder=&q=urbanindo.com&IndexDataSource=F'
	homepage = 'https://majestic.com'

	custom_settings = {
		'DOWNLOAD_DELAY' : 5,
		'ROBOTSTXT_OBEY' : False,
		'RETRY_HTTP_CODES' : ['403', '404', '500'],
		'RETRY_TIMES' : 2,
		'COOKIES_ENABLED' : True,
		'COOKIES_DEBUG' : False,
		'ITEM_PIPELINES' : {
			'seo.pipelines.SitereportPipeline' : 300
		}
	}

	def __init__(self, url=None, *args, **kwargs):
		super(SitereportSpider, self).__init__(*args, **kwargs)
		if url is not None:
			self.url = url
			self.site_report_page = 'https://majestic.com/reports/site-explorer?folder=&q=%s&IndexDataSource=F' % url 
		else :
			self.url = 'http://urbanindo.com'
			pass

	def start_requests(self):

		lastRequest = self.get_available_account_proxy()
		if lastRequest is not None:
			self.email = lastRequest[0]
			self.password = lastRequest[1]
			self.requestId = lastRequest[2]
			self.proxy = lastRequest[3]
			self.proxy_user = lastRequest[4]
			self.proxy_pass = lastRequest[5]
			found = True
		else :
			print "new account proxy"
			# TO DO : get new proxy
			found = self.set_new_account_proxy()
			if found is False:
				print "no account available"
				pass
			pass

		print self.email
		print self.proxy
		
		if found is True:
			return [Request(
					url=self.homepage,
					callback=self.parse_requests,
					headers={'referer': 'https://www.majestic.com'},
					dont_filter=True
				)]

	def parse_requests(self, response):
		# print response.headers.getlist('Set-Cookie')
		login = response.xpath('//li[@class="login separator"]/div/a/text()').extract() is None
		if login == False:
			print 'not logged in'
			return Request(
					url=self.login_page,
					callback=self.login,
					dont_filter=True
				)
		else:
			print 'logged in'
			proxy_auth = self.get_proxy_authorization()
			request = Request(
					url=self.site_report_page,
					callback=self.get_citation_trustflow,
					errback=self.errback_get_citation_trustflow,
					meta={'proxy': self.proxy},
					headers={'Proxy-Authorization':proxy_auth},
					dont_filter=True
				)
			return request
		pass

	def login(self, response):
		return FormRequest(
			url=self.login_page,
			formdata={'EmailAddress': self.email, 'Password': self.password},
			callback=self.after_login,
			dont_filter=True
		)

	def after_login(self, response):
		print self.email
		print self.proxy
		account = response.xpath('//li[@class="dd-link account-dd separator"]/a/text()').extract() is None
		if account == False:
			print "login success" 
			proxy_auth = self.get_proxy_authorization()
			request = Request(
					url=self.site_report_page,
					callback=self.get_citation_trustflow,
					errback=self.errback_get_citation_trustflow,
					meta={'proxy': self.proxy},
					headers={'Proxy-Authorization':proxy_auth},
					dont_filter=True
				)
			return request
		else:
			print "login failed"
		pass

	def get_proxy_authorization(self):
		print self.proxy_user
		if self.proxy_user != '':
			proxy_user_pass = self.proxy_user+':'+self.proxy_pass
			return 'Basic ' + base64.encodestring(proxy_user_pass)
		else:
			return ''

	def get_citation_trustflow(self, response):
		self.update_account_proxy_status(response.status)

		item = ReportItem()
		item['url'] = self.url
		item['citationFlow'] = response.xpath('//script').re(r'var citationFlow = ([0-9]+);')[0]
		item['trustFlow'] = response.xpath('//script').re(r'var trustFlow = ([0-9]+);')[0]
		print item
		yield item
		yield Request(
				url=self.logout_page,
				callback=self.after_logout,
				dont_filter=True,
			)
		pass

	def after_logout(self,response):
		logout = response.xpath('//li[@class="logout"]/a/text()').extract() is None
		if logout == False:
			print "logged out"
		else:
			print "logout failed"
			pass

	def make_connection_MySQL(self):
		return MySQLdb.connect(
					self.settings['MYSQL_HOST'],
					self.settings['MYSQL_USER'],
					self.settings['MYSQL_PASSWD'],
					self.settings['MYSQL_DBNAME'],
				)
		pass

	def get_accounts(self):
		db = self.make_connection_MySQL()
		cursor = db.cursor()
		sql = "SELECT id, username, password FROM SeoToolAccounts"
		cursor.execute(sql)
		result = cursor.fetchall()
		db.close()

		return result
		pass

	def get_proxies(self):
		db = self.make_connection_MySQL()
		cursor = db.cursor()
		sql = "SELECT id, proxy, username, password FROM Proxies"
		cursor.execute(sql);
		result = cursor.fetchall()
		db.close()

		return result
		pass

	def set_new_account_proxy(self):
		proxies = self.get_proxies()
		accounts = self.get_accounts()

		count_account = 0
		found = False
		while count_account < len(accounts) and found is False:
			count_proxy = 0
			while count_proxy < len(proxies) and found is False:
				result = self.get_exist_account_proxy(accounts[count_account][0], proxies[count_proxy][0])
				print result
				if result is None:
					self.email = accounts[count_account][1]
					self.password = accounts[count_account][2]
					self.proxy = proxies[count_proxy][1]
					self.proxy_user = proxies[count_proxy][2]
					self.proxy_pass = proxies[count_proxy][3]
					self.insert_new_account_proxy(accounts[count_account][0], proxies[count_proxy][0])
					found = True
					pass
				count_proxy = count_proxy + 1
			count_account = count_account + 1

		return found
		pass

	def insert_new_account_proxy(self, accountId, proxyId):
		db = self.make_connection_MySQL()
		cursor = db.cursor()
		sql = "INSERT INTO SeoAccountProxies(`seoAccountId`, `proxyId`) VALUES(%i, %i)" \
		% (accountId, proxyId)
		cursor.execute(sql)
		db.commit()
		db.close()

		self.requestId = cursor.lastrowid
		pass

	def get_exist_account_proxy(self, accountId, proxyId):
		db = self.make_connection_MySQL()
		cursor = db.cursor()
		sql = "SELECT id FROM SeoAccountProxies WHERE seoAccountId = %i AND proxyId = %i AND (NOW() > updatedTime + INTERVAL 1 DAY OR lastResponseStatus <> 200)" \
		% (accountId, proxyId)
		cursor.execute(sql)
		result = cursor.fetchone()
		db.close()

		return result

	def get_available_account_proxy(self):
		db = self.make_connection_MySQL()
		cursor = db.cursor()
		sql = "SELECT a.username, a.password, ap.id, p.proxy, p.username, p.password FROM SeoAccountProxies ap JOIN SeoToolAccounts a ON a.id = ap.seoAccountId JOIN Proxies p ON p.id = ap.proxyId WHERE NOW() > ap.updatedTime + INTERVAL 1 DAY OR ap.lastResponseStatus = 200 OR ap.used = 0"
		cursor.execute(sql)
		result = cursor.fetchone()
		db.close()

		return result
		pass

	def update_account_proxy_status(self, status):
		db = self.make_connection_MySQL()
		cursor = db.cursor()
		sql = "UPDATE SeoAccountProxies SET used = used + 1, lastResponseStatus = %i WHERE id = '%i' " % (status, self.requestId)
		cursor.execute(sql)
		db.commit()
		db.close()
		pass

	def errback_get_citation_trustflow(self, failure):
		if failure.check(HttpError):
			response = failure.value.response
			self.update_account_proxy_status(response.status)
			print 'HttpError on %s'  % str(response.url)
		elif failure.check(TCPTimedOutError):
			response = failure.request
			self.update_account_proxy_status(response.status)
			print 'TimeoutError on %s' % str(request.url)
		found = self.set_new_account_proxy()
		if found is False:
			print "no more account available"
		else:
			return FormRequest(
				url=self.login_page,
				formdata={'EmailAddress': self.email, 'Password': self.password},
				callback=self.after_login,
				dont_filter=True
			)
		pass
