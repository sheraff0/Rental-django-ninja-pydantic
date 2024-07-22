from config.celery import app
from contrib.utils.decorators import nested_async
import bridge.travelline.content.services as services


@app.task
@nested_async
async def import_all():
    await services.import_meal_plans(save=True)
    await services.import_room_categories(save=True)
    await services.import_amenities(save=True)
    await services.import_all_properties(save=True, with_images=True)
