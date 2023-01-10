import requests
import re

ABS_URL_REGEX = r"(((https?://|www\.|https?://www\.)([a-zA-Z0-9_\-~\(\)]+\.)+[a-z]+(\:\d+)?)(/[a-zA-Z0-9#_=\(\)\:\&\?%\-/\.]*)*)"
REL_URL_REGEX = r"(href|src)=\"(/{1,2}.+?)\""


class WebClawler:
    def __init__(self, max_depth=1):
        self.current_depth = 1
        self.max_depth = max_depth
        self.visited_urls = set()
        self.result = set()
        self.is_valid_root_url = False

    def _is_valid_response(self, resp: requests.Response):
        return resp.status_code == 200 and 'text/html' in resp.headers['Content-Type']

    def _get_url_with_protocol(self, protocol: str, url: str):
        return url if url.startswith('http') else (protocol + '//' + url)

    def _get_full_url(self, domain: str, protocol: str, url: str):
        return (protocol if url.startswith('//') else domain) + url

    def _handler(self, url):
        match = re.findall(ABS_URL_REGEX, url)[0]
        domain = match[1]
        protocol = match[2][:-2]
        self.result.add(domain)

        try:
            resp = requests.get(url)
        except:
            return []

        if not self._is_valid_response(resp):
            resp.close()
            return []

        self.is_valid_root_url = True

        abs_url_matches = re.findall(ABS_URL_REGEX, resp.text)
        abs_urls = [self._get_url_with_protocol(
            protocol, x[0]) for x in abs_url_matches]

        rel_url_matches = re.findall(REL_URL_REGEX, resp.text)
        rel_urls = [self._get_full_url(domain, protocol, x[1])
                    for x in rel_url_matches]

        urls = abs_urls + rel_urls

        self.result = self.result.union(urls)
        resp.close()

        return urls

    def get_links(self, URL):
        urls_to_visit = [URL]
        while self.current_depth <= self.max_depth:
            new_urls = []

            for url in urls_to_visit:
                if url in self.visited_urls:
                    continue

                new_urls = new_urls + self._handler(url)
                self.visited_urls.add(url)

            urls_to_visit = new_urls
            self.current_depth = self.current_depth + 1

        if not self.is_valid_root_url:
            return None

        return self.result
        return sorted(self.result)
