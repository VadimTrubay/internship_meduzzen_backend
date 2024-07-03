import time
import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

origins = [
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status_code": 200,
            "detail": "ok",
            "result": "working"
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, reload=True)
