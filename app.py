import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# Import custom modules
from database.db_handler import DatabaseHandler
from rag.document_processor import DocumentProcessor
from rag.query_engine import QueryEngine
from models.inventory import InventoryManager
from models.order import OrderManager
from models.product import ProductManager

from rag.rag_handler import RAGHandler

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Supply Chain Management System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Database connection
db = DatabaseHandler()

# Initialize managers
inventory_manager = InventoryManager(db)
order_manager = OrderManager(db)
product_manager = ProductManager(db)

# Initialize RAG components
document_processor = DocumentProcessor()
query_engine = QueryEngine()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #e3f2fd;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1565C0;
    }
    .metric-label {
        font-size: 1rem;
        color: #424242;
    }
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .bot-message {
        background-color: #f1f1f1;
        margin-right: 20%;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
def sidebar():
    with st.sidebar:
        st.image("assets/logo.svg", width=200)
        st.title("Navigation")
        
        # Navigation options
        pages = {
            "Home": "🏠",
            "Order Management": "📦",
            "Inventory Management": "🧮",
            "Products": "🛒",
            "Analytics": "📊",
            "Supply Chain Assistant": "🤖",
            "Document Upload": "📄"
        }
        
        for page, icon in pages.items():
            if st.button(f"{icon} {page}"):
                st.session_state.current_page = page
                st.rerun()

# Page rendering functions
def home_page():
    st.markdown("<h1 class='main-header'>Supply Chain Management System</h1>", unsafe_allow_html=True)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>152</div>
            <div class='metric-label'>Active Orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>98.2%</div>
            <div class='metric-label'>On-Time Delivery</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>87%</div>
            <div class='metric-label'>Inventory Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>$1.2M</div>
            <div class='metric-label'>Monthly Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("<h2 class='sub-header'>Recent Activity</h2>", unsafe_allow_html=True)
    
    # Sample data for demonstration
    recent_activities = [
        {"timestamp": "2023-07-15 09:23", "activity": "Order #12345 shipped to customer", "status": "Completed"},
        {"timestamp": "2023-07-15 08:45", "activity": "Inventory restocked: SKU-789", "status": "Completed"},
        {"timestamp": "2023-07-14 17:30", "activity": "New order #12346 received", "status": "Processing"},
        {"timestamp": "2023-07-14 14:15", "activity": "Supplier delivery delayed", "status": "Alert"},
        {"timestamp": "2023-07-14 10:00", "activity": "ABC Analysis completed", "status": "Completed"}
    ]
    
    activity_df = pd.DataFrame(recent_activities)
    st.dataframe(activity_df, width='stretch')
    
    # Quick actions
    st.markdown("<h2 class='sub-header'>Quick Actions</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.subheader("Create New Order")
            st.button("New Order", key="new_order_home")
    
    with col2:
        with st.container(border=True):
            st.subheader("Check Inventory")
            st.button("View Inventory", key="view_inventory_home")
    
    with col3:
        with st.container(border=True):
            st.subheader("Ask Assistant")
            st.button("Open Assistant", key="open_assistant_home")

def order_management_page():
    st.markdown("<h1 class='main-header'>Order Management</h1>", unsafe_allow_html=True)
    
    # Tabs for different order functions
    tab1, tab2, tab3, tab4 = st.tabs(["Create Order", "Track Orders", "Update Orders", "Delivery Updates"])
    
    with tab1:
        st.subheader("Create New Order")
        
        # Order form
        with st.form("order_form"):
            customer_name = st.text_input("Customer Name")
            customer_email = st.text_input("Customer Email")
            
            # Product selection
            st.subheader("Select Products")
            
            # Sample product data
            products = [
                {"id": "P001", "name": "Product A", "price": 100, "available": 50},
                {"id": "P002", "name": "Product B", "price": 150, "available": 30},
                {"id": "P003", "name": "Product C", "price": 200, "available": 20},
                {"id": "P004", "name": "Product D", "price": 120, "available": 40},
                {"id": "P005", "name": "Product E", "price": 180, "available": 25}
            ]
            
            selected_products = {}
            for product in products:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{product['name']} - ${product['price']} (Available: {product['available']})")
                with col2:
                    quantity = st.number_input(f"Qty for {product['name']}", min_value=0, max_value=product['available'], step=1, key=f"qty_{product['id']}")
                    if quantity > 0:
                        selected_products[product['id']] = quantity
            
            shipping_address = st.text_area("Shipping Address")
            delivery_date = st.date_input("Expected Delivery Date")
            
            submitted = st.form_submit_button("Create Order")
            if submitted:
                if customer_name and customer_email and shipping_address and selected_products:
                    st.success("Order created successfully!")
                else:
                    st.error("Please fill all required fields and select at least one product.")
    
    with tab2:
        st.subheader("Track Orders")
        
        # Order tracking
        order_id = st.text_input("Enter Order ID")
        if st.button("Track Order"):
            if order_id:
                # Sample order data
                order_details = {
                    "order_id": order_id,
                    "customer": "John Doe",
                    "order_date": "2023-07-10",
                    "status": "In Transit",
                    "estimated_delivery": "2023-07-17",
                    "current_location": "Distribution Center, Atlanta",
                    "items": [
                        {"product": "Product A", "quantity": 2, "price": 200},
                        {"product": "Product C", "quantity": 1, "price": 200}
                    ]
                }
                
                st.write("### Order Details")
                col1, col2, col3 = st.columns(3)
                col1.metric("Order ID", order_details["order_id"])
                col2.metric("Status", order_details["status"])
                col3.metric("Est. Delivery", order_details["estimated_delivery"])
                
                st.write("### Tracking Information")
                st.info(f"Current Location: {order_details['current_location']}")
                
                # Tracking timeline
                tracking_events = [
                    {"date": "2023-07-10", "time": "10:30 AM", "event": "Order Placed", "location": "Online"},
                    {"date": "2023-07-11", "time": "09:15 AM", "event": "Order Processed", "location": "Warehouse, Chicago"},
                    {"date": "2023-07-12", "time": "02:45 PM", "event": "Shipped", "location": "Warehouse, Chicago"},
                    {"date": "2023-07-14", "time": "11:20 AM", "event": "In Transit", "location": "Distribution Center, Atlanta"}
                ]
                
                for event in tracking_events:
                    st.write(f"**{event['date']} {event['time']}** - {event['event']} ({event['location']})")
                
                st.write("### Order Items")
                items_df = pd.DataFrame(order_details["items"])
                st.dataframe(items_df)
            else:
                st.error("Please enter an Order ID")
    
    with tab3:
        st.subheader("Update Orders")
        
        # Order update form
        with st.form("update_order_form"):
            order_id = st.text_input("Order ID")
            update_type = st.selectbox("Update Type", ["Change Delivery Address", "Modify Order Items", "Cancel Order"])
            
            if update_type == "Change Delivery Address":
                new_address = st.text_area("New Delivery Address")
            elif update_type == "Modify Order Items":
                st.write("Select products to modify:")
                # Sample product data
                products = [
                    {"id": "P001", "name": "Product A", "price": 100, "current_qty": 2},
                    {"id": "P003", "name": "Product C", "price": 200, "current_qty": 1}
                ]
                
                for product in products:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"{product['name']} - ${product['price']} (Current Qty: {product['current_qty']})")
                    with col2:
                        st.number_input(f"New Qty for {product['name']}", min_value=0, value=product['current_qty'], step=1, key=f"update_qty_{product['id']}")
            elif update_type == "Cancel Order":
                cancellation_reason = st.text_area("Reason for Cancellation")
            
            submitted = st.form_submit_button("Update Order")
            if submitted:
                if order_id:
                    st.success("Order updated successfully!")
                else:
                    st.error("Please enter an Order ID")
    
    with tab4:
        st.subheader("Delivery Updates")
        
        # Sample delivery updates
        delivery_updates = [
            {"order_id": "ORD-12345", "customer": "John Doe", "status": "Out for Delivery", "estimated_delivery": "Today, 2:00 PM"},
            {"order_id": "ORD-12346", "customer": "Jane Smith", "status": "Delayed", "estimated_delivery": "Tomorrow, 10:00 AM"},
            {"order_id": "ORD-12347", "customer": "Robert Johnson", "status": "Delivered", "estimated_delivery": "Delivered on July 14, 3:45 PM"},
            {"order_id": "ORD-12348", "customer": "Emily Davis", "status": "In Transit", "estimated_delivery": "July 17, 12:00 PM"},
            {"order_id": "ORD-12349", "customer": "Michael Wilson", "status": "Processing", "estimated_delivery": "July 18, 2:00 PM"}
        ]
        
        delivery_df = pd.DataFrame(delivery_updates)
        st.dataframe(delivery_df, width='stretch')
        
        # Send delivery update
        st.write("### Send Delivery Update")
        with st.form("delivery_update_form"):
            order_id = st.text_input("Order ID")
            update_status = st.selectbox("New Status", ["Processing", "Shipped", "In Transit", "Out for Delivery", "Delivered", "Delayed", "Cancelled"])
            update_message = st.text_area("Additional Message")
            
            submitted = st.form_submit_button("Send Update")
            if submitted:
                if order_id:
                    st.success(f"Delivery update sent for Order {order_id}")
                else:
                    st.error("Please enter an Order ID")

def inventory_management_page():
    st.markdown("<h1 class='main-header'>Inventory Management</h1>", unsafe_allow_html=True)
    
    # Tabs for different inventory functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "ABC Analysis", "JIT Inventory", "EOQ Calculator", "Safety Stock"])
    
    with tab1:
        st.subheader("Inventory Overview")
        
        # Inventory metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total SKUs", "1,245")
        with col2:
            st.metric("In Stock", "987")
        with col3:
            st.metric("Low Stock", "152")
        with col4:
            st.metric("Out of Stock", "106")
        
        # Inventory by category
        st.subheader("Inventory by Category")
        
        # Sample data
        categories = ["Electronics", "Clothing", "Home Goods", "Food & Beverage", "Office Supplies"]
        inventory_counts = [450, 325, 275, 120, 75]
        
        fig = px.bar(
            x=categories,
            y=inventory_counts,
            labels={"x": "Category", "y": "Item Count"},
            color=inventory_counts,
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, width='stretch')
        
        # Recent inventory movements
        st.subheader("Recent Inventory Movements")
        
        # Sample data
        movements = [
            {"timestamp": "2023-07-15 09:30", "sku": "SKU-001", "product": "Product A", "type": "Inbound", "quantity": 50},
            {"timestamp": "2023-07-15 08:45", "sku": "SKU-002", "product": "Product B", "type": "Outbound", "quantity": 25},
            {"timestamp": "2023-07-14 16:20", "sku": "SKU-003", "product": "Product C", "type": "Inbound", "quantity": 100},
            {"timestamp": "2023-07-14 14:15", "sku": "SKU-004", "product": "Product D", "type": "Outbound", "quantity": 30},
            {"timestamp": "2023-07-14 10:00", "sku": "SKU-005", "product": "Product E", "type": "Adjustment", "quantity": -5}
        ]
        
        movements_df = pd.DataFrame(movements)
        st.dataframe(movements_df, width='stretch')
    
    with tab2:
        st.subheader("ABC Analysis")
        
        # ABC Analysis explanation
        st.write("""
        ABC Analysis categorizes inventory into three tiers based on their value and sales frequency:
        - **A items**: High-value items (70-80% of value, 10-20% of items)
        - **B items**: Medium-value items (15-25% of value, 30% of items)
        - **C items**: Low-value items (5% of value, 50-60% of items)
        """)
        
        # Sample ABC analysis data
        abc_data = {
            "A": {"items": 125, "value": 850000, "percentage": "75%"},
            "B": {"items": 350, "value": 230000, "percentage": "20%"},
            "C": {"items": 770, "value": 57000, "percentage": "5%"}
        }
        
        # ABC Analysis visualization
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=["A", "B", "C"],
            y=[abc_data["A"]["items"], abc_data["B"]["items"], abc_data["C"]["items"]],
            name="Number of Items",
            marker_color=["#1E88E5", "#42A5F5", "#90CAF9"]
        ))
        
        # Add value line
        fig.add_trace(go.Scatter(
            x=["A", "B", "C"],
            y=[abc_data["A"]["value"]/1000, abc_data["B"]["value"]/1000, abc_data["C"]["value"]/1000],
            name="Value (thousands $)",
            yaxis="y2",
            line=dict(color="#0D47A1", width=4)
        ))
        
        # Update layout
        fig.update_layout(
            title="ABC Analysis Overview",
            xaxis_title="Category",
            yaxis_title="Number of Items",
            yaxis2=dict(
                title="Value (thousands $)",
                overlaying="y",
                side="right"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # ABC Analysis details
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class='card'>
                <h3>A Items</h3>
                <p><strong>Count:</strong> {abc_data['A']['items']}</p>
                <p><strong>Value:</strong> ${abc_data['A']['value']:,}</p>
                <p><strong>% of Total Value:</strong> {abc_data['A']['percentage']}</p>
                <p><strong>Management:</strong> Tight control, accurate records, frequent review</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='card'>
                <h3>B Items</h3>
                <p><strong>Count:</strong> {abc_data['B']['items']}</p>
                <p><strong>Value:</strong> ${abc_data['B']['value']:,}</p>
                <p><strong>% of Total Value:</strong> {abc_data['B']['percentage']}</p>
                <p><strong>Management:</strong> Regular review, normal controls</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='card'>
                <h3>C Items</h3>
                <p><strong>Count:</strong> {abc_data['C']['items']}</p>
                <p><strong>Value:</strong> ${abc_data['C']['value']:,}</p>
                <p><strong>% of Total Value:</strong> {abc_data['C']['percentage']}</p>
                <p><strong>Management:</strong> Simplest controls, bulk ordering, safety stock</p>
            </div>
            """, unsafe_allow_html=True)

        # Live ABC analysis using inventory data
        st.markdown("### Live ABC Analysis")
        try:
            abc_result = inventory_manager.perform_abc_analysis()
            products = product_manager.get_all_products()
            inventory_items = inventory_manager.get_all_inventory()
            product_lookup = {p["id"]: p for p in products}
            inventory_lookup = {i["product_id"]: i for i in inventory_items}

            def compute_category_stats(ids):
                count = len(ids)
                total_value = 0.0
                for pid in ids:
                    prod = product_lookup.get(pid)
                    inv = inventory_lookup.get(pid)
                    if prod and inv:
                        total_value += float(prod["price"]) * float(inv["quantity"])
                return count, total_value

            a_count, a_value = compute_category_stats(abc_result.get("A", []))
            b_count, b_value = compute_category_stats(abc_result.get("B", []))
            c_count, c_value = compute_category_stats(abc_result.get("C", []))
            total_value = max(a_value + b_value + c_value, 1e-9)
            live_data = {
                "A": {"items": a_count, "value": a_value, "percentage": f"{(a_value/total_value)*100:.1f}%"},
                "B": {"items": b_count, "value": b_value, "percentage": f"{(b_value/total_value)*100:.1f}%"},
                "C": {"items": c_count, "value": c_value, "percentage": f"{(c_value/total_value)*100:.1f}%"}
            }

            fig_live = go.Figure()
            fig_live.add_trace(go.Bar(
                x=["A", "B", "C"],
                y=[live_data["A"]["items"], live_data["B"]["items"], live_data["C"]["items"]],
                name="Number of Items",
                marker_color=["#1E88E5", "#42A5F5", "#90CAF9"]
            ))
            fig_live.add_trace(go.Scatter(
                x=["A", "B", "C"],
                y=[live_data["A"]["value"], live_data["B"]["value"], live_data["C"]["value"]],
                name="Category Value ($)",
                yaxis="y2",
                line=dict(color="#0D47A1", width=4)
            ))
            fig_live.update_layout(
                title="Live ABC Analysis",
                xaxis_title="Category",
                yaxis_title="Number of Items",
                yaxis2=dict(title="Category Value ($)", overlaying="y", side="right"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_live, width='stretch')

            st.subheader("Items by ABC Category (Live)")
            for cat in ["A", "B", "C"]:
                ids = abc_result.get(cat, [])
                rows = []
                for pid in ids:
                    prod = product_lookup.get(pid)
                    inv = inventory_lookup.get(pid)
                    if prod and inv:
                        rows.append({
                            "Product ID": pid,
                            "Product": prod["name"],
                            "Quantity": inv["quantity"],
                            "Price": prod["price"],
                            "Value": float(prod["price"]) * float(inv["quantity"])
                        })
                st.markdown(f"#### Category {cat}")
                if rows:
                    st.dataframe(pd.DataFrame(rows), width='stretch')
                else:
                    st.info("No items in this category.")
        except Exception as e:
            st.error(f"Failed to perform live ABC analysis: {e}")
    
    with tab3:
        st.subheader("Just-in-Time (JIT) Inventory")
        
        # JIT explanation
        st.write("""
        Just-in-Time (JIT) inventory is a lean manufacturing approach that minimizes inventory by receiving goods and producing them only when needed, reducing holding costs and waste.
        """)
        
        # JIT performance metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Inventory Turnover", "12.5", "2.3")
        with col2:
            st.metric("Lead Time (days)", "3.2", "-0.8")
        with col3:
            st.metric("Holding Cost Reduction", "32%", "5%")
        
        # JIT implementation status
        st.subheader("JIT Implementation Status")
        
        # Sample data
        jit_status = {
            "Supplier Integration": 85,
            "Production Scheduling": 92,
            "Quality Control": 78,
            "Delivery Optimization": 65,
            "Staff Training": 90
        }
        
        fig = go.Figure()
        
        for category, value in jit_status.items():
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=value,
                title={"text": category},
                domain={"row": 0, "column": list(jit_status.keys()).index(category)},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#1E88E5"},
                    "steps": [
                        {"range": [0, 50], "color": "#FFCDD2"},
                        {"range": [50, 80], "color": "#FFECB3"},
                        {"range": [80, 100], "color": "#C8E6C9"}
                    ]
                }
            ))
        
        fig.update_layout(
            grid={"rows": 1, "columns": len(jit_status)},
            height=250
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # JIT product candidates
        st.subheader("Top JIT Product Candidates")
        try:
            jit_candidates = inventory_manager.get_jit_candidates()
            if jit_candidates:
                jit_df = pd.DataFrame(jit_candidates)
                st.dataframe(jit_df, width='stretch')
            else:
                st.info("No JIT candidates identified.")
        except Exception as e:
            st.error(f"Failed to load JIT candidates: {e}")
    
    with tab4:
        st.subheader("Economic Order Quantity (EOQ) Calculator")
        
        # EOQ explanation
        st.write("""
        Economic Order Quantity (EOQ) is a formula that helps determine the optimal quantity of inventory to order at one time to minimize costs related to ordering and holding inventory.
        
        The formula is: EOQ = √(2DS/H)
        
        Where:
        - D = Annual demand quantity
        - S = Order cost (per purchase order)
        - H = Annual holding cost per unit
        """)
        
        # EOQ calculator
        with st.form("eoq_calculator"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                annual_demand = st.number_input("Annual Demand (units)", min_value=1, value=1000)
            
            with col2:
                order_cost = st.number_input("Order Cost ($)", min_value=0.01, value=25.0)
            
            with col3:
                holding_cost = st.number_input("Annual Holding Cost per Unit ($)", min_value=0.01, value=5.0)
            
            calculate = st.form_submit_button("Calculate EOQ")
            
            if calculate:
                eoq = round(np.sqrt((2 * annual_demand * order_cost) / holding_cost))
                optimal_orders = round(annual_demand / eoq)
                total_order_cost = optimal_orders * order_cost
                total_holding_cost = (eoq / 2) * holding_cost
                total_cost = total_order_cost + total_holding_cost
                
                st.success(f"Economic Order Quantity (EOQ): {eoq} units")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Optimal Number of Orders", str(optimal_orders))
                
                with col2:
                    st.metric("Total Order Cost", f"${total_order_cost:.2f}")
                
                with col3:
                    st.metric("Total Holding Cost", f"${total_holding_cost:.2f}")
                
                st.info(f"Total Annual Inventory Cost: ${total_cost:.2f}")
                
                # EOQ visualization
                order_sizes = list(range(max(1, eoq - 100), eoq + 100, 10))
                order_costs = []
                holding_costs = []
                total_costs = []
                
                for size in order_sizes:
                    num_orders = annual_demand / size
                    order_cost_val = num_orders * order_cost
                    holding_cost_val = (size / 2) * holding_cost
                    total_cost_val = order_cost_val + holding_cost_val
                    
                    order_costs.append(order_cost_val)
                    holding_costs.append(holding_cost_val)
                    total_costs.append(total_cost_val)
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=order_sizes,
                    y=order_costs,
                    mode="lines",
                    name="Order Cost",
                    line=dict(color="#42A5F5", width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=order_sizes,
                    y=holding_costs,
                    mode="lines",
                    name="Holding Cost",
                    line=dict(color="#FF7043", width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=order_sizes,
                    y=total_costs,
                    mode="lines",
                    name="Total Cost",
                    line=dict(color="#66BB6A", width=3)
                ))
                
                # Add vertical line at EOQ
                fig.add_vline(x=eoq, line_dash="dash", line_color="#E91E63")
                
                fig.update_layout(
                    title="Cost vs. Order Quantity",
                    xaxis_title="Order Quantity",
                    yaxis_title="Cost ($)",
                    annotations=[
                        dict(
                            x=eoq,
                            y=min(total_costs) * 1.1,
                            text=f"EOQ = {eoq}",
                            showarrow=True,
                            arrowhead=1,
                            ax=0,
                            ay=-40
                        )
                    ]
                )
                
                st.plotly_chart(fig, )
    
    with tab5:
        st.subheader("Safety Stock Calculator")
        
        # Safety stock explanation
        st.write("""
        Safety Stock is a reserve of extra inventory maintained to buffer against unexpected increases in demand or potential supply chain disruptions, preventing stockouts.
        
        The formula is: Safety Stock = Z × σ × √L
        
        Where:
        - Z = Service level factor (based on desired service level)
        - σ = Standard deviation of daily demand
        - L = Lead time in days
        """)
        
        # Safety stock calculator
        with st.form("safety_stock_calculator"):
            col1, col2 = st.columns(2)
            
            with col1:
                avg_daily_demand = st.number_input("Average Daily Demand", min_value=0.1, value=100.0)
                std_dev_demand = st.number_input("Standard Deviation of Daily Demand", min_value=0.1, value=20.0)
            
            with col2:
                avg_lead_time = st.number_input("Average Lead Time (days)", min_value=0.1, value=5.0)
                std_dev_lead_time = st.number_input("Standard Deviation of Lead Time", min_value=0.0, value=1.0)
            
            service_level = st.slider("Service Level (%)", min_value=80, max_value=99, value=95)
            
            calculate = st.form_submit_button("Calculate Safety Stock")
            
            if calculate:
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
                
                st.success(f"Safety Stock: {safety_stock} units")
                st.info(f"Reorder Point: {reorder_point} units")
                
                # Safety stock visualization
                fig = go.Figure()
                
                # Generate time series data
                days = 30
                x = list(range(1, days + 1))
                
                # Normal demand
                normal_demand = [avg_daily_demand for _ in range(days)]
                
                # Actual demand with some randomness
                np.random.seed(42)  # For reproducibility
                actual_demand = [max(0, avg_daily_demand + np.random.normal(0, std_dev_demand)) for _ in range(days)]
                
                # Inventory level simulation
                inventory = [reorder_point + 500]  # Start with reorder point + some buffer
                
                for i in range(1, days):
                    # Decrease by previous day's demand
                    new_level = inventory[i-1] - actual_demand[i-1]
                    
                    # If below reorder point, restock
                    if new_level <= reorder_point:
                        new_level = reorder_point + 500  # Restock to reorder point + buffer
                    
                    inventory.append(new_level)
                
                # Plot inventory level
                fig.add_trace(go.Scatter(
                    x=x,
                    y=inventory,
                    mode="lines",
                    name="Inventory Level",
                    line=dict(color="#1E88E5", width=3)
                ))
                
                # Add actual demand
                fig.add_trace(go.Bar(
                    x=x,
                    y=actual_demand,
                    name="Daily Demand",
                    marker_color="#90CAF9"
                ))
                
                # Add reorder point line
                fig.add_hline(
                    y=reorder_point,
                    line_dash="dash",
                    line_color="#E91E63",
                    annotation_text="Reorder Point",
                    annotation_position="bottom right"
                )
                
                # Add safety stock line
                fig.add_hline(
                    y=safety_stock,
                    line_dash="dash",
                    line_color="#FF7043",
                    annotation_text="Safety Stock",
                    annotation_position="bottom left"
                )
                
                fig.update_layout(
                    title="Inventory Level Simulation with Safety Stock",
                    xaxis_title="Day",
                    yaxis_title="Units",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, width='stretch')

def products_page():
    st.markdown("<h1 class='main-header'>Products</h1>", unsafe_allow_html=True)
    
    # Search and filter
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input("Search Products", placeholder="Enter product name, SKU, or description")
    
    with col2:
        category_filter = st.selectbox("Category", ["All Categories", "Electronics", "Clothing", "Home Goods", "Food & Beverage", "Office Supplies"])
    
    with col3:
        status_filter = st.selectbox("Status", ["All", "In Stock", "Low Stock", "Out of Stock"])
    
    # Sample product data
    products = [
        {"id": "P001", "name": "Smartphone X", "category": "Electronics", "price": 699.99, "stock": 45, "status": "In Stock"},
        {"id": "P002", "name": "Laptop Pro", "category": "Electronics", "price": 1299.99, "stock": 20, "status": "In Stock"},
        {"id": "P003", "name": "Wireless Earbuds", "category": "Electronics", "price": 129.99, "stock": 8, "status": "Low Stock"},
        {"id": "P004", "name": "Cotton T-Shirt", "category": "Clothing", "price": 19.99, "stock": 150, "status": "In Stock"},
        {"id": "P005", "name": "Denim Jeans", "category": "Clothing", "price": 49.99, "stock": 75, "status": "In Stock"},
        {"id": "P006", "name": "Coffee Maker", "category": "Home Goods", "price": 89.99, "stock": 0, "status": "Out of Stock"},
        {"id": "P007", "name": "Blender", "category": "Home Goods", "price": 69.99, "stock": 12, "status": "In Stock"},
        {"id": "P008", "name": "Organic Coffee", "category": "Food & Beverage", "price": 12.99, "stock": 30, "status": "In Stock"},
        {"id": "P009", "name": "Notebook Set", "category": "Office Supplies", "price": 15.99, "stock": 5, "status": "Low Stock"},
        {"id": "P010", "name": "Desk Lamp", "category": "Home Goods", "price": 34.99, "stock": 18, "status": "In Stock"}
    ]
    
    # Apply filters
    filtered_products = products
    
    if search_query:
        filtered_products = [p for p in filtered_products if search_query.lower() in p["name"].lower() or search_query.lower() in p["id"].lower()]
    
    if category_filter != "All Categories":
        filtered_products = [p for p in filtered_products if p["category"] == category_filter]
    
    if status_filter != "All":
        filtered_products = [p for p in filtered_products if p["status"] == status_filter]
    
    # Display products in a grid
    if filtered_products:
        st.write(f"Showing {len(filtered_products)} products")
        
        # Create rows of 3 products each
        for i in range(0, len(filtered_products), 3):
            cols = st.columns(3)
            
            for j in range(3):
                if i + j < len(filtered_products):
                    product = filtered_products[i + j]
                    
                    with cols[j]:
                        st.markdown(f"""
                        <div class='card'>
                            <h3>{product['name']}</h3>
                            <p><strong>ID:</strong> {product['id']}</p>
                            <p><strong>Category:</strong> {product['category']}</p>
                            <p><strong>Price:</strong> ${product['price']}</p>
                            <p><strong>Stock:</strong> {product['stock']} units</p>
                            <p><strong>Status:</strong> {product['status']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.button("Edit", key=f"edit_{product['id']}")
                        with col2:
                            st.button("Restock", key=f"restock_{product['id']}")
    else:
        st.warning("No products found matching your criteria")
    
    # Add new product button
    st.button("Add New Product", type="primary")

def analytics_page():
    st.markdown("<h1 class='main-header'>Analytics Dashboard</h1>", unsafe_allow_html=True)
    
    # Time period selector
    col1, col2 = st.columns([3, 1])
    
    with col1:
        time_period = st.radio("Time Period", ["Monthly", "Quarterly", "Yearly"], horizontal=True)
    
    with col2:
        if time_period == "Monthly":
            period_selector = st.selectbox("Select Month", ["January 2023", "February 2023", "March 2023", "April 2023", "May 2023", "June 2023", "July 2023"])
        elif time_period == "Quarterly":
            period_selector = st.selectbox("Select Quarter", ["Q1 2023", "Q2 2023", "Q3 2022", "Q4 2022"])
        else:
            period_selector = st.selectbox("Select Year", ["2023", "2022", "2021"])
    
    # Key metrics
    st.subheader("Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", "$1.2M", "8.5%")
    with col2:
        st.metric("Order Fulfillment Rate", "94.2%", "2.1%")
    with col3:
        st.metric("On-Time Delivery", "91.5%", "-1.2%")
    with col4:
        st.metric("Inventory Turnover", "5.3", "0.7")
    
    # Revenue trends
    st.subheader("Revenue Trends")
    
    # Sample data
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
    revenue = [980000, 1050000, 920000, 1100000, 1150000, 1250000, 1200000]
    
    fig = px.line(
        x=months,
        y=revenue,
        labels={"x": "Month", "y": "Revenue ($)"},
        markers=True
    )
    
    fig.update_traces(line_color="#1E88E5", line_width=3)
    st.plotly_chart(fig, width='stretch')
    
    # Order and inventory analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Order Status Distribution")
        
        # Sample data
        order_statuses = ["Delivered", "In Transit", "Processing", "Delayed", "Cancelled"]
        order_counts = [450, 120, 80, 30, 20]
        
        fig = px.pie(
            names=order_statuses,
            values=order_counts,
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Blues
        )
        
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("Inventory Status")
        
        # Sample data
        inventory_statuses = ["Optimal", "Low Stock", "Overstock", "Out of Stock"]
        inventory_counts = [650, 150, 100, 50]
        
        fig = px.bar(
            x=inventory_statuses,
            y=inventory_counts,
            color=inventory_counts,
            color_continuous_scale="Blues",
            labels={"x": "Status", "y": "Number of SKUs"}
        )
        
        st.plotly_chart(fig, width='stretch')
    
    # Category performance
    st.subheader("Category Performance")
    
    # Sample data
    categories = ["Electronics", "Clothing", "Home Goods", "Food & Beverage", "Office Supplies"]
    sales = [450000, 320000, 280000, 100000, 50000]
    growth = [12.5, 8.2, 15.3, 5.7, -2.1]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=sales,
        name="Sales ($)",
        marker_color="#42A5F5"
    ))
    
    fig.add_trace(go.Scatter(
        x=categories,
        y=growth,
        name="Growth (%)",
        mode="markers+lines",
        marker=dict(size=12, color="#E91E63"),
        line=dict(color="#E91E63", width=2),
        yaxis="y2"
    ))
    
    fig.update_layout(
        xaxis_title="Category",
        yaxis_title="Sales ($)",
        yaxis2=dict(
            title="Growth (%)",
            overlaying="y",
            side="right",
            range=[-5, 20]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Supply chain performance
    st.subheader("Supply Chain Performance Metrics")
    
    # Sample data
    metrics = {
        "Perfect Order Rate": 92.5,
        "Order Cycle Time": 85.3,
        "Inventory Accuracy": 96.8,
        "Supplier On-Time Delivery": 89.2,
        "Backorder Rate": 78.6,
        "Fill Rate": 94.3
    }
    
    fig = go.Figure()

    # Arrange indicators in 2 rows x 3 columns to avoid overlap
    metric_names = list(metrics.keys())
    cols = 3
    rows = 2
    for name in metric_names:
        idx = metric_names.index(name)
        r = idx // cols
        c = idx % cols
        value = metrics[name]
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": name},
            domain={"row": r, "column": c},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#1E88E5"},
                "steps": [
                    {"range": [0, 60], "color": "#FFCDD2"},
                    {"range": [60, 80], "color": "#FFECB3"},
                    {"range": [80, 100], "color": "#C8E6C9"}
                ]
            }
        ))

    fig.update_layout(
        grid={"rows": rows, "columns": cols, "pattern": "independent"},
        height=600,
        margin=dict(t=40, b=40, l=20, r=20)
    )
    
    st.plotly_chart(fig, width='stretch')

def supply_chain_assistant_page():
    st.markdown("<h1 class='main-header'>Supply Chain Assistant</h1>", unsafe_allow_html=True)
    
    # Initialize chat history if not exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class='chat-message user-message'>
                <div>
                    <strong>You:</strong><br>
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-message bot-message'>
                <div>
                    <strong>Assistant:</strong><br>
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area("Ask me anything about your supply chain:", height=100)
        submitted = st.form_submit_button("Send")
        
        if submitted and user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Sample response (in a real app, this would be processed by a RAG system)
            if "inventory" in user_input.lower():
                response = "Based on our current inventory data, we have 987 SKUs in stock, 152 items are running low, and 106 items are out of stock. The overall inventory accuracy is at 87%, which is slightly below our target of 90%. Would you like me to provide more specific information about a particular product category?"
            elif "order" in user_input.lower():
                response = "We currently have 152 active orders in the system. 120 are on schedule for delivery, 25 are in processing, and 7 are experiencing delays due to supplier issues. The on-time delivery rate is 98.2% for this month, which is above our target of 95%. Is there a specific order you'd like to know more about?"
            elif "supplier" in user_input.lower():
                response = "We work with 45 active suppliers. Our top-performing supplier is ABC Electronics with a 99.5% on-time delivery rate. We're currently experiencing delays with XYZ Manufacturing, affecting some of our electronic components. Would you like me to provide a full supplier performance report?"
            elif "analytics" in user_input.lower():
                response = "Our latest analytics show a revenue increase of 8.5% compared to last month. The best-performing product category is Electronics with a 12.5% growth rate. Our inventory turnover has improved to 5.3 times per year. Would you like me to generate a detailed analytics report for a specific time period?"
            else:
                response = "I'm your supply chain assistant, ready to help with inventory management, order tracking, supplier information, and analytics. You can ask me about current inventory levels, order status, supplier performance, or request analytics reports. How can I assist you today?"
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Rerun to display the updated chat
            st.rerun()
    
    # Suggested questions
    st.subheader("Suggested Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.button("What's our current inventory status?")
        st.button("Show me supplier performance metrics")
    
    with col2:
        st.button("How many orders are delayed?")
        st.button("What's our inventory turnover rate?")

def document_upload_page():
    st.markdown("<h1 class='main-header'>Document Upload & Query</h1>", unsafe_allow_html=True)
    
    # Document upload section
    st.subheader("Upload Supply Chain Documents")
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt", "csv", "xlsx"])
    
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        
        # Process options
        st.write("### Processing Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            extract_text = st.checkbox("Extract Text", value=True)
            index_for_search = st.checkbox("Index for Search", value=True)
        
        with col2:
            generate_summary = st.checkbox("Generate Summary")
            extract_key_metrics = st.checkbox("Extract Key Metrics")
        
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                # Import necessary modules
                import tempfile
                from rag.document_processor import DocumentProcessor
                
                # Create temp directory if it doesn't exist
                temp_dir = os.path.join(os.getcwd(), "temp_uploads")
                os.makedirs(temp_dir, exist_ok=True)
                
                # Save the uploaded file to a temporary location
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process the document
                document_processor = DocumentProcessor()
                rag_handler = RAGHandler(mock=False)  # Set to False to use actual Pinecone
                
                # Process document and get chunks with embeddings
                document_chunks = document_processor.process_document(
                    temp_file_path, 
                    metadata={"filename": uploaded_file.name, "upload_date": str(pd.Timestamp.now())}
                )
                
                # Add document chunks to Pinecone
                for chunk in document_chunks:
                    rag_handler.add_document(
                        text=chunk["text"],
                        metadata=chunk["metadata"]
                    )
                
                st.success("Document processed and indexed successfully!")
                
                # Force refresh of the document library by clearing cache
                if 'document_library_cache' in st.session_state:
                    del st.session_state.document_library_cache
                
                # Rerun the app to refresh the document library
                st.rerun()
                
                if generate_summary:
                    st.subheader("Document Summary")
                    st.info("This document contains supplier performance data for Q2 2023. It highlights on-time delivery metrics, quality issues, and cost analysis for our top 10 suppliers. Key findings include a 5% improvement in overall on-time delivery and a 3% reduction in quality issues compared to Q1.")
                
                if extract_key_metrics:
                    st.subheader("Extracted Key Metrics")
                    
                    metrics = {
                        "On-Time Delivery Rate": "94.2%",
                        "Quality Acceptance Rate": "98.7%",
                        "Average Lead Time": "12.3 days",
                        "Cost Variance": "-2.1%",
                        "Supplier Responsiveness": "4.2/5"
                    }
                    
                    for metric, value in metrics.items():
                        st.metric(metric, value)
    
    # Document library
    st.subheader("Document Library")
    
    # Get uploaded documents from RAG handler
    try:
        rag_handler = RAGHandler(mock=False, api_key=os.environ.get("PINECONE_API_KEY"))
        uploaded_documents = rag_handler.get_all_documents()
        
        if uploaded_documents:
            doc_df = pd.DataFrame(uploaded_documents)
            st.dataframe(doc_df, width='stretch')
        else:
            st.info("No documents uploaded yet. Upload documents above to see them in the library.")
            
    except Exception as e:
        st.error(f"Error loading document library: {str(e)}")
        # Fallback to sample documents
        documents = [
            {"name": "Supplier Performance Q2 2023.pdf", "type": "PDF", "uploaded": "2023-07-10", "size": "2.4 MB"},
            {"name": "Inventory Analysis June 2023.xlsx", "type": "Excel", "uploaded": "2023-07-05", "size": "1.8 MB"},
            {"name": "Logistics Cost Report.docx", "type": "Word", "uploaded": "2023-06-28", "size": "950 KB"},
            {"name": "Warehouse Optimization Plan.pdf", "type": "PDF", "uploaded": "2023-06-15", "size": "3.2 MB"},
            {"name": "Supplier Contracts 2023.pdf", "type": "PDF", "uploaded": "2023-06-01", "size": "5.1 MB"}
        ]
        doc_df = pd.DataFrame(documents)
        st.dataframe(doc_df, width='stretch')
    
    # Query documents section
    st.subheader("Query Documents with RAG")
    
    query = st.text_input("Ask a question about your supply chain documents")
    
    if query:
        with st.spinner("Searching documents..."):
            try:
                # Use QueryEngine to process the query via RAG
                result = query_engine.process_query(query, top_k=5)
                st.write("### Search Results")
                
                # Display answer
                st.markdown(f"""
                <div class='card'>
                    <h4>Answer:</h4>
                    <p>{result.get('answer', 'No answer available.')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display sources
                sources = result.get('sources', [])
                if sources:
                    st.write("### Sources")
                    for src in sources:
                        md = src.get('metadata', {})
                        name = md.get('file_name') or md.get('filename') or 'Unknown Document'
                        score = src.get('score', 0)
                        preview = (md.get('text') or '')[:200]
                        st.markdown(f"""
                        <div class='card'>
                            <p><strong>Document:</strong> {name}</p>
                            <p><strong>Score:</strong> {round(score, 4)}</p>
                            <p><strong>Excerpt:</strong> {preview}...</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No relevant sources found. Try rephrasing your question or uploading more documents.")
                
                # Related documents (top 2)
                if sources:
                    st.write("### Related Documents")
                    cols = st.columns(2)
                    for i, src in enumerate(sources[:2]):
                        md = src.get('metadata', {})
                        name = md.get('file_name') or md.get('filename') or 'Unknown Document'
                        score = src.get('score', 0)
                        preview = (md.get('text') or '')[:240]
                        with cols[i]:
                            st.markdown(f"""
                            <div class='card'>
                                <h4>{name}</h4>
                                <p><strong>Relevance:</strong> {round(score * 100, 1)}%</p>
                                <p><strong>Excerpt:</strong> {preview}...</p>
                            </div>
                            """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Search failed: {str(e)}")

# Main app logic
def main():
    # Display sidebar
    sidebar()
    
    # Render the selected page
    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "Order Management":
        order_management_page()
    elif st.session_state.current_page == "Inventory Management":
        inventory_management_page()
    elif st.session_state.current_page == "Products":
        products_page()
    elif st.session_state.current_page == "Analytics":
        analytics_page()
    elif st.session_state.current_page == "Supply Chain Assistant":
        supply_chain_assistant_page()
    elif st.session_state.current_page == "Document Upload":
        document_upload_page()

if __name__ == "__main__":
    main()