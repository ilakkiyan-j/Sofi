from fastapi import FastAPI

app = FastAPI()

@app.get("/ping")
def ping():
    return {"message": "Sofi backend is alive and working!"}

# To run the server use -> uvicorn FastAPI:app --reload --port 5000

