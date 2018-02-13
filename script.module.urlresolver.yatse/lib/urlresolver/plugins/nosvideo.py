'''
Nosvideo urlresolver plugin
Copyright (C) 2013 Vinnydude

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
'''
import re
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class NosvideoResolver(UrlResolver):
    name = "nosvideo"
    domains = ["nosvideo.com", "noslocker.com"]
    pattern = '(?://|\.)(nosvideo.com|noslocker.com)/(?:\?v\=|embed/|.+?\u=)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        html += helpers.get_packed_data(html)
        match = re.search('playlist\s*:\s*"([^"]+)', html)
        if match:
            xml = self.net.http_GET(match.group(1), headers=headers).content
            count = 1
            sources = []
            streams = set()
            for match in re.finditer('''file="([^'"]*mp4)''', xml):
                stream_url = match.group(1)
                if stream_url not in streams:
                    sources.append(('Source %s' % (count), stream_url))
                    streams.add(stream_url)
                    count += 1
            
        return helpers.pick_source(sources) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return 'http://nosvideo.com/embed/%s' % media_id
