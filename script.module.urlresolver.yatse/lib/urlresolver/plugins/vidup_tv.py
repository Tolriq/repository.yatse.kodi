"""
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
import json
import urllib
import urllib2
from urlresolver import common
from urlresolver.common import i18n
from lib import helpers
from urlresolver.resolver import UrlResolver, ResolverError


class VidUpTVResolver(UrlResolver):
    name = "vidup.tv"
    domains = ["vidup.tv","vidup.me"]
    pattern = '(?://|\.)(vidup\.tv|vidup\.me)/(?:embed-|download/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()
        self.headers = {'Host':'vidup.tv',
                        'Cache-Control':'max-age=0',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate',
                        'Accept-Language':'en-US,en;q=0.9',
                        'Connection':'keep-alive'}

        
    def get_media_url(self, host, media_id):

        web_url = self.get_url(host, media_id)

        headers=self.headers
        
        html      =   self.net.http_GET(web_url, headers=headers).content

        URL=[]
        match     =   re.compile('{"file":"(.+?)".+?"label":"(.+?)p').findall(html)

        for source , res in match:
            URL.append([(int(res)),source])


        thief     =  re.compile("thief='(.+?)'").findall(html)[0]
        
        the_thief =  self.net.http_GET('http://vidup.tv/jwv/'+thief, headers=headers).content

        Ending    =  re.compile('direct\|(.+?)\|').findall(the_thief)[0]
        
        return max(URL)[1]+'?direct=false&ua=1&vt='+Ending

        
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
