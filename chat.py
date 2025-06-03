import json
import os

# Global variable to store the last district discussed
last_location = None

def load_transport_data(state):
    """Load transport data for a specific state from the corresponding JSON file."""
    file_path = os.path.join("transport", f"{state.lower()}.json")
    
    if not os.path.exists(file_path):
        return {"error": f"❌ **{state} ka transport data file nahi mila**. Agar yeh issue bar bar ho raha hai, Vishal ko batayein."}
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {"error": "❌ **Error reading transport data file**. Yeh issue Vishal ko batayein."}

def get_location_info(place):
    """Find district and state of the given place."""
    global last_location
    state_district_map = {
        "jaipur": "rajasthan",
        "jodhpur": "rajasthan",
        "ahmedabad": "gujarat"
    }

    # Determine the state based on the city (place)
    if place.lower() not in state_district_map:
        return f"❌ **{place} ka location data nahi mila**. Agar yeh issue bar bar ho raha hai, Vishal ko batayein."
    
    state = state_district_map[place.lower()]
    data = load_transport_data(state)
    
    if "error" in data:
        return data["error"]
    
    last_location = (place, state)
    return f"📍 **{place.capitalize()}**, {state.capitalize()} me aata hai. Aapko kis cheez ki jankari chahiye? Transport, Charges, Delivery Time?"

def get_district_data(query_type):
    """Fetch specific details (transport names, charges, delivery time) based on query type."""
    global last_location
    
    if not last_location:
        return "❌ **Pehle location ka naam batao.**"
    
    place, state = last_location
    data = load_transport_data(state)
    
    if "error" in data:
        return data["error"]
    
    # Fetch transport info for the given district and state
    transport_info = data.get(place.capitalize(), {}).get("transport", {})
    
    if not transport_info:
        return f"❌ **{place.capitalize()} ka transport data nahi mila**. Agar yeh issue bar bar ho raha hai, Vishal ko batayein."
    
    # Handling different query types (transport, charge, delivery)
    if query_type == "transport":
        response = f"🚚 **{place.capitalize()} me available transport services:**\n"
        for name in transport_info:
            response += f"   - **{name}**\n"
        return response
    
    elif query_type == "charge":
        response = f"💰 **{place.capitalize()} ke transport charges:**\n"
        for name, details in transport_info.items():
            response += f"   - **{name}**: ₹{details.get('charge', 'N/A')}\n"
        return response
    
    elif query_type == "delivery":
        response = f"⏳ **{place.capitalize()} ka estimated delivery time:**\n"
        for name, details in transport_info.items():
            response += f"   - **{name}**: {details.get('delivery_time', 'N/A')}\n"
        return response
    
    return "❌ **Invalid query type**. Agar yeh issue bar bar ho raha hai, Vishal ko batayein."

def chatbot_response(user_message):
    """Process user message and return chatbot response."""
    global last_location
    user_message = user_message.lower()

    # Check if user is asking for location
    if "location" in user_message or "kahan" in user_message or "kaha hai" in user_message:
        city_names = ["jaipur", "jodhpur", "ahmedabad"]
        for city in city_names:
            if city in user_message:
                return get_location_info(city)

    # If location is provided, handle transport, charge, or delivery queries
    if last_location:
        if "transport" in user_message:
            return get_district_data("transport")
        
        if "charge" in user_message or "kitna paisa" in user_message:
            return get_district_data("charge")
        
        if "delivery" in user_message or "time lagega" in user_message:
            return get_district_data("delivery")
    
    # Default response if no valid query is detected
    return "❌ **Sorry, samajh nahi aaya.** Kya aap location ya transport ka data chahte hain?"
