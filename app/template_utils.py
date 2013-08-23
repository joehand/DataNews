from jinja2 import Markup
from urlparse import urlparse

def get_domain(url):
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    domain = domain.replace('www.', '')

    return domain