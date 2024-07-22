from io import BytesIO
import re

from django.apps import apps
from django.core.files.images import ImageFile

from contrib.utils.async_api_client import AsyncClient


class ImageSetter:
    def __init__(self, parent_object, url, sort_order):
        self.parent_object = parent_object
        self.url = url
        self.sort_order = sort_order
        self.ImageModel = parent_object.images.model
        self.tl_id = self.get_tl_id()

    def get_tl_id(self):
        try: return re.search(r"([^/]+$)", self.url).group()
        except: ...

    async def fetch_image(self):
        if not self.tl_id:
            return

        client = AsyncClient(self.url)
        res = await client.request(result_method="read")
        await client.close()

        _buffer = BytesIO(res)
        _file = ImageFile(_buffer, name=f"{self.tl_id}.jpg")

        return _file

    async def set_image(self):
        if not (_image := await self.ImageModel.objects.filter(tl_id=self.tl_id).afirst()):
            _file = await self.fetch_image()
            _image = await self.ImageModel.objects.acreate(
                tl_id=self.tl_id,
                parent=self.parent_object,
                image=_file,
                sort_order=self.sort_order,
            )
        elif _image.sort_order != self.sort_order:
            _image.sort_order = self.sort_order
            await _image.asave()

        return _image.id

    async def __call__(self):
        return await self.set_image()
