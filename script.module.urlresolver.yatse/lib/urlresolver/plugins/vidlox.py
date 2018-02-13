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

class VidloxResolver(UrlResolver):
    name = "vidlox"
    domains = ['vidlox.tv']
    pattern = '(?://|\.)(vidlox\.tv)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.IE_USER_AGENT, 'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        try: sources = re.search(r'sources\s*:\s*\[(.+?)\]', html).groups()[0]
        except: raise ResolverError('Unable to locate link')

        if sources:
            sources = helpers.scrape_sources(sources, patterns=['''["'](?P<url>http[^"']+)'''])
            if sources: return helpers.pick_source(sources) + helpers.append_headers(headers)
            
        raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
