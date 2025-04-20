from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum
import json
from datetime import datetime
from pydantic_ai import Agent, RunContext
import requests
from bs4 import BeautifulSoup
import random

class ItemSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    available_sizes: Optional[List[ItemSize]] = None
    is_available: bool = True

class OrderItem(BaseModel):
    menu_item: MenuItem
    quantity: int = 1
    size: Optional[ItemSize] = None
    special_instructions: Optional[str] = None

class Order(BaseModel):
    id: str
    items: List[OrderItem] = []
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "in_progress"
    total: float = 0.0

    def calculate_total(self) -> float:
        total = 0.0
        for item in self.items:
            total += item.menu_item.price * item.quantity
        return total

class MenuScraper:
    def __init__(self):
        self.base_url = "https://www.mcdonalds.com/us/en-us/full-menu.html"
        self.menu_data = {}
        self.categories = {
            "Featured Favorites": [],
            "Breakfast": [],
            "Burgers": [],
            "Chicken & Fish Sandwiches": [],
            "McNuggets": [],
            "Fries & Sides": [],
            "Happy Meal": [],
            "McCafé Coffees": [],
            "Sweets & Treats": [],
            "Beverages": []
        }

    def scrape_menu(self) -> Dict[str, MenuItem]:
        try:
            response = requests.get(self.base_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all menu categories
            for category_name in self.categories.keys():
                category_section = soup.find('h2', string=category_name)
                if category_section:
                    items = category_section.find_next('ul').find_all('li')
                    for item in items:
                        item_name = item.text.strip()
                        if item_name:
                            # Generate a unique ID
                            item_id = f"{category_name[:3]}_{len(self.menu_data) + 1}"
                            
                            # Generate a random price based on category
                            base_price = self._get_base_price(category_name)
                            price = round(base_price + random.uniform(0, 2), 2)
                            
                            # Create menu item
                            menu_item = MenuItem(
                                id=item_id,
                                name=item_name,
                                description=self._generate_description(item_name, category_name),
                                price=price,
                                category=category_name,
                                available_sizes=self._get_available_sizes(category_name)
                            )
                            
                            self.menu_data[item_id] = menu_item
                            self.categories[category_name].append(menu_item)
            
            return self.menu_data
        except Exception as e:
            print(f"Error scraping menu: {e}")
            return {}

    def _get_base_price(self, category: str) -> float:
        # Base prices for different categories
        prices = {
            "Featured Favorites": 5.99,
            "Breakfast": 4.99,
            "Burgers": 5.49,
            "Chicken & Fish Sandwiches": 5.99,
            "McNuggets": 4.99,
            "Fries & Sides": 2.99,
            "Happy Meal": 4.49,
            "McCafé Coffees": 3.99,
            "Sweets & Treats": 2.99,
            "Beverages": 1.99
        }
        return prices.get(category, 4.99)

    def _generate_description(self, name: str, category: str) -> str:
        # Generate simple descriptions based on category
        descriptions = {
            "Burgers": f"A delicious {name} with fresh ingredients",
            "Breakfast": f"A satisfying {name} to start your day",
            "Beverages": f"Refreshing {name}",
            "Sweets & Treats": f"Sweet and tasty {name}",
            "McCafé Coffees": f"Premium {name} made with quality ingredients",
            "Fries & Sides": f"Crispy and golden {name}",
            "Chicken & Fish Sandwiches": f"Tender and flavorful {name}",
            "McNuggets": f"Tender and juicy {name}",
            "Happy Meal": f"Fun {name} for kids",
            "Featured Favorites": f"Popular {name} that customers love"
        }
        return descriptions.get(category, f"Tasty {name}")

    def _get_available_sizes(self, category: str) -> Optional[List[ItemSize]]:
        # Items that typically have size options
        sized_items = ["Beverages", "McCafé Coffees", "Fries & Sides"]
        return [ItemSize.SMALL, ItemSize.MEDIUM, ItemSize.LARGE] if category in sized_items else None

class DriveThruAI:
    def __init__(self):
        self.menu_scraper = MenuScraper()
        self.menu = self.menu_scraper.scrape_menu()
        self.current_order = None
        self.orders_history = []

    def refresh_menu(self) -> None:
        """Refresh the menu data from the website"""
        self.menu = self.menu_scraper.scrape_menu()

    def start_new_order(self) -> Order:
        self.current_order = Order(id=f"order_{len(self.orders_history) + 1}")
        return self.current_order

    def add_item_to_order(self, item_id: str, quantity: int = 1, size: Optional[ItemSize] = None, 
                         special_instructions: Optional[str] = None) -> bool:
        if not self.current_order:
            return False

        if item_id not in self.menu:
            return False

        menu_item = self.menu[item_id]
        if menu_item.available_sizes and size not in menu_item.available_sizes:
            return False

        order_item = OrderItem(
            menu_item=menu_item,
            quantity=quantity,
            size=size,
            special_instructions=special_instructions
        )
        self.current_order.items.append(order_item)
        self.current_order.total = self.current_order.calculate_total()
        return True

    def remove_item_from_order(self, item_index: int) -> bool:
        if not self.current_order or item_index >= len(self.current_order.items):
            return False

        self.current_order.items.pop(item_index)
        self.current_order.total = self.current_order.calculate_total()
        return True

    def checkout(self) -> bool:
        if not self.current_order or not self.current_order.items:
            return False

        self.current_order.status = "completed"
        self.orders_history.append(self.current_order)
        self.current_order = None
        return True

    def get_menu(self) -> Dict[str, MenuItem]:
        return self.menu

    def get_current_order(self) -> Optional[Order]:
        return self.current_order

    def get_order_history(self) -> List[Order]:
        return self.orders_history

# Create the agent
drive_thru_agent = Agent(
    'openai:gpt-4',
    deps_type=DriveThruAI,
    output_type=str,
    system_prompt=(
        "You are a friendly McDonald's drive-thru AI assistant. "
        "Your job is to help customers place their orders using the actual McDonald's menu. "
        "You can show the menu, add items to orders, remove items, and process checkouts. "
        "Always be polite and helpful. "
        "If a customer asks for something not on the menu, politely inform them it's not available. "
        "When showing the menu, format it nicely with categories and prices. "
        "When confirming orders, always repeat the order back to the customer with prices. "
        "You have access to the full McDonald's menu with all categories and items."
    )
)

@drive_thru_agent.tool
async def show_menu(ctx: RunContext[DriveThruAI]) -> str:
    """Show the current menu with all available items"""
    menu_text = "Here's our menu:\n\n"
    
    for category, items in ctx.deps.menu_scraper.categories.items():
        if items:  # Only show categories that have items
            menu_text += f"{category.upper()}:\n"
            for item in items:
                menu_text += f"- {item.name}: ${item.price:.2f}\n"
                if item.available_sizes:
                    menu_text += "  Available sizes: " + ", ".join(size.value for size in item.available_sizes) + "\n"
            menu_text += "\n"
    
    menu_text += "\nTo order, you can say things like:\n"
    menu_text += "- 'I'd like a Big Mac and a large fries'\n"
    menu_text += "- 'Can I get a medium Coke?'\n"
    menu_text += "- 'Add a Quarter Pounder to my order'\n"
    menu_text += "- 'I want a sausage biscuit with egg and a milk'\n"
    menu_text += "\nI'll ask you for any missing details like size or specific type of item.\n"
    
    return menu_text

@drive_thru_agent.tool
async def add_to_order(ctx: RunContext[DriveThruAI], item_name: str, quantity: int = 1, 
                      size: Optional[ItemSize] = None, special_instructions: Optional[str] = None) -> str:
    """Add an item to the current order"""
    if not ctx.deps.current_order:
        ctx.deps.start_new_order()
    
    # Find the item by name (case-insensitive and with fuzzy matching)
    item_id = None
    best_match = None
    best_score = 0
    
    # Clean up the input name
    input_name = item_name.lower().strip()
    input_name = input_name.replace(" and ", " & ")
    input_name = input_name.replace(" with ", " w/ ")
    input_name = input_name.replace(" meal", "")  # Remove "meal" from input
    
    for id, item in ctx.deps.menu.items():
        # Clean up the menu item name
        menu_name = item.name.lower()
        menu_name = menu_name.replace(" and ", " & ")
        menu_name = menu_name.replace(" with ", " w/ ")
        menu_name = menu_name.replace(" meal", "")  # Remove "meal" from menu item
        
        # Check for exact match
        if input_name == menu_name:
            item_id = id
            break
            
        # Check for partial match
        if input_name in menu_name or menu_name in input_name:
            # Calculate a simple matching score
            score = len(set(input_name.split()) & set(menu_name.split()))
            if score > best_score:
                best_score = score
                best_match = id
    
    # If no exact match, use the best partial match
    if not item_id and best_match:
        item_id = best_match
    
    if not item_id:
        return f"Sorry, I couldn't find '{item_name}' on the menu. Please check the menu and try again."
    
    menu_item = ctx.deps.menu[item_id]
    
    # Check for ambiguous items
    if "milk" in menu_item.name.lower():
        return "I see you want milk. Would you like 1% Low Fat Milk Jug or Reduced Sugar Low Fat Chocolate Milk Jug?"
    
    if "coffee" in menu_item.name.lower():
        return "I see you want coffee. Would you like regular McCafé Premium Roast Coffee or one of our specialty drinks?"
    
    # Check if size is needed but not specified
    if menu_item.available_sizes and not size:
        size_options = ", ".join(size.value for size in menu_item.available_sizes)
        return f"I see you want {menu_item.name}. What size would you like? Available sizes: {size_options}"
    
    success = ctx.deps.add_item_to_order(item_id, quantity, size, special_instructions)
    if success:
        size_text = f" ({size.value})" if size else ""
        return f"Added {quantity}x {menu_item.name}{size_text} to your order"
    return "Sorry, I couldn't add that item to your order"

@drive_thru_agent.tool
async def remove_from_order(ctx: RunContext[DriveThruAI], item_name: str, quantity: int = 1) -> str:
    """Remove an item from the current order"""
    if not ctx.deps.current_order or not ctx.deps.current_order.items:
        return "Your order is currently empty."
    
    # Find the item in the current order
    items_to_remove = []
    for i, order_item in enumerate(ctx.deps.current_order.items):
        if item_name.lower() in order_item.menu_item.name.lower():
            items_to_remove.append(i)
    
    if not items_to_remove:
        return f"Sorry, I couldn't find '{item_name}' in your current order."
    
    # Remove the specified number of items
    removed_count = 0
    for i in sorted(items_to_remove, reverse=True):
        if removed_count < quantity:
            ctx.deps.current_order.items.pop(i)
            removed_count += 1
    
    ctx.deps.current_order.total = ctx.deps.current_order.calculate_total()
    return f"Removed {removed_count}x {item_name} from your order"

@drive_thru_agent.tool
async def show_current_order(ctx: RunContext[DriveThruAI]) -> str:
    """Show the current order with all items and total"""
    order = ctx.deps.get_current_order()
    if not order or not order.items:
        return "Your order is currently empty"
    
    order_text = "Your current order:\n"
    for item in order.items:
        order_text += f"- {item.quantity}x {item.menu_item.name}"
        if item.size:
            order_text += f" ({item.size.value})"
        if item.special_instructions:
            order_text += f" - {item.special_instructions}"
        order_text += f": ${item.menu_item.price * item.quantity:.2f}\n"
    
    order_text += f"\nTotal: ${order.total:.2f}"
    return order_text

@drive_thru_agent.tool
async def checkout_order(ctx: RunContext[DriveThruAI]) -> str:
    """Process the checkout for the current order"""
    if ctx.deps.checkout():
        return "Thank you for your order! Your order has been completed. Please pull forward to the next window."
    return "Sorry, I couldn't process your checkout. Your order might be empty."

async def main():
    drive_thru = DriveThruAI()
    
    print("Welcome to McDonald's AI Drive-Thru!")
    print("I'll fetch the latest menu for you...")
    drive_thru.refresh_menu()  # Ensure we have the latest menu
    print("Menu loaded! You can ask me to show the menu, add items to your order, or checkout.")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'quit':
            break
            
        result = await drive_thru_agent.run(user_input, deps=drive_thru)
        print("\nAssistant:", result.output)
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 