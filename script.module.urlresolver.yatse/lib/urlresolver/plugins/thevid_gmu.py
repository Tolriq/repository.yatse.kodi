"""
thevid.net urlresolver plugin
Copyright (C) 2015 tknorris

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
from lib import jsunpack
import re
logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()



        
def get_media_url(url):
        net = common.Net()
    
        html = net.http_GET(url).content
        match=re.compile('<script>(.+?)</script>',re.DOTALL).findall(html)
        
        for source in match:
            source =source.strip()
            try:

                UNPACKED = jsunpack.unpack(source)
                if 'sfilea' in UNPACKED:
                    FINAL_URL = re.compile('sfilea="(.+?)"').findall(UNPACKED)[0]
                    if not 'http' in FINAL_URL:
                        FINAL_URL = 'http:'+ FINAL_URL
                    return FINAL_URL
            except:pass
