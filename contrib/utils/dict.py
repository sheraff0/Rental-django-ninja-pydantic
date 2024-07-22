from functools import reduce


def dict_path(data, path):
    def get_key(acc, curr):
        return acc.get(curr, {}) if type(acc) == dict else acc[0].get(curr, {}) if type(acc) == list else {}
    return reduce(get_key, path.split('/'), data)


def flatten_nested_dict(dict_):
    return {k: v for _, x in dict_.items() for k, v in x.items()}
