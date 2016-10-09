import scrapy

from fake_useragent import UserAgent

class RandomUserAgentMiddleware(object):
	def __init__(self):
		self.ua = UserAgent()
		
	def process_request(self, request, spider):
		request.headers.setdefault('User-Agent', self.ua.random)	