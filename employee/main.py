from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
import polars as pl
import asyncio
import time

app = FastAPI()
executor = ThreadPoolExecutor(max_workers=2)

data_chache = None
last_updated = None
CACHE_REFRESH_INTERVAL = 300

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    print(f"Cache refresh at {last_updated}")

async def cache_updater():
    while True:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(executor,refresh_cache)
        await asyncio.sleep(CACHE_REFRESH_INTERVAL)

@app.on_event("startup")
async def startup_event():
    print("app starting, loading initial data....")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(executor,refresh_cache)
    asyncio.create_task(cache_updater())

@app.get('/employees')
async def get_employee():
    global data_chache,last_updated
    if not data_chache:
        return {'msg':"chache not ready, please wait.."}
    return{
        'last_updated':last_updated,
        'employess':data_chache
    }


    
        