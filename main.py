from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["Nagesh_db"]
euron_data = db["Nagesh_col"]

app = FastAPI()

class eurondata(BaseModel):
    name: str
    phone: int
    city: str
    course: str

# Helper function
def euron_helper(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


# CREATE - Insert
@app.post("/euron/insert")    
async def euron_data_insert_helper(data: eurondata):
    result = await euron_data.insert_one(data.dict())
    return str(result.inserted_id)


# READ - Get all data
@app.get("/euron/getdata")
async def get_euron_data():
    iterms = []
    cursor = euron_data.find({})
    async for document in cursor:
        iterms.append(euron_helper(document))
    return iterms


# READ - Get all data (duplicate endpoint)
@app.get("/euron/Alldata")
async def All_euron_data():
    iterms = []
    cursor = euron_data.find({})
    async for document in cursor:
        iterms.append(euron_helper(document))
    return iterms


# READ - Get single document by ID
@app.get("/euron/getdata/{id}")
async def get_euron_data_by_id(id: str):
    # Validate ObjectId
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Find document
    document = await euron_data.find_one({"_id": ObjectId(id)})
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return euron_helper(document)


# UPDATE - Partial update (PATCH) - Update specific fields only
@app.patch("/euron/update/{id}")
async def euron_data_partial_update(id: str, data: dict):
    # Validate ObjectId
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Remove None values
    update_data = {k: v for k, v in data.items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided to update")
    
    # Perform partial update using $set
    result = await euron_data.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Fetch and return updated document
    updated_doc = await euron_data.find_one({"_id": ObjectId(id)})
    
    return {
        "message": "Document partially updated successfully",
        "modified_count": result.modified_count,
        "data": euron_helper(updated_doc)
    }


# UPDATE - Full update (PUT) - Replace entire document
@app.put("/euron/update/{id}")
async def euron_data_full_update(id: str, data: eurondata):
    # Validate ObjectId
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Replace entire document
    result = await euron_data.replace_one(
        {"_id": ObjectId(id)},
        data.dict()
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Fetch and return updated document
    updated_doc = await euron_data.find_one({"_id": ObjectId(id)})
    
    return {
        "message": "Document fully updated successfully",
        "modified_count": result.modified_count,
        "data": euron_helper(updated_doc)
    }


# DELETE - Delete document by ID
@app.delete("/euron/delete/{id}")
async def euron_data_delete(id: str):
    # Validate ObjectId
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Delete document
    result = await euron_data.delete_one({"_id": ObjectId(id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "message": "Document deleted successfully",
        "deleted_id": id,
        "deleted_count": result.deleted_count
    }