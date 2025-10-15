from fastapi import FastAPI,Path,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from database import get_connection
from schemas import UpdateEmployee,EmployeeOut
import asyncio
import polars as pl

conn = ''
executor = ThreadPoolExecutor(max_workers=5)

@asynccontextmanager
async def lifespan(app:FastAPI):
    global conn
    print("App starting, loading initial data...")
    conn = await get_connection()
    yield
    await conn.close()
    print("App shutting down, cleaning up resources...")


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:5174",
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
        loop = asyncio.get_running_loop()
        df = await loop.run_in_executor(executor, pl.read_excel, 'daysales.xlsx')
        return df.to_dicts()
    except Exception as e:
        return {'msg': str(e)}
    

@app.get('/monthsales')
async def getmonthsales():
    try:
        loop = asyncio.get_running_loop()
        df = await loop.run_in_executor(executor, pl.read_excel, 'monthsales.xlsx')
        return df.to_dicts()
    except Exception as e:
        return {'msg': str(e)}



@app.get('/employeedata')
async def employee_all_data():
    query = 'select * from employee'
    data = await conn.fetch(query)
    if not data:
        raise HTTPException(status_code=404, detail='Employee data not found')
    return {'msg':data}

@app.get('/employeedata/{id}',response_model=EmployeeOut)
async def employee_data(id:int = Path(...,description='Enter the employee id')):
    try:
        query = 'select * from employee where id = $1'
        data = await conn.fetchrow(query,id)
        if not data:
            raise HTTPException(status_code=404, detail=f'Employee {id} Not Found')
        return dict(data)
    except Exception as e:
        return {'Error':str(e)}
    

@app.get('/employee_id_data/{id}',response_model=UpdateEmployee)
async def employee_id_data(id:int = Path(...,description='Enter the employee id')):
    try:
        query = 'select * from employee where id = $1'
        data = await conn.fetchrow(query,id)
        if not data:
            raise HTTPException(status_code=404, detail=f'Employee {id} Not Found')
        return dict(data)
    except Exception as e:
        return {'Error':str(e)}



@app.patch('/updateemployee/{id}')
async def updateemploye(
    details:UpdateEmployee,
    id:int = Path(...,description='Employee id to update')):
    query_parts = []
    values = []
    i = 1
    for feilds, value in details.dict(exclude_unset=True).items():
        query_parts.append(f'{feilds} = ${i}')
        values.append(value)
        i += 1
    values.append(id)
    query = f"update employee set {','.join(query_parts)} where id = ${i}"

    data = await conn.execute(query,*values)
    print(data)
    if not data:
        raise HTTPException(status_code=404,detail=f'Employee {id} not Found')
    return {'msg':f'Updated {data} '}


