from fastapi import FastAPI
import polars as pl


app = FastAPI()


@app.get('/daysales')
async def getdaysales():
    try:
        df = pl.read_excel('daysales.xlsx')
        return df.to_dicts()

    except Exception as e:
        return {'msg': str(e)}
    
@app.post('/monthsales')
async def getmonthsales():
    try:
        df = pl.read_excel('monthsales.xlsx')
        return df.to_dicts()

    except Exception as e:
        return {'msg': str(e)}
    


