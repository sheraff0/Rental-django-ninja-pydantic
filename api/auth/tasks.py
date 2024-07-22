from config.celery import app

from contrib.utils.decorators import nested_async
from api.auth.services import clear_unused_guest_accounts


@app.task
@nested_async
async def clear_unused_guest_accounts_task():
    await clear_unused_guest_accounts()
