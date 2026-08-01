from fastapi import FastAPI

app = FastAPI()


@app.get("/", summary="API metadata")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}
