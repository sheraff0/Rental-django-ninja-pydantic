def exclude_wagtail_endpoints(endpoints):
    return [x for x in endpoints if "cms/api" not in x[0]]
