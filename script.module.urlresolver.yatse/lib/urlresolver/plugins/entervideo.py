"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

    urlresolver XBMC Addon
    Copyright (C) 2018 gujal

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

class EnterVideoResolver(UrlResolver):
    name = "entervideo"
    domains = ['entervideo.net']
    pattern = '(?://|\.)(entervideo\.net)/(?:watch/)?([0-9a-zA-Z]+)'
    
    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        response = self.net.http_GET(web_url, headers=headers)
        html = response.content
        if 'Not Found' in html:
            raise ResolverError('File Removed')       
        headers['Referer'] = web_url
        stream_url = re.findall('source src="([^"]+)', html)[0]
        return stream_url + helpers.append_headers(headers)
        
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://entervideo.net/watch/{media_id}')
