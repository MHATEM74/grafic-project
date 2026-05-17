# characters/character_data.py

# Rarity colors (will be used in the shop)
RARITY = {
    "Common": (50, 200, 80),    # GREEN
    "Rare": (50, 100, 220),     # BLUE
    "Epic": (150, 50, 220),     # PURPLE
    "Legendary": (255, 200, 0)  # GOLD
}

CHARACTERS = [
    {"id":0,"name":"Alex",   "gender":"Male",   "color":(70,130,220),  "cost":0,   "owned":True,  "accent":(200,220,255), "rarity": "Common"},
    {"id":1,"name":"Mia",    "gender":"Female", "color":(230,80,160),  "cost":0,   "owned":True,  "accent":(255,180,220), "rarity": "Common"},
    {"id":2,"name":"Shadow", "gender":"Male",   "color":(90,30,130),   "cost":200, "owned":False, "accent":(180,100,255), "rarity": "Rare"},
    {"id":3,"name":"Blaze",  "gender":"Female", "color":(220,60,20),   "cost":200, "owned":False, "accent":(255,180,80), "rarity": "Rare"},
    {"id":4,"name":"Phantom","gender":"Male",   "color":(200,200,220), "cost":350, "owned":False, "accent":(255,255,255), "rarity": "Rare"},
    {"id":5,"name":"Aurora", "gender":"Female", "color":(30,180,160),  "cost":350, "owned":False, "accent":(255,210,80), "rarity": "Rare"},
    {"id":6,"name":"Titan",  "gender":"Male",   "color":(100,60,30),   "cost":500, "owned":False, "accent":(200,150,80), "rarity": "Epic"},
    {"id":7,"name":"Seraph", "gender":"Female", "color":(240,230,200), "cost":500, "owned":False, "accent":(255,255,180), "rarity": "Epic"},
    {"id":8,"name":"Void",   "gender":"Male",   "color":(10,10,20),    "cost":750, "owned":False, "accent":(0,255,100), "rarity": "Legendary"},
    {"id":9,"name":"Nova",   "gender":"Female", "color":(80,20,130),   "cost":750, "owned":False, "accent":(200,150,255), "rarity": "Legendary"},
]
