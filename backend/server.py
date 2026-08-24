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
ASSET = "https://customer-assets-7cd3h4nn.emergentagent.net/job_premium-spice-export-9/artifacts"

PRODUCTS = [
    {"slug":"cumin-seeds","name":"Cumin Seeds","local":"Jeera","category":"Whole Spices","image":f"{ASSET}/3zzq420i_image.png","description":"Warm, earthy cumin seeds for authentic Indian kitchens and food businesses.","uses":"Tempering, spice blends, breads and pickles","benefits":"Promotes digestion, rich source of iron, may support blood cholesterol and weight management","nutrition":"Per 100g: 375 kcal, 17.8g protein, 44.2g carbs, 10.5g fibre, 66.4mg iron"},
    {"slug":"green-cardamom","name":"Green Cardamom","local":"Hari Elaichi","category":"Whole Spices","image":"https://static.prod-images.emergentagent.com/jobs/392b914b-998d-4c74-a5fa-c2ebde2fab14/images/53a7697529d20e2a621c696aa759058f3aa445f0ecbd11215b07778abdf86ea9.jpeg","description":"Aromatic green cardamom with a bright, naturally sweet fragrance.","uses":"Chai, desserts, rice dishes and masalas","benefits":"Has antibacterial properties; may support blood sugar, oral, heart and liver health"},
    {"slug":"black-cardamom","name":"Black Cardamom","local":"Badi Elaichi","category":"Whole Spices","image":IMG(39150949),"description":"Smoky, robust black cardamom pods for slow-cooked Indian classics.","uses":"Biryani, curries, garam masala and stews","benefits":"May help lower blood pressure, ease respiratory discomfort and nourish skin and hair","nutrition":"Contains 1.95–3.32% essential oils that aid digestion"},
    {"slug":"cloves","name":"Cloves","local":"Laung","category":"Whole Spices","image":"https://static.prod-images.emergentagent.com/jobs/392b914b-998d-4c74-a5fa-c2ebde2fab14/images/34d42b9d0324b2eac96d4da101f32b746181c9c7bc0857565272722f88aec66e.jpeg","description":"Intensely aromatic whole cloves with a warm, sweet depth.","uses":"Biryani, chai, masalas and baking","benefits":"High in antioxidants, antibacterial, supports liver and bone health, natural pain relief","nutrition":"Per tsp (2g): 6 kcal, 1g carbs, 1g fibre, 55% DV manganese"},
    {"slug":"cinnamon-cassia","name":"Cinnamon / Cassia","local":"Dalchini","category":"Whole Spices","image":f"{ASSET}/e16kt0dt_image.png","description":"Fragrant cinnamon bark for sweet and savoury Indian recipes.","uses":"Biryani, chai, baking and spice blends","benefits":"Supports healthy blood sugar regulation; antioxidant and anti-inflammatory compounds","nutrition":"Per 100g: 317 kcal, 56g carbs, 24.4g fibre, 3.9g protein"},
    {"slug":"black-pepper","name":"Black Peppercorns","local":"Kali Mirch","category":"Whole Spices","image":f"{ASSET}/dc42dn4q_image.png","description":"Bold, warming peppercorns that bring depth to every preparation.","uses":"Seasoning, marinades, curries and sauces","benefits":"Aids digestion and weight management; potassium helps regulate heart rate and blood pressure","nutrition":"Per tbsp: 17 kcal, 4.4g carbs, 1.8g fibre, 91.7mg potassium"},
    {"slug":"nutmeg","name":"Nutmeg","local":"Jaiphal","category":"Whole Spices","image":IMG(35339664),"description":"Warm, sweetly spiced whole nutmeg for festive and everyday cooking.","uses":"Desserts, biryani, beverages and baking","benefits":"Traditionally used to sharpen memory, ease pain and support skin, hair and blood pressure","nutrition":"Rich in potassium, copper, manganese, calcium, zinc, iron and magnesium"},
    {"slug":"mace","name":"Mace","local":"Javitri","category":"Whole Spices","image":f"{ASSET}/gc850mbm_image.png","description":"Delicate, fragrant mace prized in royal Indian cuisine.","uses":"Biryani, korma, desserts and spice blends"},
    {"slug":"star-anise","name":"Star Anise","local":"Chakra Phool","category":"Whole Spices","image":f"{ASSET}/uxf3ki3p_image.png","description":"A star-shaped, dark brown pod with a delicately sweet, aromatic liquorice-like flavour.","uses":"Biryani, garam masala, teas, broths and desserts","benefits":"May relieve muscle spasms, ease cough and act as an antimicrobial and anti-inflammatory","nutrition":"Seeds contain natural compounds with potential antibacterial effects"},
    {"slug":"mustard-seeds","name":"Mustard Seeds","local":"Rai / Sarson","category":"Whole Spices","image":IMG(5409832),"description":"Pungent mustard seeds that crackle into nutty warmth in hot oil.","uses":"Tempering, pickles, curries and chutneys"},
    {"slug":"coriander-seeds","name":"Coriander Seeds","local":"Sabut Dhaniya","category":"Whole Spices","image":"https://static.prod-images.emergentagent.com/jobs/392b914b-998d-4c74-a5fa-c2ebde2fab14/images/6d141ba2bd24498e50b6159f4b14bfdea5027a894dcebeb58c934496830f650c.jpeg","description":"Citrusy coriander seeds at home in classic masalas and contemporary blends.","uses":"Ground masala, pickles, curries and roasting","benefits":"A widely loved flavouring agent that supports digestion and overall wellness"},
    {"slug":"fennel-seeds","name":"Fennel Seeds","local":"Saunf","category":"Whole Spices","image":"https://static.prod-images.emergentagent.com/jobs/392b914b-998d-4c74-a5fa-c2ebde2fab14/images/d596cb5e9c892ad5a1a5dd677ebbeca290c6c0f410fe2f62057175825adc2288.jpeg","description":"Delicately sweet fennel seeds with a clean, refreshing finish.","uses":"Mukhwas, breads, teas and spice blends","benefits":"Aids digestion and soothes the stomach; used in foods, drinks, medicines and perfumery","nutrition":"Rich source of minerals such as magnesium and potassium"},
    {"slug":"fenugreek-seeds","name":"Fenugreek Seeds","local":"Methi Dana","category":"Whole Spices","image":IMG(5987968),"description":"Golden fenugreek seeds with a distinctive bittersweet character.","uses":"Curries, pickles, tempering and sprouting","benefits":"Used in spice blends and traditional wellness; kasoori methi leaves are a prominent Indian leafy-green"},
    {"slug":"turmeric-powder","name":"Turmeric Powder","local":"Haldi","category":"Spice Powders","image":IMG(6104651),"description":"Vibrant golden turmeric powder, a cornerstone of Indian kitchens.","uses":"Curries, dals, rice and golden milk","benefits":"Curcumin-rich; valued as a pain reliever, anti-inflammatory and antioxidant that supports immunity","nutrition":"Free-flowing powder from Indian-origin turmeric; curcumin-rich Salem and Lakda Don types"},
    {"slug":"red-chilli-powder","name":"Red Chilli Powder","local":"Lal Mirch","category":"Spice Powders","image":IMG(33440710),"description":"Bright, fiery red chilli powder ground from sun-dried chillies.","uses":"Curries, marinades, chutneys and seasoning","benefits":"Aids digestion, supports heart health and metabolism; adds heat and colour to dishes","nutrition":"Per 100g: ~400 kcal; contains protein, iron, calcium and dietary fibre; 0g trans fat"},
    {"slug":"coriander-powder","name":"Coriander Powder","local":"Dhaniya Powder","category":"Spice Powders","image":IMG(7263626),"description":"Freshly ground coriander powder with a citrusy, mellow warmth.","uses":"Curries, dals, sabzis and masala bases"},
    {"slug":"raw-makhana","name":"Raw White Makhana (Bulk)","local":"Phool Makhana","category":"Makhana","image":f"{ASSET}/vx0el5rn_makhana%20BRB.WHITE.jpg","description":"Premium raw white makhana (fox nuts) sourced from the fertile wetlands of Bihar — graded, cleaned and packed for bulk and wholesale supply.","uses":"Roasting, flavoured snacks, kheer, curries and food processing","benefits":"Heart health, no preservatives, vegan, gluten-free — a nutrient powerhouse","nutrition":"Rich in plant protein, fibre, magnesium, calcium and potassium; low in calories and fat","form":"Raw whole fox nuts — bulk supply"},
    {"slug":"roasted-pink-salt-makhana","name":"Roasted Pink Salt Makhana","local":"Makhana","category":"Makhana","image":f"{ASSET}/oi8mhi20_2.png","description":"The pure delight of premium makhana roasted to golden perfection and finished with pink salt — a timeless, savoury classic.","uses":"Standalone snacking, lunchboxes, pairing with beverages","benefits":"Heart health, no preservatives, vegan, gluten-free — a nutrient powerhouse","nutrition":"Rich in protein, fibre and essential minerals","shelf_life":"Up to a year when stored in an air-tight container in a dry place","form":"Roasted, ready to eat; can be roasted in ghee, butter or without added fats"},
    {"slug":"roasted-black-salt-makhana","name":"Roasted Black Salt Makhana","local":"Makhana","category":"Makhana","image":f"{ASSET}/8f8nqxzf_5.png","description":"Crunchy roasted makhana seasoned with earthy Indian black salt (kala namak) for a bold, tangy twist on a wholesome snack.","uses":"Standalone snacking, chaat toppings, pairing with beverages","benefits":"Heart health, no preservatives, vegan, gluten-free — a nutrient powerhouse","nutrition":"Rich in protein, fibre and essential minerals","shelf_life":"Up to a year when stored in an air-tight container in a dry place","form":"Roasted, ready to eat; can be roasted in ghee, butter or without added fats"},
    {"slug":"roasted-pepper-makhana","name":"Roasted Pepper Makhana","local":"Makhana","category":"Makhana","image":f"{ASSET}/il0hy1m7_1.png","description":"Premium Bihar makhana roasted light and crispy, generously seasoned with freshly ground, organically grown black pepper and spices.","uses":"Savoury snacking, salads, soups and party platters","benefits":"Heart health, no preservatives, vegan, gluten-free — a nutrient powerhouse","nutrition":"Rich in protein, fibre and essential minerals","shelf_life":"Up to a year when stored in an air-tight container in a dry place","form":"Roasted, ready to eat; can be roasted in ghee, butter or without added fats"},
    {"slug":"roasted-chilli-tomato-makhana","name":"Roasted Chilli Tomato Makhana","local":"Makhana","category":"Makhana","image":f"{ASSET}/xupwqkkh_3.png","description":"A spicy tango of bold chilli heat and the savoury tang of ripe tomatoes coating expertly roasted makhana.","uses":"Spicy snacking, salads, dips and party platters","benefits":"Heart health, no preservatives, vegan, gluten-free — a nutrient powerhouse","nutrition":"Rich in protein, fibre and essential minerals","shelf_life":"Up to a year when stored in an air-tight container in a dry place","form":"Roasted, ready to eat; can be roasted in ghee, butter or without added fats"},
    {"slug":"roasted-cheese-makhana","name":"Roasted Cheese Makhana","local":"Makhana","category":"Makhana","image":f"{ASSET}/v0ejcf0y_4.png","description":"A crunchy symphony of indulgence — golden roasted makhana coated in rich, savoury cheese for guilt-free snacking bliss.","uses":"Movie nights, lunchboxes, salads, soups and desserts","benefits":"Heart health, no preservatives, vegan option, gluten-free — a nutrient powerhouse","nutrition":"Rich in protein, fibre and essential minerals","shelf_life":"Up to a year when stored in an air-tight container in a dry place","form":"Roasted, ready to eat; can be roasted in ghee, butter or without added fats"},
    {"slug":"dates","name":"Dates","local":"Khajoor","category":"Dates & Dry Fruits","image":"https://customer-assets-7cd3h4nn.emergentagent.net/job_premium-spice-export-9/artifacts/b5r828ja_image.png","description":"Naturally rich dates for everyday nourishment and food innovation.","uses":"Snacking, desserts, energy bites and baking","benefits":"Quick natural energy, high fibre and antioxidant-rich; supports digestion and bone health","nutrition":"Contains potassium, magnesium, copper, manganese, iron and vitamin B6"},
    {"slug":"almonds","name":"Almonds","local":"Badam","category":"Dates & Dry Fruits","image":IMG(4397851),"description":"Premium whole almonds for everyday nourishment and festive cooking.","uses":"Snacking, desserts, milk and gifting","benefits":"Nutritious and versatile with delicate taste; a favourite of health-conscious consumers","form":"Whole natural, blanched, roasted & salted, sliced"},
    {"slug":"cashews","name":"Cashews","local":"Kaju","category":"Dates & Dry Fruits","image":IMG(34424388),"description":"Creamy whole cashews, perfect for rich gravies and sweet treats.","uses":"Curries, sweets, snacking and gifting","benefits":"Rich, creamy taste packed with essential nutrients; India is among the largest producers","form":"Whole (W240 / W320 / W450 grades), split, roasted & salted"},
    {"slug":"raisins","name":"Raisins","local":"Kishmish","category":"Dates & Dry Fruits","image":IMG(32567875),"description":"Naturally sweet raisins for snacking, baking and festive dishes.","uses":"Snacking, kheer, pulao and baking","benefits":"Natural energy source, high in fibre and antioxidants; rich in iron, potassium, calcium and B vitamins"},
    {"slug":"sesame-seeds","name":"Sesame Seeds","local":"Til","category":"Seeds & Specialty","image":IMG(3338502),"description":"Nutty sesame seeds at home in sweets, chutneys and tempering.","uses":"Til ladoo, chutneys, tempering and baking","benefits":"May help lower cholesterol and fight infections; among the richest plant sources of calcium","nutrition":"Per 100g: 18g protein, 12g fibre, 1450mg calcium, 9.3mg iron"},
    {"slug":"pumpkin-seeds","name":"Pumpkin Seeds","local":"Pumpkin Seeds","category":"Seeds & Specialty","image":IMG(38571531),"description":"Wholesome pumpkin seeds for mindful snacking and modern kitchens.","uses":"Snacking, salads, granola and baking"},
    {"slug":"sunflower-seeds","name":"Sunflower Seeds","local":"Sunflower Seeds","category":"Seeds & Specialty","image":IMG(36943553),"description":"Light, nutty sunflower seeds for everyday snacking and mixes.","uses":"Snacking, salads, trail mixes and baking","benefits":"Immunity booster with cholesterol-reducing, cardioprotective effects; rich in vitamin E","nutrition":"Per 100g: 584 kcal, 20.8g protein, 8.6g fibre, 35.1mg vitamin E"},
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