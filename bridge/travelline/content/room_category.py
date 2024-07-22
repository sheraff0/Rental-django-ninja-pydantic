from external.travelline.schemas.content import RoomCategory as RoomCategoryInfo
from apps.shared.models import RoomTypeCategory
from contrib.common.cached import CachedModelMap
from .import_data import ImportData


class RoomCategoryImport(ImportData):
    source_model = RoomCategoryInfo
    db_model = RoomTypeCategory


get_room_type_category = CachedModelMap(RoomTypeCategory)
