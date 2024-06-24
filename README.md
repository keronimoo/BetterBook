# BetterBook
## _LLM Integrated Hotel Search_
This project aims to enhance the user experience of hotel and travel booking by integrating a large language model (LLM). This integration simplifies the booking process by allowing users to interact with the app using natural language queries.

## Timeline
*`local_version`: A local quantized 7 billion parameters llama-2 model is used. Setted up a Inference endpoint with llama.cpp binding LLaMaSharp with ASP.NET Core Minimal API. A Streamlit based chat interface is developed to call this endpoint.

*`streamlit_version`: Switched to OpenAI API from the local Llama-2. Streamlit Interface is enhanced slightly.

*`api`: Developed a fully functional API with Flask. Enhanced the integration of multiple APIs including Gemini, Anthropic, and OpenAI



## Endpoints

### /login

This endpoint allows users to log in to the application.

**Method:** POST

**Request Body:**

```json
{
  "username": "username",
  "password": "password"
}
```

**Response Body (Success):**

```json
{
  "user": {
    "user_id": "user_id",
    "username": "username",
    "email": "email",
    "first_name": "first_name",
    "last_name": "last_name",
    "phone_number": "phone_number"
  }
}
```

**Response Body (Error):**

```json
{
  "error": "Invalid username or password" 
}
```

**Status Codes:**

* **200 OK:** Successful login.
* **401 Unauthorized:** Invalid username or password.
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**

* The `user_id` is stored in the session to indicate that the user is logged in.
* The `user` object contains basic user information. 
### /logout

This endpoint logs out the current user.

**Method:** POST

**Request Body:** None

**Response Body (Success):**

```json
{
  "message": "User logged out successfully" 
}
```

**Response Body (Error):**

```json
{
  "error": "User is not logged in"
}
```

**Status Codes:**

* **200 OK:** User logged out successfully.
* **401 Unauthorized:** User is not logged in.
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**

* This endpoint removes the `user_id` from the session, effectively logging out the user.

### /forgot-password

This endpoint allows users to request a password reset link.

**Method:** POST

**Request Body:**

```json
{
  "email": "user_email"
}
```

**Response Body (Success):**

```json
{
  "message": "Password reset link has been sent to your email."
}
```

**Response Body (Error):**

```json
{
  "error": "Email not found"
}
```

**Status Codes:**

* **200 OK:** Password reset link sent successfully.
* **404 Not Found:** Email address not found in the database.
* **500 Internal Server Error:** An unexpected error occurred while sending the email.

**Notes:**

* This endpoint doesn't require authentication.
* The request body includes the user's email address.
* The endpoint generates a unique token and sends a password reset link to the provided email address.
* The email should include the reset link, which will be used to reset the password on the client-side.

### /register

This endpoint allows new users to register for the application.

**Method:** POST

**Request Body:**

```json
{
  "username": "username",
  "email": "user_email",
  "password": "user_password",
  "first_name": "first_name",
  "last_name": "last_name",
  "phone_number": "phone_number"
}
```

**Response Body (Success):**

```json
{
  "user": {
    "user_id": "user_id",
    "username": "username",
    "email": "user_email",
    "first_name": "first_name",
    "last_name": "last_name",
    "phone_number": "phone_number"
  }
}
```

**Response Body (Error):**

```json
{
  "error": "Error message"
}
```

**Status Codes:**

* **201 Created:** User registered successfully.
* **400 Bad Request:** Missing required fields (username, email, password).
* **409 Conflict:** Username or email address already exists.
* **500 Internal Server Error:** An unexpected error occurred during registration.

**Notes:**

* The endpoint checks if required fields are present in the request body.
* It validates that the username and email are not already taken.
* The endpoint creates a new user object in the database.
* The endpoint returns the user's information, including the newly assigned user ID, in the response.  



### /chat

This endpoint handles user chat messages and initiates a conversation.

**Method:** POST

**Request Body:**

```json
{
  "message": "user_message"
}
```

**Response Body (Success):**

```json
{
  "redirect_url": "/chat/session_id"
}
```

**Status Codes:**

* **201 Created:** Chat session started successfully, redirects to the chat session.
* **401 Unauthorized:** User is not logged in.
* **500 Internal Server Error:** An unexpected error occurred while processing the message.

**Notes:**

* This endpoint requires authentication (`@login_required`).
* The request body includes the user's message.
* The endpoint creates a new chat session (`session_id`) and stores the initial user message in the database. 
* The endpoint generates a response from the bot based on the user's message and stores it in the database
* The endpoint redirects the user to the chat session URL, which likely includes the `session_id`.
* The `redirect_url` should include a URL that allows the user to view the conversation history and continue interacting. 







### /hotels

This endpoint retrieves a list of all hotels in the database.

**Method:** GET

**Request Body:** None

**Response Body:**

```json
{
  "hotels": [
    {
      "hotel_id": "hotel_id",
      "name": "hotel_name",
      "address": "hotel_address",
      "city": "hotel_city",
      "country": "hotel_country",
      "rating": "hotel_rating",
      "description": "hotel_description"

    },

  ]
}
```

**Status Codes:**

* **200 OK:** Hotels data retrieved successfully.
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**
 
* Consider adding pagination to this endpoint if you expect a large number of hotels. 
## /hotels/<int:hotel_id>

This endpoint retrieves details of a specific hotel by its ID.

**Method:** GET

**URL Parameters:**

* **hotel_id:** The ID of the hotel to retrieve (integer).

**Response Body (Success):**

```json
{
  "hotel": {
    "hotel_id": "hotel_id",
    "name": "hotel_name",
    "address": "hotel_address",
    "city": "hotel_city",
    "country": "hotel_country",
    "rating": "hotel_rating",
    "description": "hotel_description",
    "website_url": "hotel_website_url",
    "photo_url": "hotel_photo_url"
  }
}
```

**Response Body (Error):**

```json
{
  "error": "Hotel not found"
}
```

**Status Codes:**

* **200 OK:** Hotel data retrieved successfully.
* **404 Not Found:** Hotel with the given ID does not exist.
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**
 
* Ensure that the `hotel_id` is a valid integer.


### /hotels/<int:hotel_id>/rooms

This endpoint retrieves a list of rooms available at a specific hotel.

**Method:** GET

**URL Parameters:**

* **hotel_id:** The ID of the hotel to retrieve rooms for (integer).

**Response Body:**

```json
[
  {
    "room_id": "room_id",
    "room_type": "room_type",
    "capacity": "room_capacity",
    "price_per_night": "room_price",
    "availability": "room_availability"
  },
]
```

**Status Codes:**

* **200 OK:** Room data retrieved successfully. 
* **404 Not Found:** Hotel with the given ID does not exist. (You may want to add this error handling if it's not already implemented)
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**

* The response is a list of dictionaries, each representing a room with its details.
* Ensure that the `hotel_id` is a valid integer.
## /hotels/<int:hotel_id>/metadata

This endpoint retrieves the metadata associated with a specific hotel.

**Method:** GET

**URL Parameters:**

* **hotel_id:** The ID of the hotel to retrieve metadata for (integer).

**Response Body (Success):**

```json
{
  "metadata": {
    "hotel_id": "hotel_id",
    "website_url": "hotel_website_url",
    "photo_url": "hotel_photo_url"
  }
}
```

**Response Body (Error):**

```json
{
  "error": "Hotel metadata not found"
}
```

**Status Codes:**

* **200 OK:** Hotel metadata retrieved successfully.
* **404 Not Found:** Hotel metadata with the given ID does not exist.
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**

* The response contains a dictionary with the hotel's metadata.
* Ensure that the `hotel_id` is a valid integer.




### /chats/<string:session_id>

This endpoint retrieves the chat history for a specific chat session.

**Method:** GET

**URL Parameters:**

* **session_id:** The unique identifier of the chat session (string).

**Response Body (Success):**

```json
{
  "chat_history": [
    {
      "session_id": "session_id",
      "user_id": "user_id",
      "message": "message_content",
      "timestamp": "timestamp"
    },
    // ... more messages
  ]
}
```

**Response Body (Error):**

```json
{
  "error": "Chat history not found"
}
```

**Status Codes:**

* **200 OK:** Chat history retrieved successfully.
* **404 Not Found:** Chat history with the given session ID does not exist.
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**

* The response is a list of dictionaries, each representing a message in the chat history.
* Ensure that the `session_id` is a valid string.

### /rooms/<int:room_id>/amenities

This endpoint retrieves the list of amenities associated with a specific room.

**Method:** GET

**URL Parameters:**

* **room_id:** The ID of the room to retrieve amenities for (integer).

**Response Body (Success):**

```json
{
  "room_id": "room_id",
  "amenities": [
    {
      "amenity_id": "amenity_id",
      "name": "amenity_name"
    },
    // ... more amenities
  ]
}
```

**Response Body (Error):**

```json
{
  "error": "Room not found"
}
```

**Status Codes:**

* **200 OK:** Room amenities retrieved successfully.
* **404 Not Found:** Room with the given ID does not exist.
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**

* The response includes the room ID and a list of amenities associated with that room.
* Ensure that the `room_id` is a valid integer.

### /hotels/<int:hotel_id>/amenities

This endpoint retrieves a list of amenities available at a specific hotel.

**Method:** GET

**URL Parameters:**

* **hotel_id:** The ID of the hotel to retrieve amenities for (integer).

**Response Body (Success):**

```json
{
  "hotel_id": "hotel_id",
  "amenities": [
    {
      "amenity_id": "amenity_id",
      "name": "amenity_name"
    },
    // ... more amenities
  ]
}
```

**Response Body (Error):**

```json
{
  "error": "Hotel not found"
}
```

**Status Codes:**

* **200 OK:** Hotel amenities retrieved successfully.
* **404 Not Found:** Hotel with the given ID does not exist.
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**

* The response includes the hotel ID and a list of amenities available at that hotel.
* Ensure that the `hotel_id` is a valid integer.

### /users/<int:user_id>/chats

This endpoint retrieves a list of chat sessions associated with a specific user.

**Method:** GET

**URL Parameters:**

* **user_id:** The ID of the user to retrieve chats for (integer).

**Response Body (Success):**

```json
{
  "user_id": "user_id",
  "chats": [
    {
      "session_id": "session_id",
      "subject": "chat_subject"
    },
    // ... more chats
  ]
}
```

**Response Body (Error):**

```json
{
  "error": "User not found"
}
```

**Status Codes:**

* **200 OK:** User chats retrieved successfully.
* **404 Not Found:** User with the given ID does not exist.
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**

* The response includes the user ID and a list of chat sessions associated with that user.
* Ensure that the `user_id` is a valid integer.

 
### /reserve

This endpoint allows a logged-in user to make a reservation for a specific room.

**Method:** POST

**Request Body:**

```json
{
  "room_id": "room_id",
  "check_in_date": "YYYY-MM-DD",
  "check_out_date": "YYYY-MM-DD",
  "total_price": "price",
  "guests": [
    {
      "first_name": "guest_first_name",
      "last_name": "guest_last_name",
      "age": "guest_age",
      "ssn": "guest_ssn" 
    },
    // ... more guests
  ]
}
```

**Response Body (Success):**

```json
{
  "message": "Reservation successful"
}
```

**Response Body (Error):**

```json
{
  "error": "Error message" 
}
```

**Status Codes:**

* **201 Created:** Reservation created successfully.
* **400 Bad Request:** Invalid request data, such as exceeding room capacity.
* **401 Unauthorized:** User is not logged in.
* **404 Not Found:** Room not found.
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**

* This endpoint requires authentication (`@login_required`).
* The request body includes details of the room, dates, total price, and guest information.
* The dates should be provided in the format "YYYY-MM-DD".
* Ensure that the number of guests does not exceed the room capacity. 
* The `guests` array should contain dictionaries with guest information.
* The endpoint creates a new booking entry and links guest entries to it.

## /bookings/<int:booking_id>/guests

This endpoint retrieves a list of guests associated with a specific booking.

**Method:** GET

**URL Parameters:**

* **booking_id:** The ID of the booking to retrieve guests for (integer).

**Response Body (Success):**

```json
{
  "booking_id": "booking_id",
  "guests": [
    {
      "guest_id": "guest_id",
      "first_name": "guest_first_name",
      "last_name": "guest_last_name",
      "age": "guest_age",
      "ssn": "guest_ssn" 
    },
    // ... more guests
  ]
}
```

**Response Body (Error):**

```json
{
  "error": "Booking not found"
}
```

**Status Codes:**

* **200 OK:** Guests retrieved successfully.
* **404 Not Found:** Booking with the given ID does not exist.
* **500 Internal Server Error:** An unexpected error occurred.

**Notes:**

* The response includes the booking ID and a list of guests associated with that booking.
* Ensure that the `booking_id` is a valid integer.

### /reset-password/<token>

This endpoint allows users to reset their password using a token received in their email.

**Method:** GET (Initial request) or POST (Submitting new password)

**URL Parameters:**

* **token:** The password reset token (string) received by the user via email.

**Request Body (POST):**

```json
{
  "password": "new_password"
}
```

**Response Body (Success - GET):**

```json
{
  "message": "Please enter your new password"
}
```

**Response Body (Success - POST):**

```json
{
  "message": "Your password has been updated"
}
```

**Response Body (Error):**

```json
{
  "error": "Error message"
}
```

**Status Codes:**

* **200 OK:**  GET: Shows a form for entering the new password; POST: Password updated successfully.
* **400 Bad Request:** The token is expired or invalid.
* **400 Bad Request:** Invalid request data for the password update.
* **400 Bad Request:** Invalid token or user does not exist.
* **500 Internal Server Error:** An unexpected error occurred during password update.

**Notes:**

* The endpoint handles both the initial GET request to display the password reset form and the POST request to submit the new password.
* Ensure that the token is validated on both GET and POST requests.
* The endpoint should expire the token after a certain period (e.g., 1 hour) to prevent abuse.
 