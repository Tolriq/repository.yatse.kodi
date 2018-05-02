"""
    Kodi urlresolver plugin
    Copyright (C) 2016  script.module.urlresolver

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
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class StreamDorResolver(UrlResolver):
    name = "streamdor"
    domains = ["streamdor.co"]
    pattern = '(?://|\.)(streamdor\.co)/(?:video\d*/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        match=re.compile('JuicyCodes\.Run\((.+?)\)').findall(html)[0]
        juicy = match.replace('"+"','').replace('"','')
        
        theeval = base64.b64decode(juicy)
        unpacked = jsunpack.unpack(theeval)

        result = re.compile('"fileEmbed":"(.+?)"').findall(unpacked)[0]

        import urlresolver
        return urlresolver.resolve(str(result))

    def get_url(self, host, media_id):

        return 'https://embed.streamdor.co/video/%s'  % media_id
