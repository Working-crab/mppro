import fastapi
import time
import datetime

route = fastapi.APIRouter()

@route.get('/')
async def main ():
    # return {datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}
    return {}

