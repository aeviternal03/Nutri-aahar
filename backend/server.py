from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class EnquiryCreate(BaseModel):
    enquiry_type: str = "quote"
    name: str
    company: Optional[str] = ""
    email: str
    phone: Optional[str] = ""
    country: Optional[str] = ""
    product: Optional[str] = ""
    quantity: Optional[str] = ""
    packaging: Optional[str] = ""
    destination: Optional[str] = ""
    subject: Optional[str] = ""
    message: str

class EnquiryResponse(EnquiryCreate):
    id: str
    created_at: str

PRODUCTS = [
    {"slug":"cumin-seeds","name":"Cumin Seeds","local":"Jeera","category":"Whole Spices","image":"https://images.pexels.com/photos/18778270/pexels-photo-18778270.jpeg?auto=compress&cs=tinysrgb&w=900","description":"Warm, earthy cumin seeds for authentic Indian kitchens and food businesses.","uses":"Tempering, spice blends, breads and pickles"},
    {"slug":"green-cardamom","name":"Green Cardamom","local":"Hari Elaichi","category":"Whole Spices","image":"https://images.pexels.com/photos/4110333/pexels-photo-4110333.jpeg?auto=compress&cs=tinysrgb&w=900","description":"Aromatic green cardamom with a bright, naturally sweet fragrance.","uses":"Chai, desserts, rice dishes and masalas"},
    {"slug":"black-pepper","name":"Black Peppercorns","local":"Kali Mirch","category":"Whole Spices","image":"https://images.pexels.com/photos/4198019/pexels-photo-4198019.jpeg?auto=compress&cs=tinysrgb&w=900","description":"Bold, warming peppercorns that bring depth to every preparation.","uses":"Seasoning, marinades, curries and sauces"},
    {"slug":"cinnamon-cassia","name":"Cinnamon / Cassia","local":"Dalchini","category":"Whole Spices","image":"https://images.pexels.com/photos/4198714/pexels-photo-4198714.jpeg?auto=compress&cs=tinysrgb&w=900","description":"Fragrant cinnamon bark for sweet and savoury Indian recipes.","uses":"Biryani, chai, baking and spice blends"},
    {"slug":"makhana","name":"Makhana / Foxnuts","local":"Makhana","category":"Makhana","image":"https://images.pexels.com/photos/4198929/pexels-photo-4198929.jpeg?auto=compress&cs=tinysrgb&w=900","description":"A versatile Indian ingredient for mindful snacking and modern recipes.","uses":"Roasting, snacking, curries and desserts"},
    {"slug":"dates","name":"Dates","local":"Khajoor","category":"Dates & Dry Fruits","image":"https://images.pexels.com/photos/752505/pexels-photo-752505.jpeg?auto=compress&cs=tinysrgb&w=900","description":"Naturally rich dates for everyday nourishment and food innovation.","uses":"Snacking, desserts, energy bites and baking"},
    {"slug":"coriander-seeds","name":"Coriander Seeds","local":"Sabut Dhaniya","category":"Seeds & Specialty","image":"https://images.pexels.com/photos/4198843/pexels-photo-4198843.jpeg?auto=compress&cs=tinysrgb&w=900","description":"Citrusy coriander seeds at home in classic masalas and contemporary blends.","uses":"Ground masala, pickles, curries and roasting"},
    {"slug":"fennel-seeds","name":"Fennel Seeds","local":"Saunf","category":"Seeds & Specialty","image":"https://images.pexels.com/photos/4110254/pexels-photo-4110254.jpeg?auto=compress&cs=tinysrgb&w=900","description":"Delicately sweet fennel seeds with a clean, refreshing finish.","uses":"Mukhwas, breads, teas and spice blends"},
]

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Nutri-Aahar API"}

@api_router.get("/products")
async def get_products(category: Optional[str] = None):
    if category and category != "All":
        if category in ("Dates", "Dry Fruits"):
            return [p for p in PRODUCTS if p["category"] == "Dates & Dry Fruits"]
        return [p for p in PRODUCTS if p["category"] == category]
    return PRODUCTS

@api_router.post("/enquiries", response_model=EnquiryResponse)
async def create_enquiry(input: EnquiryCreate):
    enquiry = input.model_dump()
    enquiry["id"] = str(uuid.uuid4())
    enquiry["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.enquiries.insert_one(enquiry.copy())
    return EnquiryResponse(**enquiry)

@api_router.get("/enquiries", response_model=List[EnquiryResponse])
async def get_enquiries():
    docs = await db.enquiries.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return docs

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()