import pandas as pd
import time
import subprocess
import pyautogui
import pyperclip
import random

# Function to load customer data from Excel file
def load_customers(file_path):
    print("Loading customer data from", file_path)
    df = pd.read_excel(file_path)  # Reading data from the Excel file
    
    # Check if 'MessageStatus' column exists, if not, add it with default 'नहीं'
    if 'MessageStatus' not in df.columns:
        print("'MessageStatus' column not found. Adding it with default value 'नहीं'.")
        df['MessageStatus'] = 'नहीं'  # Add the column with 'नहीं' as default value
        
    return df  # Return the DataFrame to preserve status columns

# Function to send WhatsApp message using desktop app
def send_whatsapp_message(contact_number, message):
    try:
        # Prepare WhatsApp URL for the number
        url = f"whatsapp://send?phone={contact_number}"

        # Open the WhatsApp application using subprocess
        subprocess.Popen(["start", url], shell=True)
        time.sleep(5)  # Wait for WhatsApp to open

        # Copy the message to clipboard using pyperclip
        pyperclip.copy(message)

        # Simulate CTRL+V to paste the message in the message box
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)

        # Press Enter to send the message
        pyautogui.press('enter')
        print(f"Message sent to {contact_number}")
        return True
    except Exception as e:
        print(f"Error: Unable to send message to {contact_number} - {e}")
        return False

# Function to process each customer's multiple numbers
def send_bulk_messages(customers_df, message_template, company_name):
    sent_numbers = set()  # Track numbers to prevent duplicates
    invalid_numbers = []  # List to track invalid numbers

    print("Starting to send messages to customers...")

    # Loop through all customers and their numbers
    for index, customer in customers_df.iterrows():
        # Skip customers that already received the message
        if customers_df.at[index, 'MessageStatus'] == 'हाँ':  # Skip already sent customers
            print(f"Skipping {customer.get('CustomerName', 'Sir/Ma\'am')} as message is already sent.")
            continue  # Skip this customer

        # Extract customer data with defaults
        name = customer.get('CustomerName', '').strip()
        firm_name = customer.get('FirmName', '').strip()

        # Handle missing values
        if not name:  # If name is missing
            name = "Sir/Ma'am"
        if not firm_name:  # If firm name is missing
            firm_name = "Your Firm"

        # Combine all phone numbers into one list
        raw_numbers = [str(customer.get('Mobile1', '')), str(customer.get('Mobile2', '')), str(customer.get('Mobile3', ''))]
        all_numbers = []

        for numbers in raw_numbers:
            if pd.notna(numbers):  # Check if numbers column is not empty
                # Split by comma and add to the list
                all_numbers.extend([num.strip() for num in numbers.split(",")])

        # Ensure each phone number starts with +91 (India code)
        all_numbers = [number if number.startswith("+91") else "+91" + number for number in all_numbers]

        # Send message to each valid number, ensuring no duplicates
        for number in all_numbers:
            if number and number not in sent_numbers:  # Check if the number is not empty and not already sent
                # Prepare the message
                personalized_message = message_template.format(name=name, firmname=firm_name, companyname=company_name)
                
                # Send the message and update the status
                success = send_whatsapp_message(number, personalized_message)
                if success:
                    customers_df.at[index, 'MessageStatus'] = 'हाँ'  # Mark as sent (Hindi Yes)
                else:
                    customers_df.at[index, 'MessageStatus'] = 'नहीं'  # Mark as not sent (Hindi No)
                sent_numbers.add(number)  # Add number to sent list

                # Random delay between 10-20 seconds
                delay_time = random.randint(10, 20)
                print(f"Waiting for {delay_time} seconds before sending the next message.")
                time.sleep(delay_time)  # Random delay

    return customers_df  # Return the updated DataFrame

# Save the updated customers data with message status to Excel file
def save_updated_customers(customers_df, file_path):
    customers_df.to_excel(file_path, index=False)
    print(f"Updated customer data saved to {file_path}")

# Message template
message_template = """प्रिय {name},

Krishna Home Care की ओर से आपको नववर्ष की ढेर सारी शुभकामनाएं। इस नए साल में, पाएं खास ऑफर:

✨ 5 कैन खरीदें, 1 कैन मुफ्त पाएं!
यह ऑफर 1 से 10 जनवरी तक है।

धन्यवाद और शुभकामनाएं!  
टीम {companyname}
"""

# Load customer data from Excel file
customers_df = load_customers('customers.xlsx')  # Ensure the path to the file is correct

# Set your company name
company_name = "Krishna Home Care"

# Send messages to all customers and get updated customer data
updated_customers_df = send_bulk_messages(customers_df, message_template, company_name)

# Save updated customer data with message status to a new Excel file
save_updated_customers(updated_customers_df, "updated_customers.xlsx")
