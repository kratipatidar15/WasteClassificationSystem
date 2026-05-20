RECYCLING_RULES = {
    "battery": {
        "category": "Hazardous/E-waste",
        "suggestion": "Do NOT throw in regular trash. Take to an authorized e-waste disposal facility or battery recycling drop-off."
    },
    "biological": {
        "category": "Organic",
        "suggestion": "Compost this waste or place it in the organic/green bin."
    },
    "brown-glass": {
        "category": "Glass",
        "suggestion": "Recycle separately. Ensure it is empty and clean before placing in the glass recycling bin."
    },
    "green-glass": {
        "category": "Glass",
        "suggestion": "Recycle separately. Ensure it is empty and clean before placing in the glass recycling bin."
    },
    "white-glass": {
        "category": "Glass",
        "suggestion": "Recycle separately. Ensure it is empty and clean before placing in the glass recycling bin."
    },
    "cardboard": {
        "category": "Paper/Cardboard",
        "suggestion": "Flatten and place in the paper recycling bin. Keep it dry."
    },
    "paper": {
        "category": "Paper",
        "suggestion": "Recyclable. Keep it dry and place in the paper recycling bin."
    },
    "clothes": {
        "category": "Textile",
        "suggestion": "If in good condition, consider donating. Otherwise, use a specialized textile recycling drop-off."
    },
    "shoes": {
        "category": "Textile/Apparel",
        "suggestion": "If in good condition, consider donating. Otherwise, dispose of in specialized apparel bins."
    },
    "metal": {
        "category": "Metal",
        "suggestion": "Recyclable. Rinse out if it contained food/liquid, then place in the metal/plastic recycling bin."
    },
    "plastic": {
        "category": "Plastic",
        "suggestion": "Recyclable. Ensure it is empty and clean before recycling."
    },
    "trash": {
        "category": "General Waste",
        "suggestion": "Non-recyclable. Dispose of in the regular trash bin."
    }
}

def get_recycling_info(class_name):
    # Fallback for unknown classes
    return RECYCLING_RULES.get(class_name, {
        "category": "Unknown",
        "suggestion": "Please check your local recycling guidelines."
    })
