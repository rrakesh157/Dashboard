from dotenv import load_dotenv
import asyncpg
import os


load_dotenv()
if os.getenv('user') == 'postgres':
    DB_URL = f'postgresql://{os.getenv('user')}:{os.getenv('password')}@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('database')}'

async def get_connection():
    conn = await asyncpg.connect(DB_URL)
    return conn


