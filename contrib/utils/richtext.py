import re

from .cached import get_images_index


def richtext(text):
    def image_match(m):
        _id = int(m.group(2))
        src = _images_cache.get(_id)
        alt = m.group(1)
        return f'<img src="{src}" alt="{alt}">'

    _images_cache = get_images_index()
    return re.sub(r'<embed alt="([^"]+)"[^>]+embedtype="image"[^>]+id="(\d+)"[^>]*>', image_match,
        re.sub(r' data-block-key="[\w\d]+"', '', text))
