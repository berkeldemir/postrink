import random
import time
import sqlite3
from datetime import datetime

class DatabaseManager:
	"""
	A mock class to simulate database operations.
	In a real application, this would connect to a database
	and perform actual queries.
	"""
	def __init__(self):
		self.conn = None
		self.db_name = 'database.db'
		self.connect()

	def connect(self):
		try:
			self.conn = sqlite3.connect(self.db_name)
			self.conn.row_factory = sqlite3.Row
			print("DATABASE: Successfully connected.")
		except sqlite3.Error as e:
			print(f"DATABASE: Connection failed: {e}")

	def close(self):
		if self.conn:
			self.conn.close()
			print("DATABASE: Connection closed.")

	def start_new_sale(self, customer_name):
		# Generates a random, unique ID for the new sale
		sale_id = f"{int(time.time())}-{random.randint(100, 999)}"
		sale_date = datetime.now().isoformat()

		try:
			cursor = self.conn.cursor()
			cursor.execute(
				"""
				INSERT INTO sales (sale_id, sale_date, customer_name, total_discount_perc, total_discount_num, total_amount, payment_method)
				VALUES (?, ?, ?, ?, ?, ?, ?)
				""", (sale_id, sale_date, customer_name, 0, 0.0, 0.0, "WIP"))
			self.conn.commit()
			print(f"NEW SALE: {sale_id} | {customer_name}")
			return sale_id
		except sqlite3.Error as e:
			print(f"ERROR   : sqlite3 error: {e}")
			return None

	def get_all_products(self):
		try:
			cursor = self.conn.cursor()
			cursor.execute("SELECT * FROM items")
			return cursor.fetchall()
		except sqlite3.Error as e:
			print(f"ERROR   : sqlite3 error: {e}")
			return []

	def get_sale_products(self, sale_id):
		try:
			cursor = self.conn.cursor()
			# Correcting the query to use a placeholder instead of a literal string
			cursor.execute("""
				SELECT * FROM cart_items WHERE sale_id = ?
				""", (sale_id, ))
		except sqlite3.Error as e:
			print(f"ERROR   : sqlite3 error: {e}")

	def total_amount_calculator(self, sale_id):
		try:
			cursor_total = self.conn.cursor()
			cursor_total.execute("""
				SELECT item_total FROM cart_items WHERE sale_id = ?
				""", (sale_id, ))
			item_total_tuple = cursor_total.fetchall()
			if not item_total_tuple:
				return 0
			total = 0
			for i in item_total_tuple:
				total = total + i[0]
			return total
		except Exception as e:
			print(f"ERROR   : {e}")
			self.conn.rollback()
			return 0

	def total_discount_num(self, sale_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT total_discount_num
				FROM sales
				WHERE sale_id = ?
			""", (sale_id,))
			row = cursor.fetchone()
			return row[0] if row else 0
		except Exception as e:
			print(f"ERROR   : {e}")
			self.conn.rollback()
			return 0

	def add_item_to_cart(self, sale_id, item_id, item_count, item_discount_perc, item_discount_num):
		try:
			cur = self.conn.cursor()
			cur.execute("""
				SELECT ci.item_count, ci.item_total, i.item_price
				FROM cart_items ci
				JOIN items i ON ci.item_id = i.item_id
				WHERE ci.sale_id = ? AND ci.item_id = ?
			""", (sale_id, item_id))
			row = cur.fetchone()

			if row:
				new_count = row[0] + item_count
				new_total = row[1] + (item_count * row[2])
				cur.execute("""
					UPDATE cart_items
					SET item_count = ?,
						item_total = ?
					WHERE sale_id = ? AND item_id = ?
				""", (new_count, new_total, sale_id, item_id))
				self.conn.commit()  # <-- missing before
				return True

			# insert path (unchanged)
			cur.execute("""SELECT item_price FROM items WHERE item_id = ?""", (item_id,))
			price_row = cur.fetchone()
			if not price_row:
				print(f"ERROR:   Item ID not found: {item_id}")
				return False

			base_price = price_row[0]
			line_total = base_price
			if item_discount_perc:
				line_total = line_total * (100 - item_discount_perc) / 100.0
			if item_discount_num:
				line_total = line_total - item_discount_num

			cur.execute("""
				INSERT INTO cart_items (sale_id, item_id, item_count, item_discount_perc, item_discount_num, item_total)
				VALUES (?, ?, ?, ?, ?, ?)
			""", (sale_id, item_id, item_count, item_discount_perc, item_discount_num, line_total * item_count))
			self.conn.commit()
			return True
		except Exception as e:
			print(f"ERROR   : {e}")
			self.conn.rollback()
			return False

	def apply_discounts(self, sale_id):
		"""
		Recalculate discounts row-by-row from base price (item_price * count),
		write item_discount_* and item_total (net), then update sales.* totals.
		"""
		try:
			cur = self.conn.cursor()

			# 1) Recompute each cart row from base values so discounts don’t compound
			cur.execute("""
				SELECT ci.item_id, ci.item_count, i.item_price
				FROM cart_items ci
				JOIN items i ON i.item_id = ci.item_id
				WHERE ci.sale_id = ?
			""", (sale_id,))
			rows = cur.fetchall()

			for item_id, item_count, item_price in rows:
				base_total = (item_price or 0) * (item_count or 0)

				# fetch best (or only) campaign; if you may have many, pick the best here
				cur.execute("""
					SELECT disc_type, disc_val, min_quan
					FROM campaigns
					WHERE item_id = ?
					AND min_quan <= ?
					ORDER BY min_quan DESC
					LIMIT 1
				""", (item_id, item_count))
				camp = cur.fetchone()

				discount_num = 0.0
				discount_perc = 0.0
				if camp and item_count >= camp["min_quan"]:
					if camp["disc_type"] == "percent":
						discount_num = base_total * (camp["disc_val"] / 100.0)
						discount_perc = camp["disc_val"]
					elif camp["disc_type"] == "fixed":
						discount_num = min(base_total, camp["disc_val"])  # don’t go negative
						discount_perc = (discount_num / base_total * 100.0) if base_total > 0 else 0.0

				new_total = max(0.0, base_total - discount_num)

				cur.execute("""
					UPDATE cart_items
					SET item_discount_perc = ?,
						item_discount_num  = ?,
						item_total         = ?
					WHERE sale_id = ? AND item_id = ?
				""", (discount_perc, discount_num, new_total, sale_id, item_id))

			# 2) Write aggregated totals into sales so your "İNDİRİM:" label reflects reality
			cur.execute("""
				SELECT COALESCE(SUM(item_discount_num), 0.0),
					COALESCE(SUM(item_total), 0.0)
				FROM cart_items
				WHERE sale_id = ?
			""", (sale_id,))
			disc_sum, total_sum = cur.fetchone() or (0.0, 0.0)

			cur.execute("""
				UPDATE sales
				SET total_discount_num = ?,
					total_amount       = ?
				WHERE sale_id = ?
			""", (disc_sum, total_sum, sale_id))

			self.conn.commit()
		except Exception as e:
			print(f"ERROR   : Applying discounts: {e}")
			self.conn.rollback()


	def get_cart_items(self, sale_id):
		try:
			# Apply first, then fetch
			self.apply_discounts(sale_id)

			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT
					ci.item_count,
					i.item_name,
					ci.item_discount_perc,
					ci.item_discount_num,
					ci.item_total
				FROM cart_items AS ci
				JOIN items  AS i  ON ci.item_id = i.item_id
				WHERE ci.sale_id = ?
			""", (sale_id,))
			return cursor.fetchall()
		except Exception as e:
			print(f"ERROR   : Fetching cart items: {e}")
			return []


	def remove_item_from_cart(self, sale_id, i):
		try:
			cart_items = get_cart_items(sale_id)
			cursor = self.conn.cursor()
			cursor.execute("""
				DELETE FROM cart_items
				WHERE cart_items_id = ?
			""", (cart_items[i][0], ))
			self.conn.commit()
			return True
		except Exception as e:
				print(f"ERROR   : Removing selected cart item: {e}")
				return False
	
	def remove_cart_of_sale(self, sale_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				DELETE FROM cart_items
				WHERE sale_id = ?
			""", (sale_id, ))
			self.conn.commit()
			cursor = self.conn.cursor()
			cursor.execute("""
				DELETE FROM sales
				WHERE sale_id = ?
			""", (sale_id, ))
			self.conn.commit()
		except Exception as e:
			print(f"ERROR   : Removing cart of sale: {e}")
	def	onhold_orders(self):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT *
				FROM sales
				WHERE payment_method = "WIP"
			""")
			return (cursor.fetchall())
		except Exception as e:
			print(f"ERROR   : Getting onhold orders' list: {e}")

	def calculate_cart_discount(self, sale_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT item_id, item_count
				FROM cart_items
				WHERE sale_id = ?
			""", (sale_id,))
			
			cart_items = cursor.fetchall()
			total_discount = 0
			
			for item_id, count in cart_items:
				discount = self.get_applicable_discount(item_id, count)
				total_discount += discount
			
			return total_discount
		except Exception as e:
			print(f"ERROR in calculate_cart_discount: {e}")
			return 0

class AppData:
	def __init__(self):
		self.database_manager = DatabaseManager()
		self.curr_sale_id = None
		self.curr_customer_name = ""
