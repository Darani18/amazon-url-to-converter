import tkinter as tk
from tkinter import ttk, messagebox
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Function to extract product price from Amazon using Selenium
def get_product_price(url):
    try:
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920x1080")  # Ensure all elements load

        # Setup WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        # Allow time for the page to load
        time.sleep(3)

        try:
            # Locate price element (Amazon’s structure may vary)
            price = None
            
            # Try the most common price container
            try:
                price = driver.find_element(By.CLASS_NAME, "a-price-whole").text
                fraction = driver.find_element(By.CLASS_NAME, "a-price-fraction").text
                price = f"{price}.{fraction}"
            except:
                pass
            
            # Alternative method (sometimes prices are in "a-offscreen" class)
            if not price:
                try:
                    price = driver.find_element(By.CLASS_NAME, "a-offscreen").text
                except:
                    pass

            # Clean up price formatting
            driver.quit()
            
            if price:
                return float(price.replace(",", "").replace("$", "").strip())
            else:
                messagebox.showerror("Error", "Price not found. Try another URL.")
                return None

        except Exception as e:
            driver.quit()
            messagebox.showerror("Error", f"Failed to extract price: {e}")
            return None

    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch WebDriver: {e}")
        return None

# Function to fetch exchange rates
def get_exchange_rate(to_currency):
    try:
        api_url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            return data['rates'].get(to_currency, None)
        else:
            messagebox.showerror("Error", "Failed to fetch exchange rates.")
            return None
    except Exception as e:
        messagebox.showerror("Error", f"Exchange rate fetch failed: {e}")
        return None

# Function to get price, convert, and display the result
def convert_currency():
    url = entry_url.get().strip()
    to_currency = currency_var.get()

    if not url.startswith("https://www.amazon."):
        messagebox.showwarning("Input Error", "Please enter a valid Amazon product URL.")
        return

    product_price = get_product_price(url)
    if product_price:
        rate = get_exchange_rate(to_currency)
        if rate:
            converted_price = product_price * rate
            result_label.config(text=f"Converted Price: {converted_price:.2f} {to_currency}")
        else:
            result_label.config(text="Exchange rate not available.")
    else:
        result_label.config(text="Could not extract product price.")

# GUI Setup
root = tk.Tk()
root.title("Product Price Converter")
root.geometry("500x400")
root.resizable(False, False)

# Create a gradient background using Canvas
canvas = tk.Canvas(root, width=500, height=400)
canvas.pack(fill="both", expand=True)

gradient = tk.PhotoImage(width=1, height=400)
for i in range(400):
    color = f"#{int(255 - (i / 400) * 100):02x}{int(180 - (i / 400) * 50):02x}{255:02x}"
    gradient.put(color, (0, i))

canvas.create_image(0, 0, image=gradient, anchor="nw")

# Main Frame
frame = tk.Frame(root, bg="#f0f0f0", bd=2, relief="ridge")
frame.place(relx=0.5, rely=0.5, anchor="center", width=460, height=320)

# Title Label
title_label = tk.Label(frame, text="Amazon product price Converter", font=("Arial", 14, "bold"), bg="#f0f0f0")
title_label.pack(pady=10)

# Product URL Entry
input_frame = tk.Frame(frame, bg="#f0f0f0")
input_frame.pack(pady=10)

url_label = tk.Label(input_frame, text="Product URL:", font=("Arial", 12), bg="#f0f0f0")
url_label.grid(row=0, column=0, padx=5)

entry_url = tk.Entry(input_frame, font=("Arial", 12), width=30, relief="solid", bd=1)
entry_url.grid(row=0, column=1, padx=5)

# Currency Selection Dropdown
currency_label = tk.Label(frame, text="Select Target Currency:", font=("Arial", 12), bg="#f0f0f0")
currency_label.pack()

currency_var = tk.StringVar(value="INR")
currency_dropdown = ttk.Combobox(frame, textvariable=currency_var, 
                                 values=["INR", "EUR", "GBP", "JPY", "AUD", "CAD", "CNY"], 
                                 state="readonly", width=10)
currency_dropdown.pack(pady=5)

# Convert Button
convert_button = tk.Button(frame, text="Convert", command=convert_currency, font=("Arial", 12), bg="#4CAF50", fg="purple", relief="raised")
convert_button.pack(pady=10)

# Result Label
result_label = tk.Label(frame, text="Converted Price: -", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#333")
result_label.pack(pady=10)

# Run GUI
root.mainloop()
