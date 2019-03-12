# -*- coding: utf-8 -*-
"""This is an async python client for IEX cloud

	This module has only a small subset of functionality 
	offered by the iex cloud data platform for financial
	applications.

	
"""
import aiohttp
import asyncio
from secrets import IEX_TOKEN


class IEXData:
	def __init__(self,datatype='stock'):
		self.base_url = "https://cloud.iexapis.com"
		self.version = "beta"
		self.token = f"?token={IEX_TOKEN}"
		self.dynamic = True
		self.datatype = datatype


	async def fetch(self, session, url):
		async with session.get(url) as response:
			return await response.text()



	async def __call__(self, symbol):
		async with aiohttp.ClientSession() as session:
			#To do add flexibility
			#example /stock/{symbol}/chart/{range}/{date}
			html = await self.fetch(session, self.base_url+'/'+self.version+'/'+self.datatype+'/'+symbol+'/chart/dynamic'+self.token)
			print(html)

if __name__ == '__main__':
    data = IEXData()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(data('aapl'))


