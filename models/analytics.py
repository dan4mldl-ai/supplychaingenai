import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AnalyticsManager:
    """Manages analytics operations for supply chain data."""
    
    def __init__(self, db):
        """Initialize with database connection."""
        self.db = db
    
    def get_sales_by_period(self, period="monthly", start_date=None, end_date=None):
        """
        Get sales data by period.
        
        Args:
            period (str): Period type (daily, weekly, monthly, quarterly)
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            dict: Sales data by period
        """
        # Get all orders
        orders = self.db.get_collection("orders")
        
        # Filter by date if provided
        if start_date:
            orders = [order for order in orders if order["order_date"] >= start_date]
        
        if end_date:
            orders = [order for order in orders if order["order_date"] <= end_date]
        
        # Convert to DataFrame
        df = pd.DataFrame(orders)
        
        # If no orders, return empty data
        if df.empty:
            return {"labels": [], "values": []}
        
        # Convert order_date to datetime
        df["order_date"] = pd.to_datetime(df["order_date"])
        
        # Group by period
        if period == "daily":
            df["period"] = df["order_date"].dt.strftime("%Y-%m-%d")
        elif period == "weekly":
            df["period"] = df["order_date"].dt.strftime("%Y-W%U")
        elif period == "monthly":
            df["period"] = df["order_date"].dt.strftime("%Y-%m")
        elif period == "quarterly":
            df["period"] = df["order_date"].dt.to_period("Q").astype(str)
        else:
            df["period"] = df["order_date"].dt.strftime("%Y-%m")
        
        # Group by period and sum total_amount
        sales_by_period = df.groupby("period")["total_amount"].sum().reset_index()
        
        # Sort by period
        sales_by_period = sales_by_period.sort_values("period")
        
        return {
            "labels": sales_by_period["period"].tolist(),
            "values": sales_by_period["total_amount"].tolist()
        }
    
    def get_top_selling_products(self, limit=10, start_date=None, end_date=None):
        """
        Get top selling products.
        
        Args:
            limit (int, optional): Number of products to return
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            list: Top selling products
        """
        # Get all orders
        orders = self.db.get_collection("orders")
        
        # Filter by date if provided
        if start_date:
            orders = [order for order in orders if order["order_date"] >= start_date]
        
        if end_date:
            orders = [order for order in orders if order["order_date"] <= end_date]
        
        # Extract items from orders
        items = []
        for order in orders:
            for item in order["items"]:
                items.append(item)
        
        # Convert to DataFrame
        df = pd.DataFrame(items)
        
        # If no items, return empty list
        if df.empty:
            return []
        
        # Group by product_id and sum quantity
        product_sales = df.groupby("product_id")["quantity"].sum().reset_index()
        
        # Sort by quantity in descending order
        product_sales = product_sales.sort_values("quantity", ascending=False)
        
        # Limit to top N products
        product_sales = product_sales.head(limit)
        
        # Get product details
        top_products = []
        for _, row in product_sales.iterrows():
            product = self.db.find_one("products", {"id": row["product_id"]})
            if product:
                top_products.append({
                    "id": product["id"],
                    "name": product["name"],
                    "quantity_sold": int(row["quantity"]),
                    "category": product["category"]
                })
        
        return top_products
    
    def get_inventory_value_by_category(self):
        """
        Get inventory value by category.
        
        Returns:
            dict: Inventory value by category
        """
        # Get all products
        products = self.db.get_collection("products")
        
        # Get all inventory
        inventory = self.db.get_collection("inventory")
        
        # Create product lookup dictionary
        product_dict = {product["id"]: product for product in products}
        
        # Calculate inventory value by category
        category_values = {}
        
        for item in inventory:
            product_id = item["product_id"]
            quantity = item["quantity"]
            
            if product_id in product_dict:
                product = product_dict[product_id]
                category = product["category"]
                value = product["price"] * quantity
                
                if category in category_values:
                    category_values[category] += value
                else:
                    category_values[category] = value
        
        # Convert to lists for charts
        categories = list(category_values.keys())
        values = list(category_values.values())
        
        return {
            "labels": categories,
            "values": values
        }
    
    def get_order_status_distribution(self):
        """
        Get order status distribution.
        
        Returns:
            dict: Order status distribution
        """
        # Get all orders
        orders = self.db.get_collection("orders")
        
        # Count orders by status
        status_counts = {}
        
        for order in orders:
            status = order["status"]
            
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts[status] = 1
        
        # Convert to lists for charts
        statuses = list(status_counts.keys())
        counts = list(status_counts.values())
        
        return {
            "labels": statuses,
            "values": counts
        }
    
    def get_inventory_turnover_rate(self, period="monthly"):
        """
        Calculate inventory turnover rate.
        
        Args:
            period (str): Period type (monthly, quarterly, yearly)
            
        Returns:
            dict: Inventory turnover rate by period
        """
        # Mock data for inventory turnover rate
        today = datetime.now()
        
        if period == "monthly":
            # Last 6 months
            periods = [(today - timedelta(days=30 * i)).strftime("%Y-%m") for i in range(6, 0, -1)]
            values = [round(np.random.uniform(2.0, 4.0), 2) for _ in range(6)]
        elif period == "quarterly":
            # Last 4 quarters
            current_quarter = (today.month - 1) // 3 + 1
            current_year = today.year
            
            periods = []
            for i in range(4, 0, -1):
                q = current_quarter - i % 4
                y = current_year - (1 if q <= 0 else 0)
                q = q + 4 if q <= 0 else q
                periods.append(f"{y}-Q{q}")
            
            values = [round(np.random.uniform(2.0, 4.0), 2) for _ in range(4)]
        else:  # yearly
            # Last 3 years
            periods = [(today - timedelta(days=365 * i)).strftime("%Y") for i in range(3, 0, -1)]
            values = [round(np.random.uniform(2.0, 4.0), 2) for _ in range(3)]
        
        return {
            "labels": periods,
            "values": values
        }
    
    def get_supplier_performance(self):
        """
        Get supplier performance metrics.
        
        Returns:
            list: Supplier performance data
        """
        # Get all suppliers
        suppliers = self.db.get_collection("suppliers")
        
        # Mock performance data
        performance_data = []
        
        for supplier in suppliers:
            performance_data.append({
                "id": supplier["id"],
                "name": supplier["name"],
                "on_time_delivery_rate": round(np.random.uniform(0.8, 0.99), 2),
                "quality_rating": round(np.random.uniform(3.0, 5.0), 1),
                "response_time": round(np.random.uniform(1.0, 5.0), 1),
                "lead_time": round(np.random.uniform(2.0, 14.0), 1)
            })
        
        return performance_data