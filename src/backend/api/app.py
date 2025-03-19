from fastapi import FastAPI

app = FastAPI()

@app.get("/d2/user/{destiny_id}")
async def get_user(destiny_id: int):
    return {"destiny_id": destiny_id}