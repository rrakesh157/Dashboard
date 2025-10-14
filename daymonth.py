from fastapi import FastAPI
import polars as pl
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
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
    


