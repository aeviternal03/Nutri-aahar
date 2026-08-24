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

IMG = lambda i: f"https://images.pexels.com/photos/{i}/pexels-photo-{i}.jpeg?auto=compress&cs=tinysrgb&w=900"

PRODUCTS = [
    {"slug":"cumin-seeds","name":"Cumin Seeds","local":"Jeera","category":"Whole Spices","image":IMG(18778270),"description":"Warm, earthy cumin seeds for authentic Indian kitchens and food businesses.","uses":"Tempering, spice blends, breads and pickles"},
    {"slug":"green-cardamom","name":"Green Cardamom","local":"Hari Elaichi","category":"Whole Spices","image":IMG(4110333),"description":"Aromatic green cardamom with a bright, naturally sweet fragrance.","uses":"Chai, desserts, rice dishes and masalas"},
    {"slug":"black-cardamom","name":"Black Cardamom","local":"Badi Elaichi","category":"Whole Spices","image":IMG(39150949),"description":"Smoky, robust black cardamom pods for slow-cooked Indian classics.","uses":"Biryani, curries, garam masala and stews"},
    {"slug":"cloves","name":"Cloves","local":"Laung","category":"Whole Spices","image":IMG(8804297),"description":"Intensely aromatic whole cloves with a warm, sweet depth.","uses":"Biryani, chai, masalas and baking"},
    {"slug":"cinnamon-cassia","name":"Cinnamon / Cassia","local":"Dalchini","category":"Whole Spices","image":IMG(4198714),"description":"Fragrant cinnamon bark for sweet and savoury Indian recipes.","uses":"Biryani, chai, baking and spice blends"},
    {"slug":"black-pepper","name":"Black Peppercorns","local":"Kali Mirch","category":"Whole Spices","image":IMG(4198019),"description":"Bold, warming peppercorns that bring depth to every preparation.","uses":"Seasoning, marinades, curries and sauces"},
    {"slug":"nutmeg","name":"Nutmeg","local":"Jaiphal","category":"Whole Spices","image":IMG(35339664),"description":"Warm, sweetly spiced whole nutmeg for festive and everyday cooking.","uses":"Desserts, biryani, beverages and baking"},
    {"slug":"mace","name":"Mace","local":"Javitri","category":"Whole Spices","image":IMG(36745315),"description":"Delicate, fragrant mace prized in royal Indian cuisine.","uses":"Biryani, korma, desserts and spice blends"},
    {"slug":"black-cumin","name":"Black Cumin","local":"Shah Jeera","category":"Whole Spices","image":IMG(35156986),"description":"Earthy, gently sweet black cumin seeds loved in Mughlai cooking.","uses":"Biryani, naan, curries and tempering"},
    {"slug":"mustard-seeds","name":"Mustard Seeds","local":"Rai / Sarson","category":"Whole Spices","image":IMG(5409832),"description":"Pungent mustard seeds that crackle into nutty warmth in hot oil.","uses":"Tempering, pickles, curries and chutneys"},
    {"slug":"coriander-seeds","name":"Coriander Seeds","local":"Sabut Dhaniya","category":"Whole Spices","image":IMG(4198843),"description":"Citrusy coriander seeds at home in classic masalas and contemporary blends.","uses":"Ground masala, pickles, curries and roasting"},
    {"slug":"fennel-seeds","name":"Fennel Seeds","local":"Saunf","category":"Whole Spices","image":IMG(4110254),"description":"Delicately sweet fennel seeds with a clean, refreshing finish.","uses":"Mukhwas, breads, teas and spice blends"},
    {"slug":"fenugreek-seeds","name":"Fenugreek Seeds","local":"Methi Dana","category":"Whole Spices","image":IMG(5987968),"description":"Golden fenugreek seeds with a distinctive bittersweet character.","uses":"Curries, pickles, tempering and sprouting"},
    {"slug":"carom-seeds","name":"Carom Seeds","local":"Ajwain","category":"Whole Spices","image":IMG(10817550),"description":"Bold, thyme-like carom seeds with a sharp aromatic bite.","uses":"Parathas, pakoras, dals and digestive teas"},
    {"slug":"nigella-seeds","name":"Nigella Seeds","local":"Kalonji","category":"Whole Spices","image":IMG(5738744),"description":"Peppery nigella seeds that add a gentle crunch and depth.","uses":"Naan, pickles, curries and tempering"},
    {"slug":"poppy-seeds","name":"Poppy Seeds","local":"Khuskhus","category":"Whole Spices","image":IMG(3682193),"description":"Mild, nutty poppy seeds for rich gravies and traditional sweets.","uses":"Korma, halwa, curries and baking"},
    {"slug":"turmeric-powder","name":"Turmeric Powder","local":"Haldi","category":"Spice Powders","image":IMG(6104651),"description":"Vibrant golden turmeric powder, a cornerstone of Indian kitchens.","uses":"Curries, dals, rice and golden milk"},
    {"slug":"red-chilli-powder","name":"Red Chilli Powder","local":"Lal Mirch","category":"Spice Powders","image":IMG(33440710),"description":"Bright, fiery red chilli powder ground from sun-dried chillies.","uses":"Curries, marinades, chutneys and seasoning"},
    {"slug":"coriander-powder","name":"Coriander Powder","local":"Dhaniya Powder","category":"Spice Powders","image":IMG(7263626),"description":"Freshly ground coriander powder with a citrusy, mellow warmth.","uses":"Curries, dals, sabzis and masala bases"},
    {"slug":"makhana","name":"Makhana / Foxnuts","local":"Makhana","category":"Makhana","image":IMG(4198929),"description":"A versatile Indian ingredient for mindful snacking and modern recipes.","uses":"Roasting, snacking, curries and desserts"},
    {"slug":"dates","name":"Dates","local":"Khajoor","category":"Dates & Dry Fruits","image":IMG(752505),"description":"Naturally rich dates for everyday nourishment and food innovation.","uses":"Snacking, desserts, energy bites and baking"},
    {"slug":"almonds","name":"Almonds","local":"Badam","category":"Dates & Dry Fruits","image":IMG(4397851),"description":"Premium whole almonds for everyday nourishment and festive cooking.","uses":"Snacking, desserts, milk and gifting"},
    {"slug":"cashews","name":"Cashews","local":"Kaju","category":"Dates & Dry Fruits","image":IMG(34424388),"description":"Creamy whole cashews, perfect for rich gravies and sweet treats.","uses":"Curries, sweets, snacking and gifting"},
    {"slug":"raisins","name":"Raisins","local":"Kishmish","category":"Dates & Dry Fruits","image":IMG(32567875),"description":"Naturally sweet raisins for snacking, baking and festive dishes.","uses":"Snacking, kheer, pulao and baking"},
    {"slug":"sesame-seeds","name":"Sesame Seeds","local":"Til","category":"Seeds & Specialty","image":IMG(3338502),"description":"Nutty sesame seeds at home in sweets, chutneys and tempering.","uses":"Til ladoo, chutneys, tempering and baking"},
    {"slug":"pumpkin-seeds","name":"Pumpkin Seeds","local":"Pumpkin Seeds","category":"Seeds & Specialty","image":IMG(38571531),"description":"Wholesome pumpkin seeds for mindful snacking and modern kitchens.","uses":"Snacking, salads, granola and baking"},
    {"slug":"sunflower-seeds","name":"Sunflower Seeds","local":"Sunflower Seeds","category":"Seeds & Specialty","image":IMG(36943553),"description":"Light, nutty sunflower seeds for everyday snacking and mixes.","uses":"Snacking, salads, trail mixes and baking"},
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