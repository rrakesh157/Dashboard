from pydantic import BaseModel,EmailStr
from typing import Optional

class UpdateEmployee(BaseModel):
    name:Optional[str] = None
    email:Optional[EmailStr] = None
    phone:Optional[str] = None
    website:Optional[str] = None
    company_name:Optional[str] = None 
    status:Optional[str] = None

class EmployeeOut(BaseModel):
    name:Optional[str] = None
    email:Optional[EmailStr] = None
    phone:Optional[str] = None