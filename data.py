import random # Used for mocking a sale ID
import time # Used for mocking a sale ID
from datetime import datetime

class DatabaseManager:
    """
    A mock class to simulate database operations.
    In a real application, this would connect to a database
    and perform actual queries.
    """
    def start_new_sale(self):
        """Simulates creating a new sale record in the database."""
        # Generates a random, unique ID for the new sale
        sale_id = f"{int(time.time())}-{random.randint(100, 999)}"
        print(f"NEW SALE: started with ID: {sale_id}")
        return sale_id

class AppData:
    """
    A shared data hub for the entire application.
    This object will hold all state that needs to be accessed
    by different windows and screens.
    """
    def __init__(self):
        self.db = DatabaseManager()
        self.db_name = "database.py"
        self.curr_sale_id = None
        self.curr_customer_name = ""
