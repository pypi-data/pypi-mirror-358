# -*- coding: utf-8 -*-
# author: NhanDD3 <hp.duongducnhan@gmail.com>

import re


def get_func_name(func):
    try:
        return f"<{func.__name__}>"
    except AttributeError:
        return f"<{str(func)}>"

def replace_domain(url, domain):
    new = re.sub(r"http[s]*?://[^/ | ^?]+", domain, url)
    return new