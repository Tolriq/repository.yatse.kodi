# -*- coding: utf-8 -*-
"""
urlresolver XBMC Addon
Copyright (C) 2011 t0mm0

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
from __generic_resolver__ import GenericResolver

class RapidVideoComResolver(GenericResolver):
    name = "rapidvideo.com"
    domains = ["rapidvideo.com", "raptu.com"]
    pattern = '(?://|\.)((?:rapidvideo|raptu)\.com)/(?:[ev]/|embed/|\?v=)?([0-9A-Za-z]+)'

    def get_media_url(self, host, media_id):

        url = self.get_url(host, media_id)
        net = common.Net()
        headers = {'User-Agent': common.RAND_UA}

        response = net.http_GET(url, headers=headers)
        response_headers = response.get_headers(as_dict=True)
        headers.update({'Referer': url})
        cookie = response_headers.get('Set-Cookie', None)
        if cookie:
            headers.update({'Cookie': cookie})
            html = response.content

        source_list = helpers.scrape_sources(html, generic_patterns = True)
        if source_list and len(source_list[0]) > 1:
            source_list[0][::-1]
        source = helpers.pick_source(source_list)
        return source + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}?q=all')
