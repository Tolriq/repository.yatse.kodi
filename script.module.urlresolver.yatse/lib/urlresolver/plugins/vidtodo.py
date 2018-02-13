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
import re
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VidToDoResolver(UrlResolver):
    name = 'vidtodo'
    domains = ['vidtodo.com']
    pattern = '(?://|\.)(vidtodo\.com)/(?:embed-)?([0-9a-zA-Z]+)'
    
    def __init__(self):
        self.net = common.Net()
        
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            try:
                data = helpers.get_hidden(html)
                headers.update({'Referer': web_url})
                common.kodi.sleep(2000)
                _html = self.net.http_POST(web_url, headers=headers, form_data=data).content
                if _html:
                    sources = helpers.scrape_sources(_html)
                    if sources:
                        if len(sources) > 1:
                            sources = [source for source in sources if len(re.sub("\D", "", source[0])) <= 4]
                        return helpers.pick_source(sources) + helpers.append_headers(headers)
            except Exception as e:
                raise ResolverError(e)
            
        raise ResolverError('Unable to locate video')
        
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://vidtodo.com/{media_id}')
