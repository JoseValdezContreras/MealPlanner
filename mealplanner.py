# meal_planner_app_clickable.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
import random
import json

# Set page config
st.set_page_config(
    page_title="Smart Meal Planner",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #2E86AB;
    }
    .food-card {
        background-color: #f0f7ff;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s ease;
    }
    .food-card:hover {
        background-color: #e6f0ff;
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .remove-btn {
        color: #dc3545;
        background: none;
        border: 2px solid #dc3545;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        margin-left: 10px;
        flex-shrink: 0;
    }
    .remove-btn:hover {
        background-color: #dc3545;
        color: white;
        transform: scale(1.1);
    }
    .removed-item {
        opacity: 0.6;
        background-color: #f8d7da;
        border-color: #f5c6cb;
        text-decoration: line-through;
    }
    .restricted-list {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .restricted-badge {
        background-color: #dc3545;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-left: 5px;
    }
    .nutrient-good {
        color: #28a745;
        font-weight: bold;
    }
    .nutrient-bad {
        color: #dc3545;
        font-weight: bold;
    }
    .stButton > button {
        width: 100%;
        margin: 0.2rem 0;
        border-radius: 8px;
        font-weight: 500;
    }
    .cost-display {
        font-size: 1.8rem;
        color: #198754;
        font-weight: bold;
        text-align: center;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA STRUCTURES ====================
@dataclass
class NutritionalRequirement:
    """Nutritional requirements for a 27-year-old male, 164cm"""
    calories: float = 2500
    protein_g: float = 56
    carbs_g: float = 340
    fat_g: float = 83
    fiber_g: float = 38
    calcium_mg: float = 1000
    iron_mg: float = 8
    potassium_mg: float = 3400
    sodium_mg: float = 2300
    vitamin_a_iu: float = 900
    vitamin_c_mg: float = 90
    vitamin_d_iu: float = 600
    price_limit: float = 15.0

@dataclass
class FoodItem:
    id: str
    name: str
    category: str
    serving_size: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    calcium_mg: float
    iron_mg: float
    potassium_mg: float
    sodium_mg: float
    vitamin_a_iu: float
    vitamin_c_mg: float
    vitamin_d_iu: float
    price: float

# ==================== DATA INITIALIZATION ====================
@st.cache_data
def create_food_database() -> List[FoodItem]:
    """Create mock USDA database"""
    foods = [
        # PROTEINS
        FoodItem("P001", "Chicken Breast", "protein", "100g", 165, 31, 0, 3.6, 0, 11, 0.7, 256, 64, 40, 0, 0, 2.50),
        FoodItem("P002", "Ground Beef", "protein", "100g", 250, 26, 0, 17, 0, 12, 2.6, 318, 68, 0, 0, 0, 3.00),
        FoodItem("P003", "Salmon", "protein", "100g", 208, 20, 0, 13, 0, 9, 0.5, 363, 59, 149, 0, 570, 4.50),
        FoodItem("P004", "Eggs", "protein", "2 large", 143, 12.6, 1.1, 9.5, 0, 56, 1.8, 138, 142, 540, 0, 87, 0.60),
        FoodItem("P005", "Black Beans", "protein", "1 cup", 227, 15, 41, 1, 15, 46, 3.6, 611, 1, 0, 0, 0, 1.20),
        FoodItem("P006", "Greek Yogurt", "protein", "170g", 100, 18, 6, 0.4, 0, 200, 0.1, 240, 65, 150, 0, 0, 1.80),
        FoodItem("P007", "Tofu", "protein", "100g", 76, 8, 2, 4.8, 1, 350, 1.6, 121, 7, 0, 0, 0, 1.50),
        FoodItem("P008", "Turkey Breast", "protein", "100g", 135, 30, 0, 1, 0, 13, 1.5, 290, 50, 0, 0, 0, 2.80),
        FoodItem("P009", "Cottage Cheese", "protein", "1/2 cup", 110, 14, 4, 5, 0, 69, 0.2, 104, 340, 200, 0, 0, 1.20),
        
        # GRAINS
        FoodItem("G001", "Brown Rice", "grain", "1 cup", 216, 5, 45, 1.8, 3.5, 20, 0.8, 154, 10, 0, 0, 0, 0.80),
        FoodItem("G002", "Whole Wheat Bread", "grain", "2 slices", 160, 8, 30, 2, 4, 80, 2.1, 140, 300, 0, 0, 0, 0.60),
        FoodItem("G003", "Oatmeal", "grain", "1 cup", 166, 6, 28, 3.6, 4, 21, 1.6, 164, 2, 0, 0, 0, 0.50),
        FoodItem("G004", "Quinoa", "grain", "1 cup", 222, 8, 39, 3.6, 5, 31, 2.8, 318, 13, 0, 0, 0, 1.50),
        FoodItem("G005", "Whole Wheat Pasta", "grain", "2 oz", 200, 8, 42, 1, 6, 20, 2.5, 120, 10, 0, 0, 0, 0.90),
        
        # VEGETABLES
        FoodItem("V001", "Broccoli", "vegetable", "1 cup", 31, 2.6, 6, 0.3, 2.4, 43, 0.7, 288, 30, 567, 81, 0, 0.70),
        FoodItem("V002", "Spinach", "vegetable", "1 cup", 7, 0.9, 1, 0.1, 0.7, 30, 0.8, 167, 24, 2813, 8, 0, 0.80),
        FoodItem("V003", "Carrots", "vegetable", "1 cup", 52, 1.2, 12, 0.3, 3.6, 42, 0.4, 410, 88, 21384, 7, 0, 0.50),
        FoodItem("V004", "Bell Peppers", "vegetable", "1 cup", 30, 1, 7, 0.3, 2.5, 12, 0.5, 211, 6, 157, 120, 0, 0.90),
        FoodItem("V005", "Sweet Potato", "vegetable", "1 medium", 103, 2.3, 24, 0.2, 3.8, 43, 0.8, 448, 72, 19218, 22, 0, 0.60),
        FoodItem("V006", "Kale", "vegetable", "1 cup", 33, 2.9, 6, 0.6, 1.3, 90, 1.1, 329, 30, 10302, 80, 0, 0.90),
        
        # FRUITS
        FoodItem("F001", "Banana", "fruit", "1 medium", 105, 1.3, 27, 0.4, 3.1, 6, 0.3, 422, 1, 76, 10, 0, 0.30),
        FoodItem("F002", "Apple", "fruit", "1 medium", 95, 0.5, 25, 0.3, 4.4, 11, 0.2, 195, 2, 98, 8, 0, 0.40),
        FoodItem("F003", "Orange", "fruit", "1 medium", 62, 1.2, 15, 0.2, 3.1, 52, 0.1, 237, 0, 295, 70, 0, 0.35),
        FoodItem("F004", "Blueberries", "fruit", "1 cup", 84, 1.1, 21, 0.5, 3.6, 9, 0.4, 114, 1, 80, 14, 0, 2.00),
        FoodItem("F005", "Avocado", "fruit", "1/2 medium", 114, 1.3, 6, 10.5, 4.6, 11, 0.4, 345, 5, 108, 6, 0, 1.20),
        
        # DAIRY
        FoodItem("D001", "Milk (2%)", "dairy", "1 cup", 122, 8, 12, 5, 0, 293, 0.1, 366, 100, 395, 0, 120, 0.80),
        FoodItem("D002", "Cheddar Cheese", "dairy", "1 oz", 113, 7, 0.4, 9, 0, 204, 0.2, 28, 176, 300, 0, 12, 0.90),
        
        # FATS
        FoodItem("O001", "Olive Oil", "fat", "1 tbsp", 119, 0, 0, 14, 0, 0, 0.1, 0, 0, 0, 0, 0, 0.40),
        FoodItem("O002", "Almonds", "fat", "1 oz", 164, 6, 6, 14, 3.5, 76, 1.1, 208, 0, 0, 0, 0, 0.70),
        FoodItem("O003", "Peanut Butter", "fat", "2 tbsp", 188, 8, 6, 16, 2, 15, 0.6, 214, 150, 0, 0, 0, 0.50),
    ]
    return foods

@st.cache_data
def get_foods_by_category(foods: List[FoodItem], category: str) -> List[FoodItem]:
    """Get foods by category"""
    return [f for f in foods if f.category == category]

def calculate_nutrition_totals(food_items: List[Tuple[FoodItem, float]]) -> Dict[str, float]:
    """Calculate total nutrition"""
    totals = {
        'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fat_g': 0,
        'fiber_g': 0, 'calcium_mg': 0, 'iron_mg': 0, 'potassium_mg': 0,
        'sodium_mg': 0, 'vitamin_a_iu': 0, 'vitamin_c_mg': 0,
        'vitamin_d_iu': 0, 'price': 0
    }
    
    for food, servings in food_items:
        totals['calories'] += food.calories * servings
        totals['protein_g'] += food.protein_g * servings
        totals['carbs_g'] += food.carbs_g * servings
        totals['fat_g'] += food.fat_g * servings
        totals['fiber_g'] += food.fiber_g * servings
        totals['calcium_mg'] += food.calcium_mg * servings
        totals['iron_mg'] += food.iron_mg * servings
        totals['potassium_mg'] += food.potassium_mg * servings
        totals['sodium_mg'] += food.sodium_mg * servings
        totals['vitamin_a_iu'] += food.vitamin_a_iu * servings
        totals['vitamin_c_mg'] += food.vitamin_c_mg * servings
        totals['vitamin_d_iu'] += food.vitamin_d_iu * servings
        totals['price'] += food.price * servings
        
    return totals

def get_food_by_id(foods: List[FoodItem], food_id: str) -> Optional[FoodItem]:
    """Get food by ID"""
    for food in foods:
        if food.id == food_id:
            return food
    return None

def generate_plan_with_restrictions(foods: List[FoodItem], restricted_ids: Set[str], 
                                   plan_type: str = "balanced") -> Dict:
    """Generate meal plan while avoiding restricted foods"""
    
    # Filter out restricted foods
    available_foods = [f for f in foods if f.id not in restricted_ids]
    
    if not available_foods:
        return None
    
    if plan_type == "balanced":
        # Balanced plan without restricted foods
        balanced_items = [
            ("G003", 1), ("D001", 0.5), ("F001", 1), ("O002", 0.5),
            ("G001", 1), ("P001", 1.5), ("V001", 2), ("V003", 0.5),
            ("P005", 1), ("G002", 1), ("V002", 3), ("F003", 1),
            ("P006", 1), ("F004", 0.5)
        ]
        
        # Replace restricted items with alternatives
        meal_plan = []
        for food_id, servings in balanced_items:
            if food_id in restricted_ids:
                # Find alternative
                original_food = get_food_by_id(foods, food_id)
                if original_food:
                    alternatives = [f for f in available_foods if f.category == original_food.category]
                    if alternatives:
                        alt_food = random.choice(alternatives)
                        meal_plan.append((alt_food, servings))
            else:
                food = get_food_by_id(available_foods, food_id)
                if food:
                    meal_plan.append((food, servings))
    
    elif plan_type == "low_cost":
        # Low cost plan
        low_cost_items = [
            ("P004", 2), ("P005", 1.5), ("G003", 1.5), ("V003", 2),
            ("F001", 1), ("F002", 1), ("G001", 1), ("V001", 1.5),
            ("D001", 0.5), ("P006", 0.5)
        ]
        
        meal_plan = []
        for food_id, servings in low_cost_items:
            if food_id not in restricted_ids:
                food = get_food_by_id(available_foods, food_id)
                if food:
                    meal_plan.append((food, servings))
    
    elif plan_type == "high_protein":
        # High protein plan
        high_protein_items = [
            ("P001", 2), ("P006", 2), ("P004", 3), ("P003", 1),
            ("G001", 1), ("V001", 2), ("F001", 1), ("D001", 1),
            ("O002", 1)
        ]
        
        meal_plan = []
        for food_id, servings in high_protein_items:
            if food_id not in restricted_ids:
                food = get_food_by_id(available_foods, food_id)
                if food:
                    meal_plan.append((food, servings))
    
    else:
        return None
    
    # Add more items if nutrition is insufficient
    nutrition = calculate_nutrition_totals(meal_plan)
    requirements = NutritionalRequirement()
    
    # Check for deficiencies and add more foods if needed
    if nutrition['calories'] < requirements.calories * 0.9:
        # Add more calorie-dense foods
        calorie_foods = [f for f in available_foods if f.calories > 150]
        if calorie_foods:
            extra_food = random.choice(calorie_foods[:5])
            meal_plan.append((extra_food, 1))
    
    if nutrition['protein_g'] < requirements.protein_g * 0.9:
        # Add more protein
        protein_foods = [f for f in available_foods if f.protein_g > 10]
        if protein_foods:
            extra_food = random.choice(protein_foods[:5])
            meal_plan.append((extra_food, 1))
    
    # Recalculate nutrition
    nutrition_totals = calculate_nutrition_totals(meal_plan)
    
    return {
        'meal_plan': meal_plan,
        'nutrition_totals': nutrition_totals,
        'restricted_ids': restricted_ids,
        'plan_type': plan_type
    }

def generate_balanced_meal_plan(foods: List[FoodItem]) -> Dict:
    """Generate balanced meal plan (initial)"""
    return generate_plan_with_restrictions(foods, set(), "balanced")

def generate_low_cost_plan(foods: List[FoodItem]) -> Dict:
    """Generate low-cost meal plan (initial)"""
    return generate_plan_with_restrictions(foods, set(), "low_cost")

def generate_high_protein_plan(foods: List[FoodItem]) -> Dict:
    """Generate high-protein meal plan (initial)"""
    return generate_plan_with_restrictions(foods, set(), "high_protein")

# ==================== STREAMLIT APP ====================
def main():
    # Initialize session state
    if 'current_plan' not in st.session_state:
        st.session_state.current_plan = None
    if 'restricted_foods' not in st.session_state:
        st.session_state.restricted_foods = set()
    if 'plan_type' not in st.session_state:
        st.session_state.plan_type = "balanced"
    if 'recalculate_trigger' not in st.session_state:
        st.session_state.recalculate_trigger = False
    
    # Header
    st.markdown('<h1 class="main-header">🍎 Smart Meal Planner</h1>', unsafe_allow_html=True)
    st.markdown("### Optimized Nutrition for 27-year-old Male (164cm)")
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h3 class="sub-header">🎯 Generate Plans</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Balanced", use_container_width=True, key="btn_balanced"):
                foods = create_food_database()
                st.session_state.current_plan = generate_balanced_meal_plan(foods)
                st.session_state.restricted_foods = set()
                st.session_state.plan_type = "balanced"
                st.rerun()
            
            if st.button("💰 Low Cost", use_container_width=True, key="btn_lowcost"):
                foods = create_food_database()
                st.session_state.current_plan = generate_low_cost_plan(foods)
                st.session_state.restricted_foods = set()
                st.session_state.plan_type = "low_cost"
                st.rerun()
        
        with col2:
            if st.button("💪 High Protein", use_container_width=True, key="btn_highprotein"):
                foods = create_food_database()
                st.session_state.current_plan = generate_high_protein_plan(foods)
                st.session_state.restricted_foods = set()
                st.session_state.plan_type = "high_protein"
                st.rerun()
        
        # Clear restrictions button
        if st.button("🔄 Clear Restrictions", use_container_width=True):
            if st.session_state.current_plan:
                foods = create_food_database()
                st.session_state.restricted_foods = set()
                st.session_state.current_plan = generate_plan_with_restrictions(
                    foods, 
                    st.session_state.restricted_foods,
                    st.session_state.plan_type
                )
                st.rerun()
        
        st.markdown("---")
        st.markdown('<h3 class="sub-header">⚙️ Settings</h3>', unsafe_allow_html=True)
        
        # Budget slider
        budget = st.slider("Daily Budget ($)", 5.0, 30.0, 15.0, 0.5, key="budget_slider")
        
        # Dietary preferences
        dietary_pref = st.multiselect(
            "Dietary Preferences",
            ["Vegetarian", "Low Sodium", "High Fiber", "Dairy Free", "Gluten Free"],
            key="dietary_pref"
        )
        
        st.markdown("---")
        st.markdown("### 📋 Requirements")
        req = NutritionalRequirement()
        
        metrics_data = [
            ("Calories", f"{req.calories:,} kcal"),
            ("Protein", f"{req.protein_g}g"),
            ("Carbs", f"{req.carbs_g}g"),
            ("Fat", f"{req.fat_g}g"),
            ("Budget", f"${req.price_limit}")
        ]
        
        for label, value in metrics_data:
            st.metric(label=label, value=value)
        
        # Show restricted foods in sidebar
        if st.session_state.restricted_foods:
            st.markdown("---")
            st.markdown("### 🚫 Restricted Foods")
            foods = create_food_database()
            restricted_names = []
            for food_id in st.session_state.restricted_foods:
                food = get_food_by_id(foods, food_id)
                if food:
                    restricted_names.append(food.name)
            
            if restricted_names:
                st.markdown(f"**{len(restricted_names)} item(s) restricted:**")
                for name in restricted_names:
                    st.markdown(f"- {name}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.current_plan:
            plan = st.session_state.current_plan
            nutrition = plan['nutrition_totals']
            requirements = NutritionalRequirement()
            foods_db = create_food_database()
            
            # Display plan name and cost
            plan_name = "Balanced Plan"
            if st.session_state.plan_type == "low_cost":
                plan_name = "Low Cost Plan"
            elif st.session_state.plan_type == "high_protein":
                plan_name = "High Protein Plan"
            
            st.markdown(f"### {plan_name}")
            
            # Show warning if many restrictions
            if len(st.session_state.restricted_foods) > 5:
                st.markdown("""
                <div class="warning-box">
                    ⚠️ <strong>Many restrictions applied</strong><br>
                    With {} items restricted, it may be difficult to meet all nutritional requirements.
                    Consider clearing some restrictions.
                </div>
                """.format(len(st.session_state.restricted_foods)), unsafe_allow_html=True)
            
            col_cost, col_status = st.columns(2)
            with col_cost:
                st.markdown(f'<div class="cost-display">${nutrition["price"]:.2f}</div>', 
                          unsafe_allow_html=True)
                st.caption("Total Daily Cost")
            
            with col_status:
                if nutrition['price'] <= budget:
                    st.success(f"✅ Within Budget (${budget})")
                else:
                    st.error(f"❌ Over Budget by ${nutrition['price'] - budget:.2f}")
                
                # Show number of restrictions
                if st.session_state.restricted_foods:
                    st.info(f"🚫 {len(st.session_state.restricted_foods)} item(s) restricted")
            
            # Display meal plan items WITH REMOVE BUTTONS
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### 🍽️ Meal Plan Items")
            st.markdown("*Click the red ❌ to remove an item from the plan*")
            
            # Create columns for Remove buttons
            remove_col1, remove_col2 = st.columns([5, 1])
            
            # Group by category
            categories = {}
            for food, servings in plan['meal_plan']:
                if food.category not in categories:
                    categories[food.category] = []
                categories[food.category].append((food, servings))
            
            for category, items in categories.items():
                st.markdown(f"**{category.title()}**")
                
                # Create a unique container for each food item
                for idx, (food, servings) in enumerate(items):
                    # Create columns for each item
                    item_col1, item_col2, item_col3 = st.columns([4, 1, 1])
                    
                    with item_col1:
                        # Food info
                        st.markdown(f"""
                        <div>
                            <strong>{food.name}</strong><br>
                            <small>{servings:.1f} serving(s) • {food.serving_size}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with item_col2:
                        # Cost and calories
                        cost = food.price * servings
                        calories = food.calories * servings
                        st.markdown(f"""
                        <div style="text-align: right;">
                            <strong>${cost:.2f}</strong><br>
                            <small>{calories:.0f} kcal</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with item_col3:
                        # Remove button
                        button_key = f"remove_{food.id}_{idx}"
                        if st.button("❌", key=button_key):
                            # Add to restricted foods
                            st.session_state.restricted_foods.add(food.id)
                            
                            # Regenerate plan with new restriction
                            new_plan = generate_plan_with_restrictions(
                                foods_db,
                                st.session_state.restricted_foods,
                                st.session_state.plan_type
                            )
                            
                            if new_plan:
                                st.session_state.current_plan = new_plan
                            else:
                                st.error("Cannot generate plan with these restrictions!")
                            
                            st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show restricted items section
            if st.session_state.restricted_foods:
                st.markdown('<div class="restricted-list">', unsafe_allow_html=True)
                st.markdown("#### 🚫 Restricted Items")
                
                restricted_names = []
                for food_id in st.session_state.restricted_foods:
                    food = get_food_by_id(foods_db, food_id)
                    if food:
                        restricted_names.append(food.name)
                
                # Display in columns
                if restricted_names:
                    num_cols = 3
                    names_per_col = (len(restricted_names) + num_cols - 1) // num_cols
                    
                    cols = st.columns(num_cols)
                    for i, col in enumerate(cols):
                        start_idx = i * names_per_col
                        end_idx = min(start_idx + names_per_col, len(restricted_names))
                        
                        with col:
                            for name in restricted_names[start_idx:end_idx]:
                                st.markdown(f"~~{name}~~")
                
                # Clear all restrictions button
                if st.button("Clear All Restrictions", type="secondary"):
                    st.session_state.restricted_foods = set()
                    st.session_state.current_plan = generate_plan_with_restrictions(
                        foods_db,
                        set(),
                        st.session_state.plan_type
                    )
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Nutrition comparison
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### ⚖️ Nutrition Status")
            
            # Key nutrients to display
            nutrients = [
                ('calories', 'Calories', 'kcal'),
                ('protein_g', 'Protein', 'g'),
                ('carbs_g', 'Carbs', 'g'),
                ('fat_g', 'Fat', 'g'),
                ('fiber_g', 'Fiber', 'g'),
                ('calcium_mg', 'Calcium', 'mg'),
                ('iron_mg', 'Iron', 'mg'),
            ]
            
            # Create progress bars for nutrients
            for i in range(0, len(nutrients), 3):
                cols = st.columns(3)
                for idx, (key, label, unit) in enumerate(nutrients[i:i+3]):
                    with cols[idx]:
                        actual = nutrition[key]
                        required = getattr(requirements, key)
                        percent = (actual / required * 100) if required > 0 else 0
                        
                        # Color code the progress bar
                        progress_color = "green" if percent >= 100 else "orange" if percent >= 80 else "red"
                        
                        st.progress(min(percent / 100, 1.0))
                        st.metric(
                            label=label,
                            value=f"{actual:.0f}{unit}",
                            delta=f"{percent:.0f}%",
                            delta_color="normal" if percent >= 100 else "inverse"
                        )
            
            # Warning for major deficiencies
            deficiencies = []
            if nutrition['calories'] < requirements.calories * 0.8:
                deficiencies.append("Calories")
            if nutrition['protein_g'] < requirements.protein_g * 0.8:
                deficiencies.append("Protein")
            if nutrition['calcium_mg'] < requirements.calcium_mg * 0.8:
                deficiencies.append("Calcium")
            
            if deficiencies:
                st.warning(f"⚠️ Major deficiencies: {', '.join(deficiencies)}. Consider fewer restrictions.")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            # Welcome screen
            st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem;">
                <h2 style="color: #666; margin-bottom: 2rem;">Welcome to Smart Meal Planner! 🍎</h2>
                <p style="font-size: 1.2rem; color: #777; max-width: 600px; margin: 0 auto 3rem auto;">
                    Generate optimized meal plans that meet nutritional requirements while minimizing costs.
                    Click on any plan in the sidebar to get started!
                </p>
                <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 3rem; border-radius: 20px; color: white; max-width: 500px;">
                    <h3>🎯 New Feature: Click to Remove!</h3>
                    <ol style="text-align: left; font-size: 1.1rem;">
                        <li>Generate a meal plan</li>
                        <li>Click the <span style="color: #ff6b6b; font-weight: bold;">red ❌</span> next to any item</li>
                        <li>Plan automatically recalculates without that item</li>
                        <li>Continue refining until satisfied!</li>
                    </ol>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.session_state.current_plan:
            plan = st.session_state.current_plan
            nutrition = plan['nutrition_totals']
            requirements = NutritionalRequirement()
            
            # Nutrition radar chart
            st.markdown("#### 📈 Nutrition Overview")
            
            # Prepare data for radar chart
            categories = ['Calories', 'Protein', 'Carbs', 'Fat', 'Fiber', 'Calcium']
            actual_values = [
                min(nutrition['calories'] / requirements.calories * 100, 150),
                min(nutrition['protein_g'] / requirements.protein_g * 100, 150),
                min(nutrition['carbs_g'] / requirements.carbs_g * 100, 150),
                min(nutrition['fat_g'] / requirements.fat_g * 100, 150),
                min(nutrition['fiber_g'] / requirements.fiber_g * 100, 150),
                min(nutrition['calcium_mg'] / requirements.calcium_mg * 100, 150),
            ]
            
            fig = go.Figure(data=go.Scatterpolar(
                r=actual_values,
                theta=categories,
                fill='toself',
                name='Current Intake',
                line_color='#2E86AB',
                fillcolor='rgba(46, 134, 171, 0.3)'
            ))
            
            # Add target line (100%)
            fig.add_trace(go.Scatterpolar(
                r=[100] * len(categories),
                theta=categories,
                name='Target',
                line_color='#28a745',
                line_dash='dash'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 150],
                        tickfont=dict(size=10)
                    )),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                height=300,
                margin=dict(l=40, r=40, t=40, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Quick stats
            st.markdown("#### 📊 Quick Stats")
            
            stats = [
                ("Total Items", len(plan['meal_plan'])),
                ("Categories", len(set([f.category for f, _ in plan['meal_plan']]))),
                ("Avg Cal/Serving", f"{nutrition['calories']/len(plan['meal_plan']):.0f}"),
                ("Cost/Meal", f"${nutrition['price']/3:.2f}"),
                ("Restricted Items", len(st.session_state.restricted_foods)),
            ]
            
            for label, value in stats:
                col_a, col_b = st.columns([2, 1])
                col_a.write(label)
                col_b.write(f"**{value}**")
            
            # Suggestions for improvement
            if nutrition['price'] > budget:
                st.markdown("#### 💡 Cost Reduction Tips")
                st.markdown("""
                1. Click ❌ on expensive items like Salmon ($4.50)
                2. Try the **Low Cost** plan preset
                3. Increase budget in sidebar
                """)
            
            if any([
                nutrition['calories'] < requirements.calories * 0.9,
                nutrition['protein_g'] < requirements.protein_g * 0.9,
                nutrition['calcium_mg'] < requirements.calcium_mg * 0.9
            ]):
                st.markdown("#### 💪 Nutrition Boost")
                st.markdown("""
                1. Clear some restrictions
                2. Try **High Protein** plan
                3. Allow more food categories
                """)
            
            # Export options
            st.markdown("---")
            st.markdown("#### 📤 Export Plan")
            
            if st.button("📝 Copy Plan to Clipboard", use_container_width=True):
                # Create text representation
                text = f"{'Balanced' if st.session_state.plan_type == 'balanced' else 'Low Cost' if st.session_state.plan_type == 'low_cost' else 'High Protein'} Meal Plan\n\n"
                text += "Items:\n"
                for food, servings in plan['meal_plan']:
                    text += f"- {food.name}: {servings:.1f} serving(s) (${food.price * servings:.2f})\n"
                
                if st.session_state.restricted_foods:
                    text += f"\nRestricted Items ({len(st.session_state.restricted_foods)}):\n"
                    for food_id in st.session_state.restricted_foods:
                        food = get_food_by_id(create_food_database(), food_id)
                        if food:
                            text += f"- {food.name}\n"
                
                text += f"\nTotal Cost: ${nutrition['price']:.2f}"
                text += f"\nNutrition: {nutrition['calories']:.0f} cal, {nutrition['protein_g']:.0f}g protein"
                
                st.code(text)
                st.success("Plan copied to clipboard (simulated)")
            
            if st.button("🛒 Generate Shopping List", use_container_width=True):
                # Create shopping list
                shopping = {}
                for food, servings in plan['meal_plan']:
                    if food.name not in shopping:
                        shopping[food.name] = 0
                    shopping[food.name] += servings
                
                st.markdown("**Shopping List:**")
                for item, amount in shopping.items():
                    st.write(f"- {item}: {amount:.1f} servings")
        
        else:
            # Food database preview
            st.markdown("#### 🛒 Available Foods")
            foods = create_food_database()
            
            category = st.selectbox(
                "Filter by category",
                ["All"] + sorted(set([f.category for f in foods]))
            )
            
            filtered_foods = foods
            if category != "All":
                filtered_foods = [f for f in foods if f.category == category]
            
            for food in filtered_foods[:6]:  # Show first 6
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px; margin: 0.2rem 0;">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>{food.name}</strong><br>
                            <small>{food.category} • {food.serving_size}</small>
                        </div>
                        <div style="text-align: right;">
                            <strong>${food.price:.2f}</strong><br>
                            <small>{food.calories} kcal</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if len(filtered_foods) > 6:
                st.caption(f"Showing 6 of {len(filtered_foods)} foods")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #777; font-size: 0.9rem;">
            <p>🍎 Smart Meal Planner • Click red ❌ to remove items • Plan recalculates automatically</p>
            <p>Note: This is a demonstration app. Consult a nutritionist for personalized advice.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
