# -*- coding: utf-8 -*-

import datetime, simplejson, decimal
error_mapping = {
    "LOGIN_NEEDED": (1, "login needed"),
    "PERMISSION_DENIED": (2, "permission denied"),
    "DATABASE_ERROR": (3, "operate database error"),
    "ONLY_FOR_AJAX": (4, "the url is only for ajax request")
}

class ApiError(Exception):
    def __init__(self, key, **kwargs):
        Exception.__init__(self)
        self.key = key if key in error_mapping else "UNKNOWN"
        self.kwargs = kwargs

def ajax_required(func):
    def __decorator(request, *args, **kwargs):
        if request.is_ajax:
            return func(request, *args, **kwargs)
        else:
            raise ApiError("ONLY_FOR_AJAX")
    return __decorator

def safe_new_datetime(d):
    kw = [d.year, d.month, d.day]
    if isinstance(d, datetime.datetime):
        kw.extend([d.hour, d.minute, d.second, d.microsecond, d.tzinfo])
    return datetime.datetime(*kw)

def safe_new_date(d):
    return datetime.date(d.year, d.month, d.day)

class DatetimeJSONEncoder(simplejson.JSONEncoder):
    """可以序列化时间的JSON"""

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):
            d = safe_new_datetime(o)
            return d.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            d = safe_new_date(o)
            return d.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(DatetimeJSONEncoder, self).default(o)