import os
import requests
from dotenv import load_dotenv

# Load environment variables (API key for Nutritionix)
load_dotenv()
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY")
NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")

BASE_URL = "https://trackapi.nutritionix.com/v2"

def get_food_info(food_name):
    """
    Queries Nutritionix API to fetch detailed nutritional information about a food item.
    """
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_API_KEY,
    }
    params = {"query": food_name}
    
    try:
        response = requests.get(f"https://trackapi.nutritionix.com/v2//natural/nutrients", headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def format_food_info(food_data):
    """
    Formats the food data response from Nutritionix API into a user-friendly string.
    """
    if "error" in food_data:
        return f"Error fetching food data: {food_data['error']}"
    
    try:
        food = food_data["foods"][0]
        name = food["food_name"]
        calories = food["nf_calories"]
        protein = food["nf_protein"]
        fat = food["nf_total_fat"]
        carbs = food["nf_total_carbohydrate"]
        
        return (
            f"Food: {name}\n"
            f"Calories: {calories} kcal\n"
            f"Protein: {protein} g\n"
            f"Fat: {fat} g\n"
            f"Carbohydrates: {carbs} g"
        )
    except (KeyError, IndexError):
        return "Could not parse the food data. Please try a different query."
