import os
import logging
import pathlib
import hashlib
import sqlite3
from fastapi import FastAPI, Form, HTTPException, UploadFile, File, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()


db_path = "/Users/yunaotsuki/Documents/BUILD/mercari-build-training/db/mercari.sqlite3"

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

images_directory = pathlib.Path(__file__).parent.resolve() / "images"
os.makedirs(images_directory, exist_ok=True)

origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.post("/items")
async def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    try:
        file_content = await image.read()
        sha256_hash = hashlib.sha256(file_content).hexdigest()
        image_filename = sha256_hash + ".jpg"
        image_path = images_directory / image_filename
        with open(image_path, "wb") as f:
            f.write(file_content)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name, category, image_name) VALUES (?, ?, ?)",
                       (name, category, image_filename))
        conn.commit()
        conn.close()

        return {"message": "Item successfully added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        table = "items"
        sql_command = f"""CREATE TABLE IF NOT EXISTS {table} (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            category VARCHAR(255),
            image_name VARCHAR(255)
            );"""
        cursor.execute(sql_command)
        conn.close()
        logger.info("SQL login success")
    except Exception as e:
        logger.error(f"Error creating table: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/items")
async def get_items():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        items = cursor.fetchall()
        conn.close()
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/image/{image_name}")
async def get_image(image_name: str):
    try:
        image_path = images_directory / image_name
        if not image_path.exists():
            logger.debug(f"Image not found: {image_path}")
            image_path = images_directory / "default.jpg"
        return FileResponse(image_path)
    except Exception as e:
        logger.error(f"Error retrieving image: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/search")
async def search_items(keyword: str):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT name, category, image_name FROM items WHERE name LIKE ?"
            cursor.execute(query, ("%" + keyword + "%",))
            items = [{"name": row[0], "category": row[1], "image_name": row[2]} for row in cursor.fetchall()]

        if not items:
            raise HTTPException(status_code=404, detail=f"No items found for keyword: {keyword}")

        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

