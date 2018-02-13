"""
    Kodi urlresolver plugin
    Copyright (C) 2017 alifrezser
    
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
import re, urlparse
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class PowVideoResolver(UrlResolver):
    name = "powvideo"
    domains = ["powvideo.net"]
    pattern = '(?://|\.)(powvideo.net)/(?:embed-|iframe-|preview-)?([0-9a-zA-Z]+)'
    
    def __init__(self):
        self.net = common.Net()
    
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA, 'Referer': web_url.replace("iframe-", "preview-")}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            sources = helpers.scrape_sources(html, patterns=['''src\s*:\s*["'](?P<url>[^"']+)'''])
            data = re.findall("""_[^=]+=\[([^\]]+)\];""", html, re.DOTALL)
            if sources and data:
                data = data[3].replace('\\x', '').split(",")
                data = [x.replace('"', '').replace(' ', '').decode("hex") for x in data]
                key = "".join(data[7:9])
                if key.startswith("embed"):
                    key = key[6:]+key[:6]
                i = 0
                headers.update({'Referer': web_url})
                for source in sources:
                    try:
                        src = urlparse.urlparse(source[1])
                        l = list(src)
                        b = l[2].split("/")[1:]
                        b[0] = self.decrypt(b[0], key)
                        l[2] = "/".join(b)
                        sources[i] = (source[0], urlparse.urlunparse(l))
                        i += 1
                    except:
                        i += 1
                    
                return helpers.pick_source(sources) + helpers.append_headers(headers)
            
        raise ResolverError('File not found')
        
    def decrypt(self, h, k):
        import base64

        if len(h) % 4:
            h += "="*(4-len(h) % 4)

        sig = []
        h = base64.b64decode(h.replace("-", "+").replace("_", "/"))
        for c in range(len(h)):
            sig += [ord(h[c])]

        sec = []
        for c in range(len(k)):
            sec += [ord(k[c])]

        dig = range(256)
        g = 0
        v = 128
        for b in range(len(sec)):
            a = (v + (sec[b] & 15)) % 256
            c = dig[(g)]
            dig[g] = dig[a]
            dig[a] = c
            g += 1

            a = (v + (sec[b] >> 4 & 15)) % 256
            c = dig[g]
            dig[g] = dig[a]
            dig[a] = c
            g += 1

        k = 0
        q = 1
        p = 0
        n = 0
        for b in range(512):
            k = (k + q) % 256
            n = (p + dig[(n + dig[k]) % 256]) % 256
            p = (k + p + dig[n]) % 256
            c = dig[k]
            dig[k] = dig[n]
            dig[n] = c

        q = 3
        for a in range(v):
            b = 255 - a
            if dig[a] > dig[b]:
                c = dig[a]
                dig[a] = dig[b]
                dig[b] = c

        k = 0
        for b in range(512):
            k = (k + q) % 256
            n = (p + dig[(n + dig[k]) % 256]) % 256
            p = (k + p + dig[n]) % 256
            c = dig[k]
            dig[k] = dig[n]
            dig[n] = c

        q = 5
        for a in range(v):
            b = 255 - a
            if dig[a] > dig[b]:
                c = dig[a]
                dig[a] = dig[b]
                dig[b] = c

        k = 0
        for b in range(512):
            k = (k + q) % 256
            n = (p + dig[(n + dig[k]) % 256]) % 256
            p = (k + p + dig[n]) % 256
            c = dig[k]
            dig[k] = dig[n]
            dig[n] = c

        q = 7
        k = 0
        u = 0
        d = []
        for b in range(len(dig)):
            k = (k + q) % 256
            n = (p + dig[(n + dig[k]) % 256]) % 256
            p = (k + p + dig[n]) % 256
            c = dig[k]
            dig[k] = dig[n]
            dig[n] = c
            u = dig[(n + dig[(k + dig[(u + p) % 256]) % 256]) % 256]
            d += [u]

        c = []
        for f in range(len(d)):
            try: c += [(256 + (sig[f] - d[f])) % 256]
            except: break

        h = ""
        for s in c:
          h += chr(s)

        return h

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/iframe-{media_id}-640x360.html')
