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
import urlparse
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VidZellaResolver(UrlResolver):
    name = "vidzella"
    domains = ['vidzella.me', 'dl.vidzella.me']
    pattern = '(?://|\.)(vidzella.me)/(?:play/?#|e/|stream\.php\?stream=)([0-9a-zA-Z]+)'
    
    def get_media_url(self, host, media_id):
        url = helpers.get_media_url(self.get_url(host, media_id), result_blacklist=['intro_black']).replace(' ', '%20')
        net = common.Net()
        headers = {}

        if '|' in url:
            qs_header_split = url.split('|')
            url = qs_header_split[0]

            headers = urlparse.parse_qs(qs_header_split[1])
            headers = dict((k, v[0]) for k, v in headers.iteritems())

        response = net.http_HEAD(url, headers=headers)
        if(response.get_url()):
            return response.get_url() + helpers.append_headers(headers)
        else:
            raise ResolverError(common.i18n('no_video_link'))
    
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://vidzella.me/e/{media_id}')
        
