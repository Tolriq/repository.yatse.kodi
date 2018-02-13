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
import re, base64
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class FlixtorResolver(UrlResolver):
    name = "flixtor"
    domains = ['flixtor.to']
    pattern = '(?://|\.)(flixtor\.to)/watch/([\w/\-]+)'
    
    def __init__(self):
        self.net = common.Net()
    
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA, 'Referer': 'https://flixtor.to/watch/%s' % media_id}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            try: html = base64.b64decode(html.encode("rot13"))
            except Exception as e: raise ResolverError(e)
            sources = helpers.scrape_sources(html)
            
            if sources: return helpers.pick_source(sources) + helpers.append_headers(headers)
            
        raise ResolverError("Unable to locate video")
    
    def get_url(self, host, media_id):
        if media_id.lower().startswith("tv/"): url = 'https://flixtor.to/ajax/getvid/e'
        else: url = 'https://flixtor.to/ajax/getvid/m'
        media_id = re.sub('/{2,}', '/', re.sub('[^\d/]', '', media_id))
        media_id = media_id[:-1] if media_id.endswith('/') else media_id
        
        return self._default_get_url(host, media_id, template = url + media_id)
        
