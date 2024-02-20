import json

sample_items = [
    {"name": "jacket", "category": "fashion"},
]

# Create a dictionary with the items
items_dict = {"items": sample_items}

# Write the dictionary to items.json
with open('items.json', 'w') as file:
    json.dump(items_dict, file, indent=4)

