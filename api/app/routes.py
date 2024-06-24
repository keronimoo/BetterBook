from flask import Blueprint, request, jsonify, session , url_for
import re
import sqlite3
from app import client
from app.utils import claude_context_decider , bot_sql_engine , bot_prompt_2_prompt , execute_sql , send_email
from app.prompts import OPENAI_SYSTEM_PROMPT
from app.models import User , Hotel , Room , HotelMetaData , ChatHistory , Amenities , room_amenities_association  , hotel_amenities_association , Booking , Guest
from app.decorators import login_required
from app import db
import uuid
import json
import datetime
from itsdangerous import URLSafeTimedSerializer, SignatureExpired , BadSignature
api = Blueprint("api" , __name__)

s = URLSafeTimedSerializer('0234-899-*?091')

# @api.before_request
# def before_request():
#     if 'messages' not in session:
#         session['messages'] = [{'role': 'system', 'content': OPENAI_SYSTEM_PROMPT.substitute(user_question="tell me about hotels in london")}]


@api.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json()
    user_message = data['message']
    chat_subject = user_message

        # Generate a unique session ID for the chat
    session_id = str(uuid.uuid4())

    # Create a new ChatHistory entry for the initial user message

    js_user_message ="{\"role\":\"user\",\"message\":\"%s\"}" % user_message
    user_chat = ChatHistory(
        user_id=session['user_id'],
        session_id=session_id,
        chat_subject=chat_subject,
        message=js_user_message)
    

    print("DEBUG: /CHAT session=> userid", session['user_id'])
    

    print("DEBUG: /CHAT js_user" ,js_user_message)
    
    db.session.add(user_chat)
    db.session.commit()
    p2p = bot_prompt_2_prompt(user_message)

    sql = bot_sql_engine(p2p)

    results = execute_sql(sql , p2p , 1)

    js_bot_message = "{\"role\":\"assistant\",\"message\":\"%s\"}" % results
    print("DEBUG: /CHAT js_bot", js_bot_message)
    
    bot_chat = ChatHistory(
        user_id=session['user_id'],
        session_id=session_id,
        chat_subject=chat_subject,
        message=js_bot_message
    )
    db.session.add(bot_chat)
    db.session.commit()

    # return jsonify({'response': results})
    return jsonify({'redirect_url': f"/chat/{session_id}"}), 201


@api.route('/register', methods=['POST'])
def register_user():
    try:
        # Parse request JSON data
        data = request.get_json()

        # Extract registration data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')

        # Check if required fields are present
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400

        # Check if the username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 409

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'error': 'Email address already exists'}), 409

        # Create a new user instance
        new_user = User(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )

        # Add new user to the database session
        db.session.add(new_user)
        db.session.commit()

        user_data = {
            'user_id': new_user.user_id,
            'username': new_user.username,
            'email': new_user.email,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'phone_number': new_user.phone_number
        }

        # Return success response with user data and HTTP status code 201 (Created)
        return jsonify({'user': user_data}), 201

    except Exception as e:
        db.session.rollback()  # Roll back any changes made during the session
        return jsonify({'error': str(e)}), 500

@api.route("/chat/<string:session_id>", methods=["POST"])
@login_required
def chat_with_session(session_id):
    data = request.get_json()
    user_message = data['message']

    # Retrieve the existing chat history entry (initial entry for this chat session)
    initial_chat = ChatHistory.query.filter_by(session_id=session_id).first_or_404()
    chat_subject = initial_chat.chat_subject  # Get the subject of the chat

    # Create a new ChatHistory entry for the user message
    user_chat = ChatHistory(
        user_id=session['user_id'],
        session_id=session_id,
        chat_subject=chat_subject,
        message=json.dumps({"role": "user", "message": user_message})
    )
    db.session.add(user_chat)
    db.session.commit()

    # Process the message with the bot
    p2p = bot_prompt_2_prompt(user_message)
    sql = bot_sql_engine(p2p)
    results = execute_sql(sql , p2p , 1)

    # Create a new ChatHistory entry for the bot response
    bot_chat = ChatHistory(
        user_id=session['user_id'],
        session_id=session_id,
        chat_subject=chat_subject,
        message=json.dumps({"role": "assistant", "message": results})
    )
    db.session.add(bot_chat)
    db.session.commit()

    return jsonify({'response': results})

@api.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        # Find the user by username or email
        user = User.query.filter_by(username=username).first()

        # Verify user and password
        if user and user.password == password:
            # Store user_id in session to indicate user is logged in
            session['user_id'] = user.user_id

            
            user_data = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number
            }

            # Return success response with user data and HTTP status code 200 (OK)
            return jsonify({'user': user_data}), 200
        else:
            # Return error response for invalid credentials
            return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@api.route('/logout', methods=['POST'])
def logout():
    try:
        # Check if user is logged in
        if 'user_id' in session:
            # Clear the user_id from session to log out the user
            session.pop('user_id', None)

            # Return success response with message and HTTP status code 200 (OK)
            return jsonify({'message': 'User logged out successfully'}), 200
        else:
            # Return error response if user is not logged in
            return jsonify({'error': 'User is not logged in'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/users', methods=['GET'])
#@login_required deneme
def get_users():
    try:
        # Query all users from the database
        users = User.query.all()

        users_list = []
        for user in users:
            user_data = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number
            }
            users_list.append(user_data)

        # Return users data as JSON response with HTTP status code 200 (OK)
        return jsonify({'users': users_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@api.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        # Query the user from the database by user_id
        user = User.query.get(user_id)

        if not user:
            # If user with the given user_id does not exist, return 404 Not Found
            return jsonify({'error': 'User not found'}), 404

        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number
        }

        # Return user data as JSON response with HTTP status code 200 (OK)
        return jsonify({'user': user_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@api.route('/hotels', methods=['GET'])
def get_hotels():
    try:
        # Query all hotels from the database
        hotels = Hotel.query.all()

        hotels_list = []
        for hotel in hotels:
            hotel_data = {
                'hotel_id': hotel.hotel_id,
                'name': hotel.name,
                'address': hotel.address,
                'city': hotel.city,
                'country': hotel.country,
                'rating': hotel.rating,
                'description': hotel.description
                # You can include more fields as needed
            }
            hotels_list.append(hotel_data)

        # Return hotels data as JSON response with HTTP status code 200 (OK)
        return jsonify({'hotels': hotels_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@api.route('/hotels/<int:hotel_id>', methods=['GET'])
def get_hotel_by_id(hotel_id):
    try:
        # Query the hotel from the database by hotel_id
        hotel = Hotel.query.get(hotel_id)
        hotel_mdata = HotelMetaData.query.get(hotel_id)

        if not hotel:
            # If hotel with the given hotel_id does not exist, return 404 Not Found
            return jsonify({'error': 'Hotel not found'}), 404

        hotel_data = {
            'hotel_id': hotel.hotel_id,
            'name': hotel.name,
            'address': hotel.address,
            'city': hotel.city,
            'country': hotel.country,
            'rating': hotel.rating,
            'description': hotel.description,
            'website_url': hotel_mdata.website_url,
            'photo_url': hotel_mdata.photo_url
        }

        # Return hotel data as JSON response with HTTP status code 200 (OK)
        return jsonify({'hotel': hotel_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Get rooms for a specific hotel
@api.route('/hotels/<int:hotel_id>/rooms', methods=['GET'])
def get_rooms_by_hotel(hotel_id):
    """
    Retrieve all rooms for a specific hotel.

    parameters:
        name :hotel_id
        description : id of the hotel
    response:
        200:
            description: List of rooms for the hotel
            example:
                [
                {
                  "room_id": 1,
                  "room_type": "Single",
                  "capacity": 1,
                  "price_per_night": 100.0,
                  "availability": true
                },
                {
                  "room_id": 2,
                  "room_type": "Double",
                  "capacity": 2,
                  "price_per_night": 150.0,
                  "availability": false
                }
              ]
        400:
            description: Hotel not found or no rooms available for the specified hotel
            example:
              {
                "message": "No rooms available for this hotel"
              }
    """
    rooms = Room.query.filter_by(hotel_id=hotel_id).all()
    result = []
    for room in rooms:
        result.append({
            'room_id': room.room_id,
            'room_type': room.room_type,
            'capacity': room.capacity,
            'price_per_night': room.price_per_night,
            'availability': room.availability
        })
    return jsonify(result)

@api.route('/hotels/<int:hotel_id>/metadata', methods=['GET'])
def get_hotel_metadata(hotel_id):
    try:
        # Query the database to get the hotel metadata by hotel ID
        _metadata = HotelMetaData.query.filter_by(hotel_id=hotel_id).first()

        # Check if metadata exists for the given hotel ID
        if not _metadata:
            return jsonify({'error': 'Hotel metadata not found'}), 404

        # Prepare metadata data for JSON response
        metadata_data = {
            'hotel_id': _metadata.hotel_id,
            'website_url': _metadata.website_url,
            'photo_url': _metadata.photo_url
        }

        # Return success response with metadata data and HTTP status code 200 (OK)
        return jsonify({'metadata': metadata_data}), 200

    except Exception as e:
        # Handle exceptions (e.g., database errors) and return error response
        return jsonify({'error': str(e)}), 500
    
#chat messages of a chat with specified id
@api.route('/chats/<string:session_id>', methods=['GET'])
def get_chat_history(session_id):
    try:
        # Query the database to get chat history by chat ID
        chat_history = ChatHistory.query.filter_by(session_id=session_id).all()

        # Check if any messages exist for the given chat ID
        if not chat_history:
            return jsonify({'error': 'Chat history not found'}), 404

        # Prepare chat history data for JSON response
        chat_history_data = [
            {
                'session_id': chat.session_id,
                'user_id': chat.user_id,
                'message': chat.message,
                'timestamp': chat.timestamp
            }
            for chat in chat_history
        ]

        # Return success response with chat history data and HTTP status code 200 (OK)
        return jsonify({'chat_history': chat_history_data}), 200

    except Exception as e:

        return jsonify({'error': str(e)}), 500
    
@api.route('/rooms/<int:room_id>/amenities', methods=['GET'])
def get_room_amenities(room_id):
    try:
        # Query the database to get room by room ID
        room = Room.query.get(room_id)

        # Check if the room exists
        if not room:
            return jsonify({'error': 'Room not found'}), 404

        # Get the amenities for the room
        amenities = db.session.query(Amenities).join(room_amenities_association).filter(room_amenities_association.c.room_id == room_id).all()

        # Prepare amenities data for JSON response
        amenities_data = [
            {
                'amenity_id': amenity.amenity_id,
                'name': amenity.name
            }
            for amenity in amenities
        ]

        # Return success response with amenities data and HTTP status code 200 (OK)
        return jsonify({'room_id': room_id, 'amenities': amenities_data}), 200

    except Exception as e:

        return jsonify({'error': str(e)}), 500   
    
@api.route('/hotels/<int:hotel_id>/amenities', methods=['GET'])
def get_hotel_amenities(hotel_id):
    try:
        # Query the database to get the hotel by hotel ID
        hotel = Hotel.query.get(hotel_id)

        # Check if the hotel exists
        if not hotel:
            return jsonify({'error': 'Hotel not found'}), 404

        # Get the amenities for the hotel
        amenities = db.session.query(Amenities).join(hotel_amenities_association).filter(hotel_amenities_association.c.hotel_id == hotel_id).all()

        # Prepare amenities data for JSON response
        amenities_data = [
            {
                'amenity_id': amenity.amenity_id,
                'name': amenity.name
            }
            for amenity in amenities
        ]

        # Return success response with amenities data and HTTP status code 200 (OK)
        return jsonify({'hotel_id': hotel_id, 'amenities': amenities_data}), 200

    except Exception as e:

        return jsonify({'error': str(e)}), 500
    
@api.route('/users/<int:user_id>/chats', methods=['GET'])
def get_user_chats(user_id):
    try:
        # Query the database to get the user by user ID
        user = User.query.get(user_id)

        # Check if the user exists
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get all chat histories for the user
        # chats = ChatHistory.query.filter_by(user_id=user_id).all()
        chats = ChatHistory.query.filter_by(user_id=user_id).group_by(ChatHistory.session_id).all()

        # Prepare chat data for JSON response
        chats_data = [
            {
                'session_id': chat.session_id,
                'subject': chat.chat_subject
            }
            for chat in chats
        ]

        # Return success response with chats data and HTTP status code 200 (OK)
        return jsonify({'user_id': user_id, 'chats': chats_data}), 200

    except Exception as e:

        return jsonify({'error': str(e)}), 500

   
# Example call for /reserve endpoint
# {
#     "room_id": 1,
#     "check_in_date": "2024-06-01",
#     "check_out_date": "2024-06-05",
#     "total_price": 500.00,
#     "guests": [
#         {
#             "first_name": "John",
#             "last_name": "Doe",
#             "age": 30,
#             "ssn": "11122223344"
#         },
#         {
#             "first_name": "Jane",
#             "last_name": "Doe",
#             "age": 28,
#             "ssn": "11122223344"
#         }
#     ]
# }
# 201 success
# 400 Number of guests exceeds room capacity
# 404 room not found
@api.route("/reserve", methods=["POST"])
@login_required
def reserve():
    try:
        data = request.get_json()
        user_id = session['user_id']
        room_id = data['room_id']
        check_in_date_str = data['check_in_date']
        check_out_date_str = data['check_out_date']
        total_price = data['total_price']
        guests_info = data['guests']


         # Parse string dates into datetime.date objects
        check_in_date = datetime.datetime.strptime(check_in_date_str, '%Y-%m-%d').date()
        check_out_date = datetime.datetime.strptime(check_out_date_str, '%Y-%m-%d').date()


        # Retrieve room information to check capacity
        room = Room.query.get(room_id)
        if not room:
            return jsonify({'error': 'Room not found'}), 404

        # Check if the number of guests exceeds room capacity
        if len(guests_info) > room.capacity:
            return jsonify({'error': 'Number of guests exceeds room capacity'}), 400

        # Create a new booking entry
        new_booking = Booking(
            user_id=user_id,
            room_id=room_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            total_price=total_price
        )
        db.session.add(new_booking)
        db.session.commit()

        # Create guest entries linked to the booking
        for guest_info in guests_info:
            guest = Guest(
                booking_id=new_booking.booking_id,
                first_name=guest_info['first_name'],
                last_name=guest_info['last_name'],
                age=guest_info['age'],
                ssn=guest_info['ssn']
            )
            db.session.add(guest)

        db.session.commit()

        return jsonify({'message': 'Reservation successful'}), 201
    except Exception as e:
        #return error response
        return jsonify({'error': str(e)}), 500



#Example response GET /bookings/4/guests
# {
#     "booking_id": 4,
#     "guests": [
#         {
#             "age": 30,
#             "first_name": "John",
#             "guest_id": 1,
#             "last_name": "Doe",
#             "ssn": "11122223344"
#         },
#         {
#             "age": 28,
#             "first_name": "Jane",
#             "guest_id": 2,
#             "last_name": "Doe",
#             "ssn": "11122223344"
#         }
#     ]
# }
@api.route('/bookings/<int:booking_id>/guests', methods=['GET'])
def get_guests_by_booking(booking_id):
    try:
        # Query the database to get the booking by booking ID
        booking = Booking.query.get(booking_id)

        # Check if the booking exists
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        # Get all guests for the booking
        guests = Guest.query.filter_by(booking_id=booking_id).all()

        # Prepare guest data for JSON response
        guests_data = [
            {
                'guest_id': guest.guest_id,
                'first_name': guest.first_name,
                'last_name': guest.last_name,
                'age': guest.age,
                'ssn': guest.ssn
            }
            for guest in guests
        ]

        # Return success response with guests data and HTTP status code 200 (OK)
        return jsonify({'booking_id': booking_id, 'guests': guests_data}), 200

    except Exception as e:
        
        return jsonify({'error': str(e)}), 500
    


@api.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    # Check if the email exists in the database
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found'}), 404

    # Generate a one-time token
    token = s.dumps(email, salt='password-reset-salt')

    # Create the password reset link
    reset_url = url_for('api.reset_password', token=token, _external=True)

    # Send the reset link via email
    subject = "Password Reset Request"
    from_email = "keremsenyurt@proton.me"
    from_name = "BetterBook"
    to_email = email
    body_html = f"<p>To reset your password, click the following link: <a href='{reset_url}'>{reset_url}</a></p>"
    body_text = f"To reset your password, click the following link: {reset_url}"

    send_email(subject, from_email, from_name, to_email, body_html, body_text)

    return jsonify({'message': 'Password reset link has been sent to your email.'}), 200

# Example POST http://127.0.0.1:5000/reset-password/ImtlcmVtc2VueXVydDFAZ21haWwuY29tIg.ZlEjFQ.2RbKh6V701zzUgCAS11lUolDgMka
# {
#   "password": "new_password123"
# }
# response 200 on success
# 400 if token is expired or invalid or user does not exist
@api.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        # Decode the token and extract the email
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        return jsonify({'error': 'The token is expired'}), 400
    except BadSignature:
        return jsonify({'error': 'Invalid token'}), 400

    if request.method == 'POST':
        data = request.get_json()
        new_password = data.get('password')

        # Update the user's password in the database
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Invalid token or user does not exist'}), 400

        user.password = new_password
        db.session.commit()

        return jsonify({'message': 'Your password has been updated'}), 200

    return jsonify({'message': 'Please enter your new password'}), 200