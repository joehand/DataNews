from urlparse import urlparse
from dateutil import tz
from datetime import datetime


EPOCH = datetime(1970, 1, 1)

# Form validation

NAME_LEN_MIN = 2
NAME_LEN_MAX = 15

ILLEGAL_NAMES = ['active']

ALLOWED_TAGS = ['a', 'p','em','strong','code','pre','blockquote','ul','li','ol']
SUPER_TAGS = ['a', 'p','em','strong','code','pre','blockquote',
                'ul','li','ol','h3','h4','h5','h6','img']


def epoch_seconds(date):
    """Returns the number of seconds from the epoch to date."""
    td = date - EPOCH
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

def get_domain(url):
    """ Return just the domain (and subdomain!) for a url
    """
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    domain = domain.replace('www.', '')

    return domain


def local_time(utc=False):
    """ Make a utc time into a local time
    """
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    if not utc:
        utc = datetime.utcnow()
    utc = utc.replace(tzinfo=from_zone)

    return utc.astimezone(to_zone)

def pretty_date(dt, default=None):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    Ref: https://bitbucket.org/danjac/newsmeme/src/a281babb9ca3/newsmeme/
    """

    if default is None:
        default = 'just now'

    now = datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, 'year', 'years'),
        (diff.days / 30, 'month', 'months'),
        (diff.days / 7, 'week', 'weeks'),
        (diff.days, 'day', 'days'),
        (diff.seconds / 3600, 'hour', 'hours'),
        (diff.seconds / 60, 'minute', 'minutes'),
        (diff.seconds, 'second', 'seconds'),
    )

    for period, singular, plural in periods:

        if not period:
            continue

        if period == 1:
            return u'%d %s ago' % (period, singular)
        else:
            return u'%d %s ago' % (period, plural)

    return default


def paginate(query, page, per_page=20, error_out=True):
    """
       Paginate query if we can't use flask-sqlalchemy query (we use regular sqlalchemy one instead)
    """
    if error_out and page < 1:
        abort(404)
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    if not items and page != 1 and error_out:
        abort(404)

    # No need to count if we're on the first page and there are fewer
    # items than we expected.
    if page == 1 and len(items) < per_page:
        total = len(items)
    else:
        total = query.order_by(None).count()

    return Pagination(query, page, per_page, total, items)

