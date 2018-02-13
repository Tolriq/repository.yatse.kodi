"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

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

import re
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class MehlizMoviesResolver(UrlResolver):
    name = "mehlizmovies"
    domains = ["mehlizmovies.com"]
    pattern = '(?://|\.)(mehlizmovies\.com)/player/embed\.php\?url=([a-zA-Z0-9+/=]+)'
    
    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            sources = re.findall('''file:\s*["']([^"']+).+?label:\s*["']([^"']+)''', html)
            if sources:
                sources = [(source[1], source[0]) for source in sources]
                if len(sources) > 1:
                    try: sources.sort(key=lambda x: int(re.sub("\D", "", x[0])), reverse=True)
                    except: common.logger.log_debug('Scrape sources sort failed |int(re.sub("\D", "", x[0])|')
                    
                return helpers.pick_source(sources) + helpers.append_headers(headers)
            
        raise ResolverError('Video not found')
    
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/player/embed.php?url={media_id}')
