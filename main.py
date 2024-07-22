from fastapi import FastAPI,APIRouter

app = FastAPI()

router = APIRouter()




app.include_router(router, tags=['main'])




