from datetime import datetime

class OrderManager:
    """Manages order operations including creation, tracking, and updates."""
    
    def __init__(self, db):
        """Initialize with database connection."""
        self.db = db
    
    def get_all_orders(self):
        """Get all orders."""
        return self.db.get_collection("orders")
    
    def get_order_by_id(self, order_id):
        """Get order by ID."""
        return self.db.find_one("orders", {"id": order_id})
    
    def get_orders_by_status(self, status):
        """Get orders by status."""
        return self.db.find("orders", {"status": status})
    
    def create_order(self, customer_id, items, shipping_address):
        """
        Create a new order.
        
        Args:
            customer_id (str): Customer ID
            items (list): List of items with product_id and quantity
            shipping_address (str): Shipping address
            
        Returns:
            dict: Created order or None if failed
        """
        # Generate order ID
        order_count = len(self.get_all_orders())
        order_id = f"ORD-{12350 + order_count}"
        
        # Calculate total amount
        total_amount = 0
        order_items = []
        
        for item in items:
            product = self.db.find_one("products", {"id": item["product_id"]})
            if not product:
                return None
            
            # Check inventory
            inventory = self.db.find_one("inventory", {"product_id": item["product_id"]})
            if not inventory or inventory["quantity"] < item["quantity"]:
                return None
            
            # Update inventory
            self.db.update_one(
                "inventory",
                {"product_id": item["product_id"]},
                {"$set": {"quantity": inventory["quantity"] - item["quantity"]}}
            )
            
            # Add to order items
            item_total = product["price"] * item["quantity"]
            order_items.append({
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "price": product["price"]
            })
            
            total_amount += item_total
        
        # Create order
        order = {
            "id": order_id,
            "customer_id": customer_id,
            "order_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "Processing",
            "estimated_delivery": (datetime.now().replace(day=datetime.now().day + 7)).strftime("%Y-%m-%d"),
            "items": order_items,
            "shipping_address": shipping_address,
            "total_amount": total_amount
        }
        
        # Insert order
        self.db.insert_one("orders", order)
        
        # Update customer order history
        customer = self.db.find_one("customers", {"id": customer_id})
        if customer:
            if "order_history" not in customer:
                customer["order_history"] = []
            
            customer["order_history"].append(order_id)
            
            self.db.update_one(
                "customers",
                {"id": customer_id},
                {"$set": {"order_history": customer["order_history"]}}
            )
        
        return order
    
    def update_order_status(self, order_id, status, additional_info=None):
        """
        Update order status.
        
        Args:
            order_id (str): Order ID
            status (str): New status
            additional_info (dict, optional): Additional information
            
        Returns:
            bool: Success or failure
        """
        order = self.get_order_by_id(order_id)
        if not order:
            return False
        
        update_data = {"status": status}
        
        if status == "Delivered":
            update_data["delivery_date"] = datetime.now().strftime("%Y-%m-%d")
        
        if additional_info:
            for key, value in additional_info.items():
                update_data[key] = value
        
        result = self.db.update_one(
            "orders",
            {"id": order_id},
            {"$set": update_data}
        )
        
        return result["modified_count"] > 0
    
    def cancel_order(self, order_id, reason):
        """
        Cancel an order and return items to inventory.
        
        Args:
            order_id (str): Order ID
            reason (str): Cancellation reason
            
        Returns:
            bool: Success or failure
        """
        order = self.get_order_by_id(order_id)
        if not order or order["status"] == "Delivered":
            return False
        
        # Return items to inventory
        for item in order["items"]:
            inventory = self.db.find_one("inventory", {"product_id": item["product_id"]})
            if inventory:
                self.db.update_one(
                    "inventory",
                    {"product_id": item["product_id"]},
                    {"$set": {"quantity": inventory["quantity"] + item["quantity"]}}
                )
        
        # Update order status
        result = self.db.update_one(
            "orders",
            {"id": order_id},
            {"$set": {"status": "Cancelled", "cancellation_reason": reason}}
        )
        
        return result["modified_count"] > 0
    
    def get_order_tracking(self, order_id):
        """
        Get tracking information for an order.
        
        Args:
            order_id (str): Order ID
            
        Returns:
            dict: Tracking information or None if not found
        """
        order = self.get_order_by_id(order_id)
        if not order:
            return None
        
        # Mock tracking events based on order status
        tracking_events = []
        
        # Order placed event
        tracking_events.append({
            "date": order["order_date"],
            "time": "10:30 AM",
            "event": "Order Placed",
            "location": "Online"
        })
        
        # Order processed event
        if order["status"] != "Cancelled":
            process_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
            process_date = process_date.replace(day=process_date.day + 1)
            
            tracking_events.append({
                "date": process_date.strftime("%Y-%m-%d"),
                "time": "09:15 AM",
                "event": "Order Processed",
                "location": "Warehouse, Chicago"
            })
        
        # Shipped event
        if order["status"] in ["Shipped", "In Transit", "Out for Delivery", "Delivered"]:
            ship_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
            ship_date = ship_date.replace(day=ship_date.day + 2)
            
            tracking_events.append({
                "date": ship_date.strftime("%Y-%m-%d"),
                "time": "02:45 PM",
                "event": "Shipped",
                "location": "Warehouse, Chicago"
            })
        
        # In Transit event
        if order["status"] in ["In Transit", "Out for Delivery", "Delivered"]:
            transit_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
            transit_date = transit_date.replace(day=transit_date.day + 4)
            
            tracking_events.append({
                "date": transit_date.strftime("%Y-%m-%d"),
                "time": "11:20 AM",
                "event": "In Transit",
                "location": "Distribution Center, Atlanta"
            })
        
        # Out for Delivery event
        if order["status"] in ["Out for Delivery", "Delivered"]:
            delivery_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
            delivery_date = delivery_date.replace(day=delivery_date.day + 6)
            
            tracking_events.append({
                "date": delivery_date.strftime("%Y-%m-%d"),
                "time": "08:30 AM",
                "event": "Out for Delivery",
                "location": "Local Delivery Center"
            })
        
        # Delivered event
        if order["status"] == "Delivered":
            delivered_date = order.get("delivery_date", datetime.strptime(order["order_date"], "%Y-%m-%d").replace(day=datetime.strptime(order["order_date"], "%Y-%m-%d").day + 6).strftime("%Y-%m-%d"))
            
            tracking_events.append({
                "date": delivered_date,
                "time": "03:45 PM",
                "event": "Delivered",
                "location": order["shipping_address"]
            })
        
        # Cancelled event
        if order["status"] == "Cancelled":
            cancel_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
            cancel_date = cancel_date.replace(day=cancel_date.day + 1)
            
            tracking_events.append({
                "date": cancel_date.strftime("%Y-%m-%d"),
                "time": "11:30 AM",
                "event": "Cancelled",
                "location": "Online",
                "reason": order.get("cancellation_reason", "No reason provided")
            })
        
        return {
            "order_id": order_id,
            "status": order["status"],
            "estimated_delivery": order["estimated_delivery"],
            "current_location": self._get_current_location(order["status"]),
            "tracking_events": tracking_events
        }
    
    def _get_current_location(self, status):
        """Get current location based on order status."""
        if status == "Processing":
            return "Warehouse, Chicago"
        elif status == "Shipped":
            return "Warehouse, Chicago"
        elif status == "In Transit":
            return "Distribution Center, Atlanta"
        elif status == "Out for Delivery":
            return "Local Delivery Center"
        elif status == "Delivered":
            return "Delivered to recipient"
        elif status == "Cancelled":
            return "Order Cancelled"
        else:
            return "Unknown"