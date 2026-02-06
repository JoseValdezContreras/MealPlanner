# meal_planner_app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
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
        
        # GRAINS
        FoodItem("G001", "Brown Rice", "grain", "1 cup", 216, 5, 45, 1.8, 3.5, 20, 0.8, 154, 10, 0, 0, 0, 0.80),
        FoodItem("G002", "Whole Wheat Bread", "grain", "2 slices", 160, 8, 30, 2, 4, 80, 2.1, 140, 300, 0, 0, 0, 0.60),
        FoodItem("G003", "Oatmeal", "grain", "1 cup", 166, 6, 28, 3.6, 4, 21, 1.6, 164, 2, 0, 0, 0, 0.50),
        FoodItem("G004", "Quinoa", "grain", "1 cup", 222, 8, 39, 3.6, 5, 31, 2.8, 318, 13, 0, 0, 0, 1.50),
        
        # VEGETABLES
        FoodItem("V001", "Broccoli", "vegetable", "1 cup", 31, 2.6, 6, 0.3, 2.4, 43, 0.7, 288, 30, 567, 81, 0, 0.70),
        FoodItem("V002", "Spinach", "vegetable", "1 cup", 7, 0.9, 1, 0.1, 0.7, 30, 0.8, 167, 24, 2813, 8, 0, 0.80),
        FoodItem("V003", "Carrots", "vegetable", "1 cup", 52, 1.2, 12, 0.3, 3.6, 42, 0.4, 410, 88, 21384, 7, 0, 0.50),
        FoodItem("V004", "Bell Peppers", "vegetable", "1 cup", 30, 1, 7, 0.3, 2.5, 12, 0.5, 211, 6, 157, 120, 0, 0.90),
        
        # FRUITS
        FoodItem("F001", "Banana", "fruit", "1 medium", 105, 1.3, 27, 0.4, 3.1, 6, 0.3, 422, 1, 76, 10, 0, 0.30),
        FoodItem("F002", "Apple", "fruit", "1 medium", 95, 0.5, 25, 0.3, 4.4, 11, 0.2, 195, 2, 98, 8, 0, 0.40),
        FoodItem("F003", "Orange", "fruit", "1 medium", 62, 1.2, 15, 0.2, 3.1, 52, 0.1, 237, 0, 295, 70, 0, 0.35),
        FoodItem("F004", "Blueberries", "fruit", "1 cup", 84, 1.1, 21, 0.5, 3.6, 9, 0.4, 114, 1, 80, 14, 0, 2.00),
        
        # DAIRY
        FoodItem("D001", "Milk (2%)", "dairy", "1 cup", 122, 8, 12, 5, 0, 293, 0.1, 366, 100, 395, 0, 120, 0.80),
        FoodItem("D002", "Cheddar Cheese", "dairy", "1 oz", 113, 7, 0.4, 9, 0, 204, 0.2, 28, 176, 300, 0, 12, 0.90),
        
        # FATS
        FoodItem("O001", "Olive Oil", "fat", "1 tbsp", 119, 0, 0, 14, 0, 0, 0.1, 0, 0, 0, 0, 0, 0.40),
        FoodItem("O002", "Almonds", "fat", "1 oz", 164, 6, 6, 14, 3.5, 76, 1.1, 208, 0, 0, 0, 0, 0.70),
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

def generate_balanced_meal_plan(foods: List[FoodItem]) -> Dict:
    """Generate balanced meal plan"""
    def get_food_by_id(food_id: str) -> Optional[FoodItem]:
        for food in foods:
            if food.id == food_id:
                return food
        return None
    
    meal_plan = [
        (get_food_by_id("G003"), 1),  # Oatmeal
        (get_food_by_id("D001"), 0.5),  # Milk
        (get_food_by_id("F001"), 1),  # Banana
        (get_food_by_id("O002"), 0.5),  # Almonds
        (get_food_by_id("G001"), 1),  # Brown Rice
        (get_food_by_id("P001"), 1.5),  # Chicken Breast
        (get_food_by_id("V001"), 2),  # Broccoli
        (get_food_by_id("V003"), 0.5),  # Carrots
        (get_food_by_id("P005"), 1),  # Black Beans
        (get_food_by_id("G002"), 1),  # Whole Wheat Bread
        (get_food_by_id("V002"), 3),  # Spinach
        (get_food_by_id("F003"), 1),  # Orange
        (get_food_by_id("P006"), 1),  # Greek Yogurt
        (get_food_by_id("F004"), 0.5),  # Blueberries
    ]
    
    meal_plan = [(f, s) for f, s in meal_plan if f is not None]
    nutrition_totals = calculate_nutrition_totals(meal_plan)
    
    return {
        'meal_plan': meal_plan,
        'nutrition_totals': nutrition_totals,
        'name': 'Balanced Plan'
    }

def generate_low_cost_plan(foods: List[FoodItem]) -> Dict:
    """Generate low-cost meal plan"""
    import random
    
    low_cost_foods = [
        ("P004", 2),  # Eggs
        ("P005", 1.5),  # Black Beans
        ("G003", 1.5),  # Oatmeal
        ("V003", 2),  # Carrots
        ("F001", 1),  # Banana
        ("F002", 1),  # Apple
        ("G001", 1),  # Brown Rice
        ("V001", 1.5),  # Broccoli
        ("D001", 0.5),  # Milk
        ("P006", 0.5),  # Greek Yogurt
    ]
    
    def get_food_by_id(food_id: str) -> Optional[FoodItem]:
        for food in foods:
            if food.id == food_id:
                return food
        return None
    
    meal_plan = [(get_food_by_id(fid), servings) for fid, servings in low_cost_foods]
    meal_plan = [(f, s) for f, s in meal_plan if f is not None]
    
    # Adjust servings to meet requirements
    nutrition = calculate_nutrition_totals(meal_plan)
    requirements = NutritionalRequirement()
    
    # Add more if needed
    if nutrition['protein_g'] < requirements.protein_g:
        meal_plan.append((get_food_by_id("P004"), 1))  # More eggs
    
    nutrition_totals = calculate_nutrition_totals(meal_plan)
    
    return {
        'meal_plan': meal_plan,
        'nutrition_totals': nutrition_totals,
        'name': 'Low Cost Plan'
    }

def generate_high_protein_plan(foods: List[FoodItem]) -> Dict:
    """Generate high-protein meal plan"""
    def get_food_by_id(food_id: str) -> Optional[FoodItem]:
        for food in foods:
            if food.id == food_id:
                return food
        return None
    
    meal_plan = [
        (get_food_by_id("P001"), 2),  # Chicken Breast
        (get_food_by_id("P006"), 2),  # Greek Yogurt
        (get_food_by_id("P004"), 3),  # Eggs
        (get_food_by_id("P003"), 1),  # Salmon
        (get_food_by_id("G001"), 1),  # Brown Rice
        (get_food_by_id("V001"), 2),  # Broccoli
        (get_food_by_id("F001"), 1),  # Banana
        (get_food_by_id("D001"), 1),  # Milk
        (get_food_by_id("O002"), 1),  # Almonds
    ]
    
    meal_plan = [(f, s) for f, s in meal_plan if f is not None]
    nutrition_totals = calculate_nutrition_totals(meal_plan)
    
    return {
        'meal_plan': meal_plan,
        'nutrition_totals': nutrition_totals,
        'name': 'High Protein Plan'
    }

# ==================== STREAMLIT APP ====================
def main():
    # Initialize session state
    if 'current_plan' not in st.session_state:
        st.session_state.current_plan = None
    if 'show_details' not in st.session_state:
        st.session_state.show_details = False
    
    # Header
    st.markdown('<h1 class="main-header">🍎 Smart Meal Planner</h1>', unsafe_allow_html=True)
    st.markdown("### Optimized Nutrition for 27-year-old Male (164cm)")
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h3 class="sub-header">🎯 Quick Actions</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Generate Balanced", use_container_width=True):
                foods = create_food_database()
                st.session_state.current_plan = generate_balanced_meal_plan(foods)
                st.session_state.show_details = True
                st.rerun()
            
            if st.button("💰 Low Cost Plan", use_container_width=True):
                foods = create_food_database()
                st.session_state.current_plan = generate_low_cost_plan(foods)
                st.session_state.show_details = True
                st.rerun()
        
        with col2:
            if st.button("💪 High Protein", use_container_width=True):
                foods = create_food_database()
                st.session_state.current_plan = generate_high_protein_plan(foods)
                st.session_state.show_details = True
                st.rerun()
            
            if st.button("🔄 Customize", use_container_width=True):
                st.session_state.show_details = True
                st.rerun()
        
        st.markdown("---")
        st.markdown('<h3 class="sub-header">⚙️ Settings</h3>', unsafe_allow_html=True)
        
        # Budget slider
        budget = st.slider("Daily Budget ($)", 5.0, 30.0, 15.0, 0.5)
        
        # Dietary preferences
        dietary_pref = st.multiselect(
            "Dietary Preferences",
            ["Vegetarian", "Low Sodium", "High Fiber", "Dairy Free", "Gluten Free"]
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
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.current_plan:
            plan = st.session_state.current_plan
            nutrition = plan['nutrition_totals']
            requirements = NutritionalRequirement()
            
            # Display plan name and cost
            st.markdown(f"### {plan['name']}")
            
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
            
            # Display meal plan items
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### 🍽️ Meal Plan Items")
            
            # Group by category
            categories = {}
            for food, servings in plan['meal_plan']:
                if food.category not in categories:
                    categories[food.category] = []
                categories[food.category].append((food, servings))
            
            for category, items in categories.items():
                st.markdown(f"**{category.title()}**")
                for food, servings in items:
                    cost = food.price * servings
                    st.markdown(f'''
                    <div class="food-card">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <strong>{food.name}</strong><br>
                                <small>{servings:.1f} serving(s) • {food.serving_size}</small>
                            </div>
                            <div style="text-align: right;">
                                <strong>${cost:.2f}</strong><br>
                                <small>{food.calories * servings:.0f} kcal</small>
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
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
            
            for i in range(0, len(nutrients), 3):
                cols = st.columns(3)
                for idx, (key, label, unit) in enumerate(nutrients[i:i+3]):
                    with cols[idx]:
                        actual = nutrition[key]
                        required = getattr(requirements, key)
                        percent = (actual / required * 100) if required > 0 else 0
                        
                        st.progress(min(percent / 100, 1.0))
                        st.metric(
                            label=label,
                            value=f"{actual:.0f}{unit}",
                            delta=f"{percent:.0f}%",
                            delta_color="normal" if percent >= 100 else "inverse"
                        )
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
                    <h3>🎯 How it works:</h3>
                    <ol style="text-align: left; font-size: 1.1rem;">
                        <li>Choose a plan type from the sidebar</li>
                        <li>View the generated meal plan</li>
                        <li>Check nutrition and cost details</li>
                        <li>Customize based on your preferences</li>
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
            categories = ['Calories', 'Protein', 'Carbs', 'Fat', 'Fiber']
            actual_values = [
                nutrition['calories'] / requirements.calories * 100,
                nutrition['protein_g'] / requirements.protein_g * 100,
                nutrition['carbs_g'] / requirements.carbs_g * 100,
                nutrition['fat_g'] / requirements.fat_g * 100,
                nutrition['fiber_g'] / requirements.fiber_g * 100,
            ]
            
            fig = go.Figure(data=go.Scatterpolar(
                r=actual_values,
                theta=categories,
                fill='toself',
                name='Current Intake',
                line_color='#2E86AB'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 150],
                        tickfont=dict(size=10)
                    )),
                showlegend=False,
                height=300,
                margin=dict(l=40, r=40, t=40, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Quick stats
            st.markdown("#### 📊 Quick Stats")
            
            stats = [
                ("Total Items", len(plan['meal_plan'])),
                ("Categories", len(set([f.category for f, _ in plan['meal_plan']]))),
                ("Cal/Serving", f"{nutrition['calories']/len(plan['meal_plan']):.0f}"),
                ("Cost/Meal", f"${nutrition['price']/3:.2f}"),
            ]
            
            for label, value in stats:
                col_a, col_b = st.columns([2, 1])
                col_a.write(label)
                col_b.write(f"**{value}**")
            
            # Export options
            st.markdown("---")
            st.markdown("#### 📤 Export Plan")
            
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                if st.button("📝 Copy to Clipboard", use_container_width=True):
                    # Create text representation
                    text = f"{plan['name']}\n\n"
                    for food, servings in plan['meal_plan']:
                        text += f"- {food.name}: {servings:.1f} serving(s) (${food.price * servings:.2f})\n"
                    text += f"\nTotal Cost: ${nutrition['price']:.2f}"
                    st.code(text)
                    st.success("Plan copied to clipboard (simulated)")
            
            with col_exp2:
                if st.button("🛒 Shopping List", use_container_width=True):
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
            
            for food in filtered_foods[:5]:  # Show first 5
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px; margin: 0.2rem 0;">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>{food.name}</strong><br>
                            <small>{food.category} • {food.serving_size}</small>
                        </div>
                        <div style="text-align: right;">
                            <strong>${food.price}</strong><br>
                            <small>{food.calories} kcal</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if len(filtered_foods) > 5:
                st.caption(f"Showing 5 of {len(filtered_foods)} foods. Use a plan to see all.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #777; font-size: 0.9rem;">
            <p>🍎 Smart Meal Planner • Uses USDA nutritional data • Optimized for cost and nutrition</p>
            <p>Note: This is a demonstration app. Consult a nutritionist for personalized advice.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()