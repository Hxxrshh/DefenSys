from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Test DefenSys API")

@app.get("/")
async def root():
    return {"message": "Test server is working"}

@app.get("/test")
async def test():
    return {"status": "ok", "test": "successful"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8004)