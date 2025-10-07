class ProductManager:
    """Manages product operations including creation, updates, and retrieval."""
    
    def __init__(self, db):
        """Initialize with database connection."""
        self.db = db
    
    def get_all_products(self):
        """Get all products."""
        return self.db.get_collection("products")
    
    def get_product_by_id(self, product_id):
        """Get product by ID."""
        return self.db.find_one("products", {"id": product_id})
    
    def get_products_by_category(self, category):
        """Get products by category."""
        return self.db.find("products", {"category": category})
    
    def get_products_by_supplier(self, supplier_id):
        """Get products by supplier ID."""
        return self.db.find("products", {"supplier_id": supplier_id})
    
    def create_product(self, name, description, price, category, supplier_id, image_url=None):
        """
        Create a new product.
        
        Args:
            name (str): Product name
            description (str): Product description
            price (float): Product price
            category (str): Product category
            supplier_id (str): Supplier ID
            image_url (str, optional): Product image URL
            
        Returns:
            dict: Created product or None if failed
        """
        # Generate product ID
        product_count = len(self.get_all_products())
        product_id = f"PRD-{10000 + product_count}"
        
        # Create product
        product = {
            "id": product_id,
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "supplier_id": supplier_id,
            "image_url": image_url or f"https://via.placeholder.com/150?text={name.replace(' ', '+')}"
        }
        
        # Insert product
        self.db.insert_one("products", product)
        
        # Create initial inventory entry
        self.db.insert_one("inventory", {
            "product_id": product_id,
            "quantity": 0,
            "reorder_level": 10,
            "reorder_quantity": 50,
            "last_restock_date": None
        })
        
        return product
    
    def update_product(self, product_id, update_data):
        """
        Update product information.
        
        Args:
            product_id (str): Product ID
            update_data (dict): Data to update
            
        Returns:
            bool: Success or failure
        """
        result = self.db.update_one(
            "products",
            {"id": product_id},
            {"$set": update_data}
        )
        
        return result["modified_count"] > 0
    
    def delete_product(self, product_id):
        """
        Delete a product.
        
        Args:
            product_id (str): Product ID
            
        Returns:
            bool: Success or failure
        """
        # Check if product exists
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        
        # Delete product
        self.db.delete_one("products", {"id": product_id})
        
        # Delete inventory entry
        self.db.delete_one("inventory", {"product_id": product_id})
        
        return True
    
    def get_product_categories(self):
        """Get all unique product categories."""
        products = self.get_all_products()
        categories = set()
        
        for product in products:
            categories.add(product["category"])
        
        return sorted(list(categories))
    
    def get_low_stock_products(self, threshold=10):
        """
        Get products with low stock.
        
        Args:
            threshold (int, optional): Low stock threshold
            
        Returns:
            list: Products with low stock
        """
        inventory_items = self.db.find("inventory", {"quantity": {"$lte": threshold}})
        low_stock_products = []
        
        for item in inventory_items:
            product = self.get_product_by_id(item["product_id"])
            if product:
                product["stock_quantity"] = item["quantity"]
                product["reorder_level"] = item["reorder_level"]
                low_stock_products.append(product)
        
        return low_stock_products