import requests

# Test the debug database endpoint
response = requests.get("https://ttprov4-k58o.onrender.com/debug/database")
print("Database Debug Status:")
print(response.json())