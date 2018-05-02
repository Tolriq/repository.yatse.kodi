"""
    Copyright (C) 2017 tknorris

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os,re
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
from lib import jsunpack

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()


class StreamApi(UrlResolver):
    name = "StreamApi"
    domains = ["streamapi.xyz"]
    pattern = '(?://|\.)(streamapi\.xyz)/([A-Za-z0-9\?\.\-\=\_\&\~]+)'
    
    def __init__(self):
        self.net = common.Net()
    
    def get_media_url(self, host, media_id):
            net = common.Net()
            web_url = self.get_url(host, media_id)
            html = net.http_GET(web_url).content
            match=re.compile('"false"> (.+?)</script>',re.DOTALL).findall(html)
            for source in match:
                source =source.strip()
                try:

                    UNPACKED = jsunpack.unpack(source)
                    if 'var link=' in UNPACKED:
                        FINAL_URL = re.compile('var link="(.+?)"').findall(UNPACKED)[0]
                        if not 'http' in FINAL_URL:
                            FINAL_URL = 'http:'+ FINAL_URL
                        import urlresolver
                        return urlresolver.resolve(str(FINAL_URL))
                        
                except:pass

    def get_url(self, host, media_id):

        return 'https://streamapi.xyz/%s' % media_id
        

