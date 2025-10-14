from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import concurrent.futures
import time
import polars as pl


CACHE_REFRESH_INTERVAL = 500
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

data_chache = []
last_updated = None


def read_excel_data():
    print('reading Excel file....')
    df = pl.read_excel('users_data-1.xlsx')
    users = []
    for row in df.to_dicts():
        user = {
            "id": row.get("id"),
            "name": row.get("name"),
            "username": row.get("username"),
            "email": row.get("email"),
            "address": {
                "street": row.get("address.street"),
                "suite": row.get("address.suite"),
                "city": row.get("address.city"),
                "zipcode": row.get("address.zipcode"),
                "geo": {
                    "lat": row.get("address.geo.lat"),
                    "lng": row.get("address.geo.lng"),
                },
                },
            "icon" : row.get("icon"),
            "status" : row.get("status"),
            "phone": row.get("phone"),
            "website": row.get("website"),
            "company": {
                "name": row.get("company.name"),
                "catchPhrase": row.get("company.catchPhrase"),
                "bs": row.get("company.bs"),
            },
        }
        users.append(user)
    return users


def refresh_cache():
    
    global data_chache, last_updated
    data_chache = read_excel_data()
    last_updated = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"✅ Cache refreshed at {last_updated}")


async def cache_updater():
    
    while True: #Runs continuously to refresh cache periodically
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(executor, refresh_cache)
        await asyncio.sleep(CACHE_REFRESH_INTERVAL)


@asynccontextmanager  #Handles startup and shutdown lifecycle for the app.
async def lifespan(app: FastAPI):
    
    print("🚀 App starting, loading initial data...")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(executor, refresh_cache)
    background_task = asyncio.create_task(cache_updater())
    yield  
    # When app shuts down, cancel the background task
    background_task.cancel()
    print("App shutting down, cleaning up resources...")



app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:5173",
    "http://localhost:8080",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/daysales')
async def getdaysales():
    try:
        df = pl.read_excel('daysales.xlsx')
        return df.to_dicts()

    except Exception as e:
        return {'msg': str(e)}
    
@app.get('/monthsales')
async def getmonthsales():
    try:
        df = pl.read_excel('monthsales.xlsx')
        return df.to_dicts()

    except Exception as e:
        return {'msg': str(e)}


@app.get('/employees')
async def get_employee():
    global data_chache, last_updated
    if not data_chache:
        return {'msg': "cache not ready, please wait..."}
    return {
        'last_updated': last_updated,
        'employees': data_chache
    }

    
        
