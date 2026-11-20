import os
import socket

import boto3
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text

from predictor import predict_iris

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

S3_BUCKET = os.environ["S3_BUCKET"]
S3_REGION = os.environ.get("S3_REGION", "eu-west-1")
s3 = boto3.client(
    "s3",
    endpoint_url=os.environ.get("S3_ENDPOINT_URL"),
    aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("S3_SECRET_KEY"),
    region_name=S3_REGION,
)

app = FastAPI(title="CODA Monolith")


class Features(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    checks = {"db": "ok", "storage": "ok"}
    ok = True

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        checks["db"] = "error"
        ok = False

    try:
        s3.head_bucket(Bucket=S3_BUCKET)
    except Exception:
        checks["storage"] = "error"
        ok = False

    status_code = 200 if ok else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if ok else "not_ready", **checks},
    )


@app.get("/info")
def info():
    return {
        "hostname": socket.gethostname(),
        "version": os.environ.get("APP_VERSION", "monolith"),
        "db": "postgresql",
        "uploads": f"s3://{S3_BUCKET}",
    }


@app.post("/predict")
def predict(features: Features):
    values = [[features.sepal_length, features.sepal_width, features.petal_length, features.petal_width]]
    predicted = predict_iris(values[0])
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO predictions(features, predicted) VALUES (:features, :predicted)"),
            {"features": str(values[0]), "predicted": predicted},
        )
    return {"prediction": predicted, "hostname": socket.gethostname()}


@app.get("/predictions")
def predictions():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, features, predicted FROM predictions ORDER BY id")).fetchall()
    return [{"id": r[0], "features": r[1], "prediction": r[2]} for r in rows]


@app.post("/datasets")
async def upload_dataset(file: UploadFile = File(...)):
    content = await file.read()
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=file.filename,
        Body=content,
        ContentType=file.content_type or "application/octet-stream",
    )
    s3_path = f"s3://{S3_BUCKET}/{file.filename}"
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO datasets(name, path) VALUES (:name, :path)"),
            {"name": file.filename, "path": s3_path},
        )
    return {"name": file.filename, "path": s3_path, "hostname": socket.gethostname()}


@app.get("/datasets")
def datasets():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, name, path FROM datasets ORDER BY id")).fetchall()
    return [{"id": r[0], "name": r[1], "path": r[2]} for r in rows]
