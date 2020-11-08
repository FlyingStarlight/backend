import typing as t
from pydantic import BaseModel

from app.db.schemas.user import UserOut


class ServerBase(BaseModel):
    name: str
    address: str


class ServerOut(ServerBase):
    id: int

    class Config:
        orm_mode = True


class ServerOpsOut(ServerOut):
    id: int
    ansible_name: str
    ansible_host: t.Optional[str]
    ansible_port: t.Optional[int]
    is_active: bool

    class Config:
        orm_mode = True


class ServerCreate(ServerBase):
    ansible_name: str
    ansible_host: t.Optional[str] = None
    ansible_port: t.Optional[int] = 22

    class Config:
        orm_mode = True


class ServerEdit(BaseModel):
    name: t.Optional[str]
    address: t.Optional[str]
    ansible_name: t.Optional[str]
    ansible_host: t.Optional[str]
    ansible_port: t.Optional[int]
    is_active: t.Optional[bool]

    class Config:
        orm_mode = True


class Server(ServerBase):
    id: int

    class Config:
        orm_mode = True


class ServerUserBase(BaseModel):
    server_id: int
    user_id: int


class ServerUserOut(ServerUserBase):
    # server: ServerOut
    # user: UserOut

    class Config:
        orm_mode = True


class ServerUserEdit(BaseModel):
    user_id: int

    class Config:
        orm_mode = True
