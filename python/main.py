# Import necessary modules
import os
import logging
import pathlib
import hashlib
import json
from fastapi import FastAPI, Form, HTTPException, UploadFile, File, Path
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO

# Define paths
images_directory = pathlib.Path(__file__).parent.resolve() / "images"
os.makedirs(images_directory, exist_ok=True)

# CORS settings
origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize a counter to keep track of the number of items added
item_counter = 0

# Endpoint for adding an item with an image
@app.post("/items")
async def add_item(name: str = Form(), category: str = Form(), image: UploadFile = File(...)):
    global item_counter  # Access the counter defined outside the function
    try:
        file_content = await image.read()
        sha256_hash = hashlib.sha256(file_content).hexdigest()
        image_filename = sha256_hash + ".jpg"  # Extract filename from full path
        image_path = images_directory / image_filename
        with open(image_path, "wb") as f:
            f.write(file_content)

        # Increment the counter for the new item ID
        item_counter += 1

        # Save item information to items.json
        item_dict = {"id": item_counter, "name": name, "category": category, "image": image_filename}  # Include the ID
        with open("items.json", "a") as file:
            json.dump(item_dict, file, indent=4)
            file.write("\n")

        return item_dict  # Return the item details including the ID
        
    except Exception as e:
        logger.error(f"Error adding item: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Endpoint for retrieving items
@app.get("/items")
async def return_items_json():
    try:
        items = []
        with open("items.json") as json_file:
            for line in json_file:
                item = json.loads(line.strip())
                items.append(item)
        return items
    except Exception as e:
        logger.error(f"Error retrieving items: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint for retrieving item details by ID
@app.get("/items/{item_id}")
async def return_item_details(item_id: int = Path(..., title="The ID of the item to retrieve")):
    try:
        with open("items.json") as json_file:
            for line in json_file:
                item = json.loads(line.strip())
                if item.get("id") == item_id:  # Assuming each item has an 'id' field
                    item.pop("id")  # Remove the 'id' field
                    return item
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Error retrieving item details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))

