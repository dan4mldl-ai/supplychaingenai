import os
import pymongo
from dotenv import load_dotenv

class DatabaseHandler:
    """
    Handles database connections and operations for the supply chain management system.
    Uses MongoDB for document storage.
    """
    
    def __init__(self):
        """Initialize database connection."""
        load_dotenv()
        
        # For demonstration purposes, we'll use a mock connection
        # In production, you would use actual MongoDB connection
        self.client = None
        self.db = None
        
        # Initialize mock data
        self.initialize_mock_data()
    
    def connect(self):
        """
        Connect to MongoDB database.
        In a real application, this would use environment variables for connection details.
        """
        try:
            # MongoDB connection string would be stored in environment variables
            # connection_string = os.getenv("MONGODB_URI")
            # self.client = pymongo.MongoClient(connection_string)
            # self.db = self.client.get_database("supply_chain_db")
            pass
        except Exception as e:
            print(f"Error connecting to database: {e}")
    
    def initialize_mock_data(self):
        """Initialize mock data for demonstration purposes."""
        # Mock collections
        self.collections = {
            "products": [],
            "inventory": [],
            "orders": [],
            "suppliers": [],
            "customers": []
        }
        
        # Add sample products
        self.collections["products"] = [
            {"id": "P001", "name": "Smartphone X", "category": "Electronics", "price": 699.99, "description": "Latest smartphone with advanced features"},
            {"id": "P002", "name": "Laptop Pro", "category": "Electronics", "price": 1299.99, "description": "High-performance laptop for professionals"},
            {"id": "P003", "name": "Wireless Earbuds", "category": "Electronics", "price": 129.99, "description": "Premium wireless earbuds with noise cancellation"},
            {"id": "P004", "name": "Cotton T-Shirt", "category": "Clothing", "price": 19.99, "description": "Comfortable cotton t-shirt in various colors"},
            {"id": "P005", "name": "Denim Jeans", "category": "Clothing", "price": 49.99, "description": "Classic denim jeans with modern fit"},
            {"id": "P006", "name": "Coffee Maker", "category": "Home Goods", "price": 89.99, "description": "Programmable coffee maker with thermal carafe"},
            {"id": "P007", "name": "Blender", "category": "Home Goods", "price": 69.99, "description": "High-speed blender for smoothies and more"},
            {"id": "P008", "name": "Organic Coffee", "category": "Food & Beverage", "price": 12.99, "description": "Organic, fair-trade coffee beans"},
            {"id": "P009", "name": "Notebook Set", "category": "Office Supplies", "price": 15.99, "description": "Set of 3 premium notebooks"},
            {"id": "P010", "name": "Desk Lamp", "category": "Home Goods", "price": 34.99, "description": "Adjustable LED desk lamp with multiple brightness levels"}
        ]
        
        # Add sample inventory
        self.collections["inventory"] = [
            {"product_id": "P001", "quantity": 45, "location": "Warehouse A", "reorder_point": 20, "safety_stock": 15, "abc_category": "A"},
            {"product_id": "P002", "quantity": 20, "location": "Warehouse A", "reorder_point": 10, "safety_stock": 5, "abc_category": "A"},
            {"product_id": "P003", "quantity": 8, "location": "Warehouse B", "reorder_point": 15, "safety_stock": 10, "abc_category": "B"},
            {"product_id": "P004", "quantity": 150, "location": "Warehouse C", "reorder_point": 50, "safety_stock": 30, "abc_category": "C"},
            {"product_id": "P005", "quantity": 75, "location": "Warehouse C", "reorder_point": 30, "safety_stock": 20, "abc_category": "B"},
            {"product_id": "P006", "quantity": 0, "location": "Warehouse B", "reorder_point": 10, "safety_stock": 5, "abc_category": "B"},
            {"product_id": "P007", "quantity": 12, "location": "Warehouse B", "reorder_point": 8, "safety_stock": 5, "abc_category": "B"},
            {"product_id": "P008", "quantity": 30, "location": "Warehouse D", "reorder_point": 20, "safety_stock": 10, "abc_category": "C"},
            {"product_id": "P009", "quantity": 5, "location": "Warehouse D", "reorder_point": 15, "safety_stock": 10, "abc_category": "C"},
            {"product_id": "P010", "quantity": 18, "location": "Warehouse B", "reorder_point": 12, "safety_stock": 8, "abc_category": "B"}
        ]
        
        # Add sample orders
        self.collections["orders"] = [
            {
                "id": "ORD-12345",
                "customer_id": "C001",
                "order_date": "2023-07-10",
                "status": "In Transit",
                "estimated_delivery": "2023-07-17",
                "items": [
                    {"product_id": "P001", "quantity": 2, "price": 699.99},
                    {"product_id": "P003", "quantity": 1, "price": 129.99}
                ],
                "shipping_address": "123 Main St, Anytown, USA",
                "total_amount": 1529.97
            },
            {
                "id": "ORD-12346",
                "customer_id": "C002",
                "order_date": "2023-07-12",
                "status": "Processing",
                "estimated_delivery": "2023-07-19",
                "items": [
                    {"product_id": "P002", "quantity": 1, "price": 1299.99},
                    {"product_id": "P010", "quantity": 2, "price": 34.99}
                ],
                "shipping_address": "456 Oak Ave, Somewhere, USA",
                "total_amount": 1369.97
            },
            {
                "id": "ORD-12347",
                "customer_id": "C003",
                "order_date": "2023-07-08",
                "status": "Delivered",
                "estimated_delivery": "2023-07-15",
                "delivery_date": "2023-07-14",
                "items": [
                    {"product_id": "P004", "quantity": 3, "price": 19.99},
                    {"product_id": "P005", "quantity": 1, "price": 49.99}
                ],
                "shipping_address": "789 Pine Rd, Elsewhere, USA",
                "total_amount": 109.96
            }
        ]
        
        # Add sample suppliers
        self.collections["suppliers"] = [
            {
                "id": "S001",
                "name": "ABC Electronics",
                "contact_person": "John Smith",
                "email": "john@abcelectronics.com",
                "phone": "555-123-4567",
                "address": "100 Supplier Blvd, Tech City, USA",
                "products": ["P001", "P002", "P003"],
                "performance": {
                    "on_time_delivery": 99.5,
                    "quality": 98.7,
                    "response_time": 4.8
                }
            },
            {
                "id": "S002",
                "name": "Fashion Fabrics",
                "contact_person": "Jane Doe",
                "email": "jane@fashionfabrics.com",
                "phone": "555-987-6543",
                "address": "200 Textile Ave, Fabric Town, USA",
                "products": ["P004", "P005"],
                "performance": {
                    "on_time_delivery": 95.2,
                    "quality": 97.5,
                    "response_time": 4.2
                }
            },
            {
                "id": "S003",
                "name": "Home Essentials",
                "contact_person": "Robert Johnson",
                "email": "robert@homeessentials.com",
                "phone": "555-456-7890",
                "address": "300 Homewares St, Comfort City, USA",
                "products": ["P006", "P007", "P010"],
                "performance": {
                    "on_time_delivery": 92.8,
                    "quality": 96.3,
                    "response_time": 3.9
                }
            }
        ]
        
        # Add sample customers
        self.collections["customers"] = [
            {
                "id": "C001",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "555-111-2222",
                "address": "123 Main St, Anytown, USA",
                "order_history": ["ORD-12345"]
            },
            {
                "id": "C002",
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "phone": "555-333-4444",
                "address": "456 Oak Ave, Somewhere, USA",
                "order_history": ["ORD-12346"]
            },
            {
                "id": "C003",
                "name": "Robert Johnson",
                "email": "robert.johnson@example.com",
                "phone": "555-555-6666",
                "address": "789 Pine Rd, Elsewhere, USA",
                "order_history": ["ORD-12347"]
            }
        ]
    
    def get_collection(self, collection_name):
        """Get a collection by name."""
        if collection_name in self.collections:
            return self.collections[collection_name]
        return []
    
    def find_one(self, collection_name, query):
        """Find a single document in a collection."""
        collection = self.get_collection(collection_name)
        for item in collection:
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                return item
        return None
    
    def find(self, collection_name, query=None):
        """Find documents in a collection."""
        collection = self.get_collection(collection_name)
        if query is None:
            return collection
        
        results = []
        for item in collection:
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                results.append(item)
        return results
    
    def insert_one(self, collection_name, document):
        """Insert a document into a collection."""
        if collection_name in self.collections:
            self.collections[collection_name].append(document)
            return {"inserted_id": document.get("id")}
        return None
    
    def update_one(self, collection_name, query, update):
        """Update a document in a collection."""
        if collection_name not in self.collections:
            return None
        
        for i, item in enumerate(self.collections[collection_name]):
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            
            if match:
                # Apply updates
                for key, value in update.items():
                    if key == "$set":
                        for update_key, update_value in value.items():
                            item[update_key] = update_value
                
                self.collections[collection_name][i] = item
                return {"modified_count": 1}
        
        return {"modified_count": 0}
    
    def delete_one(self, collection_name, query):
        """Delete a document from a collection."""
        if collection_name not in self.collections:
            return None
        
        for i, item in enumerate(self.collections[collection_name]):
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            
            if match:
                del self.collections[collection_name][i]
                return {"deleted_count": 1}
        
        return {"deleted_count": 0}