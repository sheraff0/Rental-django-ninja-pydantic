from external.travelline.schemas.content import MealPlan as MealPlanInfo
from apps.shared.models import MealPlan
from contrib.common.cached import CachedModelMap
from .import_data import ImportData


class MealPlanImport(ImportData):
    source_model = MealPlanInfo
    db_model = MealPlan


get_meal_plan = CachedModelMap(MealPlan)
