import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from pathlib import Path
from auth import hash_password
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def seed_database():
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🌱 Seeding database...")
    
    # Clear existing data
    await db.users.delete_many({})
    await db.subscriptions.delete_many({})
    await db.data_sources.delete_many({})
    print("✓ Cleared existing data")
    
    # Create sample users
    users_data = [
        {"name": "John Doe", "email": "john@example.com", "plan": "Business Pro"},
        {"name": "Jane Smith", "email": "jane@example.com", "plan": "Business Essential"},
        {"name": "Mike Johnson", "email": "mike@example.com", "plan": "Hobby"},
        {"name": "Sarah Williams", "email": "sarah@example.com", "plan": "Business Pro"},
        {"name": "Tom Brown", "email": "tom@example.com", "plan": "Business Essential"},
        {"name": "Emily Davis", "email": "emily@example.com", "plan": "Business Essential"},
        {"name": "David Wilson", "email": "david@example.com", "plan": "Hobby"},
        {"name": "Lisa Anderson", "email": "lisa@example.com", "plan": "Ultra"},
        {"name": "James Martinez", "email": "james@example.com", "plan": "Business Pro"},
        {"name": "Maria Garcia", "email": "maria@example.com", "plan": "Business Essential"},
    ]
    
    user_ids = []
    for i, user_data in enumerate(users_data):
        # Create user over last 7 months
        days_ago = 210 - (i * 20)  # Spread over ~7 months
        created_at = datetime.utcnow() - timedelta(days=days_ago)
        
        user_doc = {
            "name": user_data["name"],
            "email": user_data["email"],
            "password": hash_password("password123"),
            "plan": user_data["plan"],
            "status": "active" if i < 8 else "inactive",
            "credits": 100 + (i * 50),
            "role": "user",
            "created_at": created_at,
            "updated_at": created_at
        }
        result = await db.users.insert_one(user_doc)
        user_ids.append(result.inserted_id)
    
    print(f"✓ Created {len(user_ids)} users")
    
    # Create subscriptions
    plan_prices = {
        "Hobby": 19,
        "Business Essential": 50,
        "Business Pro": 299,
        "Ultra": 999
    }
    
    subscription_count = 0
    for i, user_id in enumerate(user_ids):
        plan = users_data[i]["plan"]
        days_ago = 210 - (i * 20)
        created_at = datetime.utcnow() - timedelta(days=days_ago)
        
        subscription_doc = {
            "user_id": user_id,
            "plan": plan,
            "status": "active" if i < 8 else "cancelled",
            "amount": plan_prices[plan],
            "start_date": created_at,
            "end_date": created_at + timedelta(days=30),
            "created_at": created_at
        }
        await db.subscriptions.insert_one(subscription_doc)
        subscription_count += 1
    
    print(f"✓ Created {subscription_count} subscriptions")
    
    # Create data sources
    data_source_types = [
        "PostgreSQL", "MySQL", "MongoDB", "Supabase", 
        "Google Sheets", "Excel", "CSV", "Stripe",
        "Shopify", "QuickBooks", "Google Analytics", "HubSpot"
    ]
    
    data_source_count = 0
    for user_id in user_ids[:8]:  # Only for active users
        # Each user has 2-4 data sources
        num_sources = random.randint(2, 4)
        selected_types = random.sample(data_source_types, num_sources)
        
        for ds_type in selected_types:
            days_ago = random.randint(10, 180)
            created_at = datetime.utcnow() - timedelta(days=days_ago)
            
            ds_doc = {
                "user_id": user_id,
                "name": f"{ds_type} - Production",
                "type": ds_type,
                "status": "connected",
                "created_at": created_at
            }
            await db.data_sources.insert_one(ds_doc)
            data_source_count += 1
    
    print(f"✓ Created {data_source_count} data sources")
    
    # Create admin user
    admin_doc = {
        "name": "Admin User",
        "email": "admin@papermap.com",
        "password": hash_password("admin123"),
        "plan": "Ultra",
        "status": "active",
        "credits": 10000,
        "role": "admin",
        "created_at": datetime.utcnow() - timedelta(days=365),
        "updated_at": datetime.utcnow()
    }
    await db.users.insert_one(admin_doc)
    print("✓ Created admin user (admin@papermap.com / admin123)")
    
    print("\n✅ Database seeded successfully!")
    print(f"   - Users: {len(user_ids) + 1}")
    print(f"   - Subscriptions: {subscription_count}")
    print(f"   - Data Sources: {data_source_count}")
    print("\n🔐 Login credentials:")
    print("   Email: admin@papermap.com")
    print("   Password: admin123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
