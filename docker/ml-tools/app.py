from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("HERMES_PORT", 8001))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)

