# /root/salon-autonomous-ai/services/booking-service/firestore_schema.py

# Firestore Data Model for Booking Service

# Collection: 'services'
# Represents the types of services offered by the salon (e.g., Haircut, Manicure, Facial)
# Document ID: Auto-generated or a unique service ID
# Fields:
#   name (string): Name of the service (e.g., "Men's Haircut")
#   description (string): Detailed description of the service
#   duration_minutes (integer): Estimated duration of the service in minutes
#   price (float): Price of the service
#   category (string): Category of the service (e.g., "Hair", "Nails", "Skin")
#   is_active (boolean): Whether the service is currently offered
#   created_at (timestamp): Timestamp of creation
#   updated_at (timestamp): Timestamp of last update

# Collection: 'customers'
# Represents salon customers
# Document ID: Auto-generated or a unique customer ID
# Fields:
#   first_name (string): Customer's first name
#   last_name (string): Customer's last name
#   phone_number (string): Customer's primary phone number (unique)
#   email (string): Customer's email address (optional, unique)
#   loyalty_points (integer): Loyalty points accumulated by the customer
#   last_visit (timestamp): Timestamp of the last visit
#   total_visits (integer): Total number of visits
#   preferences (map): Map of customer preferences (e.g., {'stylist': 'John Doe', 'shampoo': 'Volumizing'})
#   created_at (timestamp): Timestamp of creation
#   updated_at (timestamp): Timestamp of last update

# Collection: 'bookings'
# Represents scheduled appointments
# Document ID: Auto-generated or a unique booking ID
# Fields:
#   customer_id (string): Reference to the 'customers' collection Document ID
#   service_id (string): Reference to the 'services' collection Document ID
#   staff_id (string): Reference to the 'staff' collection Document ID (assuming a 'staff' collection will exist)
#   start_time (timestamp): Start time of the booking
#   end_time (timestamp): End time of the booking
#   status (string): Current status of the booking (e.g., 'scheduled', 'completed', 'cancelled', 'no-show')
#   notes (string): Any specific notes for the booking
#   price_at_booking (float): Price of the service at the time of booking
#   payment_status (string): Payment status (e.g., 'pending', 'paid', 'refunded')
#   created_at (timestamp): Timestamp of creation
#   updated_at (timestamp): Timestamp of last update

# Note: A 'staff' collection would also be necessary to manage salon employees and their schedules.
# Collection: 'staff'
# Document ID: Auto-generated or a unique staff ID
# Fields:
#   first_name (string)
#   last_name (string)
#   role (string): e.g., 'Stylist', 'Manicurist', 'Receptionist'
#   phone_number (string)
#   email (string)
#   is_active (boolean)
#   specialties (array of strings): e.g., ['Haircut', 'Coloring']
#   schedule (map): Map of availability (e.g., {'Monday': {'start': '09:00', 'end': '17:00'}})
#   created_at (timestamp)
#   updated_at (timestamp)
