import numpy as np

class InventoryManager:
    """Manages inventory operations including ABC analysis, JIT, EOQ, FIFO, and Safety Stock."""
    
    def __init__(self, db):
        """Initialize with database connection."""
        self.db = db
    
    def get_all_inventory(self):
        """Get all inventory items."""
        return self.db.get_collection("inventory")
    
    def get_inventory_by_product(self, product_id):
        """Get inventory for a specific product."""
        return self.db.find_one("inventory", {"product_id": product_id})
    
    def update_inventory(self, product_id, quantity_change):
        """Update inventory quantity."""
        inventory = self.get_inventory_by_product(product_id)
        if inventory:
            new_quantity = inventory["quantity"] + quantity_change
            self.db.update_one(
                "inventory",
                {"product_id": product_id},
                {"$set": {"quantity": new_quantity}}
            )
            return True
        return False
    
    def get_low_stock_items(self):
        """Get items with stock below reorder point."""
        inventory = self.get_all_inventory()
        return [item for item in inventory if item["quantity"] <= item["reorder_point"]]
    
    def get_out_of_stock_items(self):
        """Get items with zero stock."""
        inventory = self.get_all_inventory()
        return [item for item in inventory if item["quantity"] == 0]
    
    def perform_abc_analysis(self):
        """
        Perform ABC analysis on inventory.
        
        Returns:
            dict: Dictionary with A, B, and C category items
        """
        inventory = self.get_all_inventory()
        products = self.db.get_collection("products")
        
        # Calculate value for each inventory item
        inventory_values = []
        for inv_item in inventory:
            product = next((p for p in products if p["id"] == inv_item["product_id"]), None)
            if product:
                value = inv_item["quantity"] * product["price"]
                inventory_values.append({
                    "product_id": inv_item["product_id"],
                    "value": value,
                    "quantity": inv_item["quantity"]
                })
        
        # Sort by value in descending order
        inventory_values.sort(key=lambda x: x["value"], reverse=True)
        
        # Calculate cumulative percentage
        total_value = sum(item["value"] for item in inventory_values)
        cumulative_value = 0
        
        a_items = []
        b_items = []
        c_items = []
        
        for item in inventory_values:
            cumulative_value += item["value"]
            cumulative_percentage = (cumulative_value / total_value) * 100
            
            if cumulative_percentage <= 80:
                a_items.append(item["product_id"])
                self.db.update_one(
                    "inventory",
                    {"product_id": item["product_id"]},
                    {"$set": {"abc_category": "A"}}
                )
            elif cumulative_percentage <= 95:
                b_items.append(item["product_id"])
                self.db.update_one(
                    "inventory",
                    {"product_id": item["product_id"]},
                    {"$set": {"abc_category": "B"}}
                )
            else:
                c_items.append(item["product_id"])
                self.db.update_one(
                    "inventory",
                    {"product_id": item["product_id"]},
                    {"$set": {"abc_category": "C"}}
                )
        
        return {
            "A": a_items,
            "B": b_items,
            "C": c_items
        }
    
    def calculate_eoq(self, product_id, annual_demand, order_cost, holding_cost):
        """
        Calculate Economic Order Quantity.
        
        Args:
            product_id (str): Product ID
            annual_demand (float): Annual demand quantity
            order_cost (float): Cost per order
            holding_cost (float): Annual holding cost per unit
            
        Returns:
            dict: EOQ results
        """
        eoq = round(np.sqrt((2 * annual_demand * order_cost) / holding_cost))
        optimal_orders = round(annual_demand / eoq)
        total_order_cost = optimal_orders * order_cost
        total_holding_cost = (eoq / 2) * holding_cost
        total_cost = total_order_cost + total_holding_cost
        
        return {
            "product_id": product_id,
            "eoq": eoq,
            "optimal_orders": optimal_orders,
            "total_order_cost": total_order_cost,
            "total_holding_cost": total_holding_cost,
            "total_cost": total_cost
        }
    
    def calculate_safety_stock(self, product_id, avg_daily_demand, std_dev_demand, avg_lead_time, std_dev_lead_time, service_level=95):
        """
        Calculate safety stock level.
        
        Args:
            product_id (str): Product ID
            avg_daily_demand (float): Average daily demand
            std_dev_demand (float): Standard deviation of daily demand
            avg_lead_time (float): Average lead time in days
            std_dev_lead_time (float): Standard deviation of lead time
            service_level (int): Service level percentage (default: 95)
            
        Returns:
            dict: Safety stock results
        """
        # Service level Z-score mapping
        z_scores = {
            80: 0.84,
            85: 1.04,
            90: 1.28,
            95: 1.65,
            96: 1.75,
            97: 1.88,
            98: 2.05,
            99: 2.33
        }
        
        # Get closest z-score
        z_score = z_scores.get(service_level, 1.65)
        
        # Calculate safety stock
        demand_during_lead_time = avg_daily_demand * avg_lead_time
        std_dev_during_lead_time = np.sqrt(
            (avg_lead_time * std_dev_demand**2) + 
            (avg_daily_demand**2 * std_dev_lead_time**2)
        )
        
        safety_stock = round(z_score * std_dev_during_lead_time)
        reorder_point = round(demand_during_lead_time + safety_stock)
        
        # Update inventory with new safety stock and reorder point
        self.db.update_one(
            "inventory",
            {"product_id": product_id},
            {"$set": {"safety_stock": safety_stock, "reorder_point": reorder_point}}
        )
        
        return {
            "product_id": product_id,
            "safety_stock": safety_stock,
            "reorder_point": reorder_point,
            "service_level": service_level
        }
    
    def get_jit_candidates(self):
        """
        Identify products suitable for Just-in-Time inventory management.
        
        Returns:
            list: List of products suitable for JIT
        """
        inventory = self.get_all_inventory()
        products = self.db.get_collection("products")
        
        jit_candidates = []
        
        for inv_item in inventory:
            product = next((p for p in products if p["id"] == inv_item["product_id"]), None)
            if product:
                # Mock criteria for JIT suitability
                # In a real system, this would use actual demand stability, lead time, etc.
                demand_stability = "High" if inv_item["product_id"] in ["P001", "P003", "P005"] else "Medium"
                lead_time = "2 days" if inv_item["product_id"] in ["P001", "P003"] else "3 days"
                supplier_reliability = "Excellent" if inv_item["product_id"] in ["P001", "P003"] else "Good"
                
                # Calculate JIT score (mock calculation)
                jit_score = 0
                if demand_stability == "High":
                    jit_score += 40
                elif demand_stability == "Medium":
                    jit_score += 30
                else:
                    jit_score += 10
                
                if lead_time == "1 day":
                    jit_score += 30
                elif lead_time == "2 days":
                    jit_score += 25
                elif lead_time == "3 days":
                    jit_score += 20
                else:
                    jit_score += 10
                
                if supplier_reliability == "Excellent":
                    jit_score += 30
                elif supplier_reliability == "Good":
                    jit_score += 25
                else:
                    jit_score += 15
                
                jit_candidates.append({
                    "product": product["name"],
                    "product_id": inv_item["product_id"],
                    "demand_stability": demand_stability,
                    "lead_time": lead_time,
                    "supplier_reliability": supplier_reliability,
                    "jit_score": jit_score
                })
        
        # Sort by JIT score in descending order
        jit_candidates.sort(key=lambda x: x["jit_score"], reverse=True)
        
        return jit_candidates