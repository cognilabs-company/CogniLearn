from fastapi import FastAPI, APIRouter
from auth import auth
from routers import roles

app = FastAPI()

router = APIRouter()


app.include_router(router, tags=['main'])

app.include_router(auth.router)
app.include_router(roles.router)





