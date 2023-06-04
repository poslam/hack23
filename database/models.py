from database.database import base
from sqlalchemy import (
    TIMESTAMP,
    Double,
    Enum,
    Column,
    ForeignKey,
    Integer,
    TEXT,
    String,
)
import enum

class UserTypes(enum.Enum):
    admin = "admin" 
    regular_user = "regular_user"
    

class ComponentStatuses(enum.Enum):
    active = "active"
    inactive = "inactive"
    
    
class TaskStatuses(enum.Enum):
    inactive = "inactive"
    active = "active"
    done = "done"


class User(base):
    __tablename__ = "client"
    
    id = Column(Integer, primary_key=True)
        
    num = Column(Integer, unique=True)
    
    first_name = Column(TEXT)
    second_name = Column(TEXT)
    third_name = Column(TEXT)

    password = Column(TEXT)
    type = Column(Enum(UserTypes), default="regular_user")
    
    
class Product(base):
    __tablename__ = "product"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
   
    
class Receipt(base):
    __tablename__ = "receipt"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    product_id = Column(ForeignKey(Product.id))
    
    
class Component(base):
    __tablename__ = "component"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    receipt_id = Column(ForeignKey(Receipt.id))
    
    weight = Column(Double)
    status = Column(Enum(ComponentStatuses), default="active")
    
    activation_date = Column(TIMESTAMP)
    
    
class Load(base):
    __tablename__ = "load"
    
    id = Column(Integer, primary_key=True)
    
    receipt_id = Column(ForeignKey(Receipt.id))
    
    out_weight = Column(Integer)
    date = Column(TIMESTAMP)
    

class Param(base):
    __tablename__ = "param"
    
    id = Column(Integer, primary_key=True)
    
    name = Column(String)
    value = Column(Integer)
    
    receipt_id = Column(ForeignKey(Receipt.id))
    
    status = Column(Enum(ComponentStatuses), default="active")
    activation_date = Column(TIMESTAMP)


class Shift(base):
    __tablename__ = "shift"
    
    id = Column(Integer, primary_key=True)
    
    user_id = Column(ForeignKey(User.id))
    
    date = Column(TIMESTAMP)
    shift_time = Column(Integer)
    

class Task(base):
    __tablename__ = "task"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(User.id))
    
    name = Column(TEXT)
    
    begin = Column(TIMESTAMP)
    end = Column(TIMESTAMP)
    
    status = Column(Enum(TaskStatuses))
    value = Column(TEXT)
    
    done_time = Column(TIMESTAMP)