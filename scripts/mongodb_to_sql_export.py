#!/usr/bin/env python3
"""
MongoDB to SQL Export Script
Exports all MongoDB collections to SQL INSERT statements
Supports MySQL/MariaDB syntax
"""

import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']

# SQL table definitions
SQL_TABLES = {
    'roles': '''
CREATE TABLE IF NOT EXISTS `roles` (
  `id` INT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL,
  `description` TEXT,
  `permissions` JSON,
  `created_at` DATETIME NOT NULL,
  INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
''',
    'users': '''
CREATE TABLE IF NOT EXISTS `users` (
  `id` VARCHAR(36) PRIMARY KEY,
  `username` VARCHAR(50) UNIQUE NOT NULL,
  `email` VARCHAR(100) UNIQUE NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(20),
  `address` TEXT,
  `role_id` INT NOT NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `last_login` DATETIME,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  FOREIGN KEY (role_id) REFERENCES roles(id),
  INDEX idx_username (username),
  INDEX idx_email (email),
  INDEX idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
''',
    'businesses': '''
CREATE TABLE IF NOT EXISTS `businesses` (
  `id` VARCHAR(36) PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `category` VARCHAR(50) NOT NULL,
  `description` TEXT,
  `address` TEXT,
  `phone` VARCHAR(20),
  `email` VARCHAR(100),
  `settings` JSON,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_by` VARCHAR(36) NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  FOREIGN KEY (created_by) REFERENCES users(id),
  INDEX idx_category (category),
  INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
''',
    'orders': '''
CREATE TABLE IF NOT EXISTS `orders` (
  `id` VARCHAR(36) PRIMARY KEY,
  `order_number` VARCHAR(50) UNIQUE NOT NULL,
  `business_id` VARCHAR(36) NOT NULL,
  `customer_name` VARCHAR(100) NOT NULL,
  `customer_phone` VARCHAR(20),
  `customer_email` VARCHAR(100),
  `service_type` VARCHAR(50) NOT NULL,
  `order_details` JSON NOT NULL,
  `total_amount` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `paid_amount` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `status` ENUM('pending','processing','completed','cancelled') NOT NULL DEFAULT 'pending',
  `payment_status` ENUM('unpaid','partial','paid','refunded') NOT NULL DEFAULT 'unpaid',
  `payment_method` VARCHAR(50),
  `assigned_to` VARCHAR(36),
  `completion_date` DATETIME,
  `notes` TEXT,
  `created_by` VARCHAR(36) NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  FOREIGN KEY (business_id) REFERENCES businesses(id),
  FOREIGN KEY (created_by) REFERENCES users(id),
  FOREIGN KEY (assigned_to) REFERENCES users(id),
  INDEX idx_order_number (order_number),
  INDEX idx_business_id (business_id),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
''',
    'transactions': '''
CREATE TABLE IF NOT EXISTS `transactions` (
  `id` VARCHAR(36) PRIMARY KEY,
  `transaction_code` VARCHAR(50) UNIQUE NOT NULL,
  `order_id` VARCHAR(36),
  `business_id` VARCHAR(36) NOT NULL,
  `transaction_type` ENUM('income','expense','transfer','commission') NOT NULL,
  `category` VARCHAR(100) NOT NULL,
  `description` VARCHAR(255) NOT NULL,
  `amount` DECIMAL(15,2) NOT NULL,
  `payment_method` VARCHAR(50),
  `reference_number` VARCHAR(100),
  `created_by` VARCHAR(36) NOT NULL,
  `created_at` DATETIME NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
  FOREIGN KEY (business_id) REFERENCES businesses(id),
  FOREIGN KEY (created_by) REFERENCES users(id),
  INDEX idx_transaction_code (transaction_code),
  INDEX idx_transaction_type (transaction_type),
  INDEX idx_business_id (business_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
''',
    'notifications': '''
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` VARCHAR(36) PRIMARY KEY,
  `user_id` VARCHAR(36) NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `message` TEXT NOT NULL,
  `type` ENUM('info','warning','error','success') NOT NULL DEFAULT 'info',
  `is_read` TINYINT(1) NOT NULL DEFAULT 0,
  `related_id` VARCHAR(36),
  `related_type` VARCHAR(50),
  `action_url` VARCHAR(255),
  `created_at` DATETIME NOT NULL,
  INDEX idx_user_id (user_id),
  INDEX idx_is_read (is_read),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
''',
    'activity_logs': '''
CREATE TABLE IF NOT EXISTS `activity_logs` (
  `id` VARCHAR(36) PRIMARY KEY,
  `user_id` VARCHAR(36) NOT NULL,
  `action` VARCHAR(100) NOT NULL,
  `description` TEXT,
  `ip_address` VARCHAR(45),
  `user_agent` VARCHAR(255),
  `related_id` VARCHAR(36),
  `related_type` VARCHAR(50),
  `created_at` DATETIME NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_user_id (user_id),
  INDEX idx_action (action),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
'''
}

def escape_sql_string(value):
    """Escape string for SQL"""
    if value is None:
        return 'NULL'
    if isinstance(value, str):
        return "'" + value.replace("'", "''").replace('\\', '\\\\') + "'"
    if isinstance(value, bool):
        return '1' if value else '0'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        import json
        return "'" + json.dumps(value).replace("'", "''") + "'"
    return "'" + str(value) + "'"

async def export_collection(db, collection_name):
    """Export a MongoDB collection to SQL INSERT statements"""
    collection = db[collection_name]
    documents = await collection.find({}, {'_id': 0}).to_list(10000)
    
    if not documents:
        return []
    
    inserts = []
    for doc in documents:
        fields = []
        values = []
        
        for key, value in doc.items():
            fields.append(f'`{key}`')
            values.append(escape_sql_string(value))
        
        insert = f"INSERT INTO `{collection_name}` ({', '.join(fields)}) VALUES ({', '.join(values)});"
        inserts.append(insert)
    
    return inserts

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    output_file = '/app/scripts/gelis_export.sql'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"-- GELIS MongoDB to SQL Export\\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\\n")
        f.write(f"-- Database: {DB_NAME}\\n\\n")
        
        f.write("SET FOREIGN_KEY_CHECKS=0;\\n\\n")
        
        # Create tables
        f.write("-- =============================================\\n")
        f.write("-- CREATE TABLES\\n")
        f.write("-- =============================================\\n\\n")
        
        for table_name, create_sql in SQL_TABLES.items():
            f.write(f"-- Table: {table_name}\\n")
            f.write(f"DROP TABLE IF EXISTS `{table_name}`;\\n")
            f.write(create_sql)
            f.write("\\n\\n")
        
        # Insert data
        f.write("-- =============================================\\n")
        f.write("-- INSERT DATA\\n")
        f.write("-- =============================================\\n\\n")
        
        # Export in order of dependencies
        export_order = ['roles', 'users', 'businesses', 'orders', 'transactions', 'notifications', 'activity_logs']
        
        for collection_name in export_order:
            print(f"Exporting {collection_name}...")
            inserts = await export_collection(db, collection_name)
            
            if inserts:
                f.write(f"-- Data for table: {collection_name}\\n")
                for insert in inserts:
                    f.write(insert + "\\n")
                f.write("\\n")
            
            print(f"  Exported {len(inserts)} records from {collection_name}")
        
        f.write("SET FOREIGN_KEY_CHECKS=1;\\n")
    
    client.close()
    print(f"\\n✅ Export selesai! File: {output_file}")
    print(f"\\nUntuk import ke MySQL/MariaDB:")
    print(f"  mysql -u username -p database_name < {output_file}")

if __name__ == '__main__':
    asyncio.run(main())
