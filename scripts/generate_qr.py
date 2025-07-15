import os
import qrcode
import json

# Functions to generate QR codes from a JSON file
# Required: 
# - Run `pip install qrcode pillow`
# - Ensure data.json exists in the same directory with the required format

def get_json_data():
    file_path = "data.json"
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def generate_qr(url: str, id: str):
    current_directory = os.getcwd()
    filename = f"{id}.png"
    file_path = os.path.join(current_directory, "qr", filename)
    img = qrcode.make(url)
    img.save(file_path)

def generate_qr_codes():
    telegram_url = "https://t.me/orc4bikes_bot"
    for id in get_json_data():
        url = f"{telegram_url}?start=qr_{id}"
        print(f"Generating QR for {url}...")
        generate_qr(url, id)
        print(f"QR generated for {url}!")
        print("========================")

generate_qr_codes()

