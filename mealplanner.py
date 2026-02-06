import pandas as pd
import numpy as np
import random
from typing import List, Dict, Tuple, Optional
import json
from dataclasses import dataclass
from datetime import datetime

# ==================== DATA STRUCTURES ====================
@dataclass
class NutritionalRequirement:
    """Nutritional requirements for a 27-year-old male, 164cm"""
    calories: float = 2500  # Estimated based on sedentary activity
    protein_g: float = 56  # 0.8g per kg (70kg estimated weight)
    carbs_g: float = 340   # ~55% of calories
    fat_g: float = 83      # ~30% of calories
    fiber_g: float = 38    # AI for men
    calcium_mg: float = 1000
    iron_mg: float = 8
    potassium_mg: float = 3400
    sodium_mg: float = 2300
    vitamin_a_iu: float = 900
    vitamin_c_mg: float = 90
    vitamin_d_iu: float = 600
    price_limit: float = 15.0  # Daily budget in USD

@dataclass
class FoodItem:
    id: str
    name: str
    category: str  # 'protein', 'grain', 'vegetable', 'fruit', 'dairy', 'fat'
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
    price: float  # Price per serving in USD

class USDAFoodDatabase:
    """Mock USDA food database with realistic nutritional values"""
    
    def __init__(self):
        self.foods = self._create_food_database()
    
    def _create_food_database(self) -> List[FoodItem]:
        """Create a mock USDA database with realistic foods"""
        
        foods = [
            # PROTEINS
            FoodItem("P001", "Chicken Breast", "protein", "100g", 165, 31, 0, 3.6, 0, 11, 0.7, 256, 64, 40, 0, 0, 2.50),
            FoodItem("P002", "Ground Beef (85/15)", "protein", "100g", 250, 26, 0, 17, 0, 12, 2.6, 318, 68, 0, 0, 0, 3.00),
            FoodItem("P003", "Salmon", "protein", "100g", 208, 20, 0, 13, 0, 9, 0.5, 363, 59, 149, 0, 570, 4.50),
            FoodItem("P004", "Eggs", "protein", "2 large", 143, 12.6, 1.1, 9.5, 0, 56, 1.8, 138, 142, 540, 0, 87, 0.60),
            FoodItem("P005", "Black Beans", "protein", "1 cup", 227, 15, 41, 1, 15, 46, 3.6, 611, 1, 0, 0, 0, 1.20),
            FoodItem("P006", "Greek Yogurt", "protein", "170g", 100, 18, 6, 0.4, 0, 200, 0.1, 240, 65, 150, 0, 0, 1.80),
            FoodItem("P007", "Tofu", "protein", "100g", 76, 8, 2, 4.8, 1, 350, 1.6, 121, 7, 0, 0, 0, 1.50),
            
            # GRAINS
            FoodItem("G001", "Brown Rice", "grain", "1 cup cooked", 216, 5, 45, 1.8, 3.5, 20, 0.8, 154, 10, 0, 0, 0, 0.80),
            FoodItem("G002", "Whole Wheat Bread", "grain", "2 slices", 160, 8, 30, 2, 4, 80, 2.1, 140, 300, 0, 0, 0, 0.60),
            FoodItem("G003", "Oatmeal", "grain", "1 cup cooked", 166, 6, 28, 3.6, 4, 21, 1.6, 164, 2, 0, 0, 0, 0.50),
            FoodItem("G004", "Quinoa", "grain", "1 cup cooked", 222, 8, 39, 3.6, 5, 31, 2.8, 318, 13, 0, 0, 0, 1.50),
            FoodItem("G005", "Whole Wheat Pasta", "grain", "2 oz dry", 200, 8, 42, 1, 6, 20, 2.5, 120, 10, 0, 0, 0, 0.90),
            
            # VEGETABLES
            FoodItem("V001", "Broccoli", "vegetable", "1 cup chopped", 31, 2.6, 6, 0.3, 2.4, 43, 0.7, 288, 30, 567, 81, 0, 0.70),
            FoodItem("V002", "Spinach", "vegetable", "1 cup raw", 7, 0.9, 1, 0.1, 0.7, 30, 0.8, 167, 24, 2813, 8, 0, 0.80),
            FoodItem("V003", "Carrots", "vegetable", "1 cup chopped", 52, 1.2, 12, 0.3, 3.6, 42, 0.4, 410, 88, 21384, 7, 0, 0.50),
            FoodItem("V004", "Bell Peppers", "vegetable", "1 cup chopped", 30, 1, 7, 0.3, 2.5, 12, 0.5, 211, 6, 157, 120, 0, 0.90),
            FoodItem("V005", "Sweet Potato", "vegetable", "1 medium", 103, 2.3, 24, 0.2, 3.8, 43, 0.8, 448, 72, 19218, 22, 0, 0.60),
            
            # FRUITS
            FoodItem("F001", "Banana", "fruit", "1 medium", 105, 1.3, 27, 0.4, 3.1, 6, 0.3, 422, 1, 76, 10, 0, 0.30),
            FoodItem("F002", "Apple", "fruit", "1 medium", 95, 0.5, 25, 0.3, 4.4, 11, 0.2, 195, 2, 98, 8, 0, 0.40),
            FoodItem("F003", "Orange", "fruit", "1 medium", 62, 1.2, 15, 0.2, 3.1, 52, 0.1, 237, 0, 295, 70, 0, 0.35),
            FoodItem("F004", "Blueberries", "fruit", "1 cup", 84, 1.1, 21, 0.5, 3.6, 9, 0.4, 114, 1, 80, 14, 0, 2.00),
            FoodItem("F005", "Avocado", "fruit", "1/2 medium", 114, 1.3, 6, 10.5, 4.6, 11, 0.4, 345, 5, 108, 6, 0, 1.20),
            
            # DAIRY
            FoodItem("D001", "Milk (2%)", "dairy", "1 cup", 122, 8, 12, 5, 0, 293, 0.1, 366, 100, 395, 0, 120, 0.80),
            FoodItem("D002", "Cheddar Cheese", "dairy", "1 oz", 113, 7, 0.4, 9, 0, 204, 0.2, 28, 176, 300, 0, 12, 0.90),
            FoodItem("D003", "Cottage Cheese", "dairy", "1/2 cup", 110, 14, 4, 5, 0, 69, 0.2, 104, 340, 200, 0, 0, 1.20),
            
            # FATS/OILS
            FoodItem("O001", "Olive Oil", "fat", "1 tbsp", 119, 0, 0, 14, 0, 0, 0.1, 0, 0, 0, 0, 0, 0.40),
            FoodItem("O002", "Almonds", "fat", "1 oz", 164, 6, 6, 14, 3.5, 76, 1.1, 208, 0, 0, 0, 0, 0.70),
            FoodItem("O003", "Peanut Butter", "fat", "2 tbsp", 188, 8, 6, 16, 2, 15, 0.6, 214, 150, 0, 0, 0, 0.50),
        ]
        
        return foods
    
    def get_foods_by_category(self, category: str) -> List[FoodItem]:
        """Get all foods in a specific category"""
        return [f for f in self.foods if f.category == category]
    
    def get_food_by_id(self, food_id: str) -> Optional[FoodItem]:
        """Get a specific food by its ID"""
        for food in self.foods:
            if food.id == food_id:
                return food
        return None

# ==================== MEAL PLANNER ====================
class MealPlanner:
    """Optimizes meal plans based on nutritional requirements and cost"""
    
    def __init__(self):
        self.db = USDAFoodDatabase()
        self.requirements = NutritionalRequirement()
        
    def calculate_nutrition_totals(self, food_items: List[Tuple[FoodItem, float]]) -> Dict[str, float]:
        """Calculate total nutrition for a list of food items with servings"""
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
    
    def meets_requirements(self, nutrition_totals: Dict[str, float]) -> Tuple[bool, List[str]]:
        """Check if nutrition totals meet requirements"""
        meets = True
        deficiencies = []
        
        req_vars = vars(self.requirements)
        
        # Check key nutrients
        nutrients_to_check = [
            ('calories', 'calories'),
            ('protein_g', 'protein_g'),
            ('carbs_g', 'carbs_g'),
            ('fat_g', 'fat_g'),
            ('fiber_g', 'fiber_g'),
            ('calcium_mg', 'calcium_mg'),
            ('iron_mg', 'iron_mg'),
            ('potassium_mg', 'potassium_mg'),
            ('vitamin_a_iu', 'vitamin_a_iu'),
            ('vitamin_c_mg', 'vitamin_c_mg'),
            ('vitamin_d_iu', 'vitamin_d_iu')
        ]
        
        for total_key, req_key in nutrients_to_check:
            if nutrition_totals[total_key] < req_vars[req_key]:
                meets = False
                deficiency = req_vars[req_key] - nutrition_totals[total_key]
                deficiencies.append(f"{req_key}: {deficiency:.1f} more needed")
        
        # Check sodium limit (should not exceed)
        if nutrition_totals['sodium_mg'] > self.requirements.sodium_mg:
            meets = False
            excess = nutrition_totals['sodium_mg'] - self.requirements.sodium_mg
            deficiencies.append(f"sodium_mg: {excess:.1f} over limit")
        
        # Check budget
        if nutrition_totals['price'] > self.requirements.price_limit:
            meets = False
            over_budget = nutrition_totals['price'] - self.requirements.price_limit
            deficiencies.append(f"price: ${over_budget:.2f} over budget")
        
        return meets, deficiencies
    
    def generate_balanced_meal_plan(self) -> Dict:
        """Generate a balanced meal plan using a heuristic approach"""
        
        # Initialize food selections with reasonable defaults
        meal_plan = []
        
        # Breakfast
        meal_plan.append((self.db.get_food_by_id("G003"), 1))  # Oatmeal
        meal_plan.append((self.db.get_food_by_id("D001"), 0.5))  # Milk
        meal_plan.append((self.db.get_food_by_id("F001"), 1))  # Banana
        meal_plan.append((self.db.get_food_by_id("O002"), 0.5))  # Almonds
        
        # Lunch
        meal_plan.append((self.db.get_food_by_id("G001"), 1))  # Brown Rice
        meal_plan.append((self.db.get_food_by_id("P001"), 1.5))  # Chicken Breast
        meal_plan.append((self.db.get_food_by_id("V001"), 2))  # Broccoli
        meal_plan.append((self.db.get_food_by_id("V003"), 0.5))  # Carrots
        
        # Dinner
        meal_plan.append((self.db.get_food_by_id("P005"), 1))  # Black Beans
        meal_plan.append((self.db.get_food_by_id("G002"), 1))  # Whole Wheat Bread
        meal_plan.append((self.db.get_food_by_id("V002"), 3))  # Spinach
        meal_plan.append((self.db.get_food_by_id("F003"), 1))  # Orange
        
        # Snacks
        meal_plan.append((self.db.get_food_by_id("P006"), 1))  # Greek Yogurt
        meal_plan.append((self.db.get_food_by_id("F004"), 0.5))  # Blueberries
        
        # Calculate totals
        nutrition_totals = self.calculate_nutrition_totals(meal_plan)
        meets_req, deficiencies = self.meets_requirements(nutrition_totals)
        
        return {
            'meal_plan': meal_plan,
            'nutrition_totals': nutrition_totals,
            'meets_requirements': meets_req,
            'deficiencies': deficiencies
        }
    
    def optimize_meal_plan(self, iterations: int = 1000) -> Dict:
        """Use a simple optimization algorithm to find a cheaper meal plan"""
        
        best_plan = None
        best_cost = float('inf')
        best_nutrition = None
        
        categories = ['protein', 'grain', 'vegetable', 'fruit', 'dairy', 'fat']
        
        for _ in range(iterations):
            current_plan = []
            
            # Select random foods from each category with random servings
            for category in categories:
                foods_in_category = self.db.get_foods_by_category(category)
                if foods_in_category:
                    # Select 1-2 items from each category
                    num_items = random.randint(1, 2)
                    selected_foods = random.sample(foods_in_category, min(num_items, len(foods_in_category)))
                    
                    for food in selected_foods:
                        servings = random.uniform(0.5, 2.0)
                        current_plan.append((food, servings))
            
            # Calculate nutrition
            nutrition_totals = self.calculate_nutrition_totals(current_plan)
            
            # Check if it meets requirements
            meets_req, _ = self.meets_requirements(nutrition_totals)
            
            # Update best plan if it's cheaper and meets requirements
            if meets_req and nutrition_totals['price'] < best_cost:
                best_cost = nutrition_totals['price']
                best_plan = current_plan
                best_nutrition = nutrition_totals
        
        if best_plan is None:
            # Fall back to balanced plan if optimization fails
            return self.generate_balanced_meal_plan()
        
        meets_req, deficiencies = self.meets_requirements(best_nutrition)
        
        return {
            'meal_plan': best_plan,
            'nutrition_totals': best_nutrition,
            'meets_requirements': meets_req,
            'deficiencies': deficiencies,
            'optimized': True
        }

# ==================== UI & OUTPUT ====================
def print_meal_plan(plan_result: Dict):
    """Print the meal plan in a readable format"""
    
    print("=" * 60)
    print("OPTIMIZED MEAL PLAN FOR 27-YEAR-OLD MALE (164cm)")
    print("=" * 60)
    
    print("\n📋 DAILY MEAL PLAN:")
    print("-" * 40)
    
    meal_plan = plan_result['meal_plan']
    nutrition = plan_result['nutrition_totals']
    
    # Group by category for better display
    categories = {}
    for food, servings in meal_plan:
        if food.category not in categories:
            categories[food.category] = []
        categories[food.category].append((food, servings))
    
    for category, items in categories.items():
        print(f"\n{category.upper()}:")
        for food, servings in items:
            cost = food.price * servings
            print(f"  • {food.name}: {servings:.1f} serving(s)")
            print(f"    Size: {food.serving_size}, Cost: ${cost:.2f}")
    
    print("\n💰 DAILY COST SUMMARY:")
    print("-" * 40)
    print(f"Total Cost: ${nutrition['price']:.2f}")
    print(f"Budget Limit: ${plan_result['requirements'].price_limit:.2f}")
    print(f"Remaining Budget: ${plan_result['requirements'].price_limit - nutrition['price']:.2f}")
    
    print("\n⚖️ NUTRITIONAL SUMMARY:")
    print("-" * 40)
    
    req_vars = vars(plan_result['requirements'])
    
    # Key nutrients to display
    key_nutrients = [
        ('calories', 'Calories'),
        ('protein_g', 'Protein (g)'),
        ('carbs_g', 'Carbs (g)'),
        ('fat_g', 'Fat (g)'),
        ('fiber_g', 'Fiber (g)'),
        ('calcium_mg', 'Calcium (mg)'),
        ('iron_mg', 'Iron (mg)'),
        ('vitamin_c_mg', 'Vitamin C (mg)'),
        ('vitamin_d_iu', 'Vitamin D (IU)')
    ]
    
    for key, label in key_nutrients:
        actual = nutrition[key]
        required = req_vars[key]
        percentage = (actual / required * 100) if required > 0 else 0
        status = "✅" if actual >= required else "❌"
        print(f"{status} {label}: {actual:.1f} / {required:.1f} ({percentage:.1f}%)")
    
    print("\n📊 STATUS:")
    print("-" * 40)
    if plan_result['meets_requirements']:
        print("✅ All nutritional requirements met!")
    else:
        print("❌ Some requirements not met:")
        for deficiency in plan_result['deficiencies']:
            print(f"  - {deficiency}")

class MealPlanApp:
    """Main application class"""
    
    def __init__(self):
        self.planner = MealPlanner()
        
    def run(self):
        """Run the meal planning application"""
        print("\n🍎 MEAL PLANNING APPLICATION")
        print("=" * 60)
        
        while True:
            print("\nOptions:")
            print("1. Generate Balanced Meal Plan")
            print("2. Optimize for Lowest Cost")
            print("3. View Nutritional Requirements")
            print("4. View Available Foods")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                print("\nGenerating balanced meal plan...")
                plan_result = self.planner.generate_balanced_meal_plan()
                plan_result['requirements'] = self.planner.requirements
                print_meal_plan(plan_result)
                
            elif choice == "2":
                print("\nOptimizing for lowest cost (this may take a moment)...")
                plan_result = self.planner.optimize_meal_plan(iterations=500)
                plan_result['requirements'] = self.planner.requirements
                print_meal_plan(plan_result)
                
            elif choice == "3":
                self.print_nutritional_requirements()
                
            elif choice == "4":
                self.print_available_foods()
                
            elif choice == "5":
                print("\nThank you for using the Meal Planning App!")
                break
                
            else:
                print("Invalid choice. Please try again.")
    
    def print_nutritional_requirements(self):
        """Print the nutritional requirements"""
        req = self.planner.requirements
        print("\n📋 NUTRITIONAL REQUIREMENTS (27-year-old male, 164cm):")
        print("-" * 50)
        
        requirements = [
            ("Calories", f"{req.calories:.0f} kcal"),
            ("Protein", f"{req.protein_g:.1f} g"),
            ("Carbohydrates", f"{req.carbs_g:.1f} g"),
            ("Fat", f"{req.fat_g:.1f} g"),
            ("Fiber", f"{req.fiber_g:.1f} g"),
            ("Calcium", f"{req.calcium_mg:.0f} mg"),
            ("Iron", f"{req.iron_mg:.1f} mg"),
            ("Potassium", f"{req.potassium_mg:.0f} mg"),
            ("Sodium (max)", f"{req.sodium_mg:.0f} mg"),
            ("Vitamin A", f"{req.vitamin_a_iu:.0f} IU"),
            ("Vitamin C", f"{req.vitamin_c_mg:.0f} mg"),
            ("Vitamin D", f"{req.vitamin_d_iu:.0f} IU"),
            ("Daily Budget", f"${req.price_limit:.2f}")
        ]
        
        for nutrient, value in requirements:
            print(f"  {nututrient:<20} {value}")
    
    def print_available_foods(self):
        """Print all available foods in the database"""
        print("\n📦 AVAILABLE FOODS:")
        print("-" * 80)
        
        categories = {}
        for food in self.planner.db.foods:
            if food.category not in categories:
                categories[food.category] = []
            categories[food.category].append(food)
        
        for category, foods in categories.items():
            print(f"\n{category.upper()}:")
            for food in foods:
                print(f"  • {food.name:20} ${food.price:5.2f}  {food.serving_size:15} "
                      f"{food.calories:5.0f} kcal")

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    app = MealPlanApp()
    app.run()
