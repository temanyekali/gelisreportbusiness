"""
Script untuk membuat sample pekerjaan teknisi
Run: python3 /app/scripts/create_teknisi_jobs.py
"""
import sys
sys.path.append('/app/backend')

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
from datetime import datetime, timezone, timedelta
import random

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def create_teknisi_jobs():
    """Create sample technician jobs"""
    print("\n" + "="*70)
    print("🔧 CREATING TEKNISI JOBS")
    print("="*70)
    
    # Get teknisi user ID
    indra = await db.users.find_one({'username': 'indra'}, {'_id': 0})
    if not indra:
        print("❌ User 'indra' not found!")
        return
    
    teknisi_user_id = indra['id']
    print(f"\n✅ Found teknisi user: {indra['full_name']} (ID: {teknisi_user_id})")
    
    # Get PLN Installation business
    pln_business = await db.businesses.find_one({'name': 'Unit PLN Installation'}, {'_id': 0})
    if not pln_business:
        print("❌ PLN Installation business not found!")
        return
    
    business_id = pln_business['id']
    print(f"✅ Found business: {pln_business['name']} (ID: {business_id})")
    
    # Sample technical jobs
    job_types = [
        {'type': 'installation', 'name': 'Instalasi Listrik Baru', 'price': 2500000},
        {'type': 'maintenance', 'name': 'Maintenance Berkala', 'price': 500000},
        {'type': 'repair', 'name': 'Perbaikan Meteran', 'price': 750000},
        {'type': 'upgrade', 'name': 'Upgrade Daya', 'price': 3000000},
    ]
    
    statuses = ['pending', 'processing', 'completed']
    
    jobs_created = 0
    
    for i in range(8):  # Create 8 jobs
        job_type = random.choice(job_types)
        status = random.choice(statuses)
        
        # Create order date in the past week
        days_ago = random.randint(0, 7)
        order_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        job_data = {
            'id': f'job-{i+1:03d}-{teknisi_user_id[:8]}',
            'business_id': business_id,
            'order_number': f'ORD-PLN-{order_date.strftime("%Y%m%d")}-{i+1:04d}',
            'service_type': job_type['type'],
            'customer_name': f'Customer {i+1}',
            'customer_phone': f'08123456{i:04d}',
            'customer_address': f'Jl. Contoh No. {i+1}, Jakarta',
            'order_type': job_type['type'],
            'description': f"{job_type['name']} - {i+1}",
            'total_amount': job_type['price'],
            'payment_status': 'paid' if status == 'completed' else 'partial',
            'status': status,
            'requires_technician': True,
            'assigned_to': teknisi_user_id,
            'created_by': teknisi_user_id,
            'created_at': order_date.isoformat(),
            'updated_at': order_date.isoformat(),
            'notes': f'Technical job {i+1} for testing'
        }
        
        # Check if job already exists
        existing = await db.orders.find_one({'id': job_data['id']})
        if existing:
            print(f"  ⚠️ Job {job_data['id']} already exists, skipping...")
            continue
        
        await db.orders.insert_one(job_data)
        jobs_created += 1
        print(f"  ✅ Created: {job_data['description']} | Status: {status}")
        
        # Create technical progress for processing/completed jobs
        if status in ['processing', 'completed']:
            progress_data = {
                'id': f'progress-{job_data["id"]}',
                'order_id': job_data['id'],
                'business_id': business_id,
                'technician_id': teknisi_user_id,
                'steps': [
                    {
                        'step_name': 'Survey Lokasi',
                        'description': 'Melakukan survey lokasi instalasi',
                        'status': 'completed',
                        'step_weight': 20,
                        'completed_at': order_date.isoformat(),
                        'notes': 'Survey completed'
                    },
                    {
                        'step_name': 'Persiapan Material',
                        'description': 'Menyiapkan material yang dibutuhkan',
                        'status': 'completed' if status == 'completed' else 'in_progress',
                        'step_weight': 30,
                        'completed_at': order_date.isoformat() if status == 'completed' else None,
                        'notes': 'Material ready' if status == 'completed' else 'In progress'
                    },
                    {
                        'step_name': 'Instalasi',
                        'description': 'Melakukan instalasi',
                        'status': 'completed' if status == 'completed' else 'pending',
                        'step_weight': 40,
                        'completed_at': order_date.isoformat() if status == 'completed' else None,
                        'notes': 'Installation done' if status == 'completed' else None
                    },
                    {
                        'step_name': 'Testing',
                        'description': 'Testing dan quality check',
                        'status': 'completed' if status == 'completed' else 'pending',
                        'step_weight': 10,
                        'completed_at': order_date.isoformat() if status == 'completed' else None,
                        'notes': 'All tests passed' if status == 'completed' else None
                    }
                ],
                'created_at': order_date.isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            existing_progress = await db.technical_progress.find_one({'order_id': job_data['id']})
            if not existing_progress:
                await db.technical_progress.insert_one(progress_data)
                print(f"    ✅ Created progress tracking for {job_data['description']}")
    
    print(f"\n📊 Summary:")
    print(f"  Total jobs created: {jobs_created}")
    print(f"  Assigned to: {indra['full_name']} ({teknisi_user_id})")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(create_teknisi_jobs())
