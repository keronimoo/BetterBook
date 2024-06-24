from app import db

# Association table for Hotel-Amenities Many-to-Many relationship
hotel_amenities_association = db.Table('hotel_amenities',
    db.Column('hotel_id', db.Integer, db.ForeignKey('hotel.hotel_id')),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.amenity_id'))
)

# Association table for Room-Amenities Many-to-Many relationship
room_amenities_association = db.Table('room_amenities',
    db.Column('room_id', db.Integer, db.ForeignKey('room.room_id')),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.amenity_id'))
)

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))

    bookings = db.relationship("Booking", back_populates="user") #one to many
    chat_history = db.relationship("ChatHistory", back_populates="user")

class Hotel(db.Model):
    __tablename__ = 'hotel'

    hotel_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    rating = db.Column(db.Float)
    description = db.Column(db.Text)  # Added hotel description column

    rooms = db.relationship("Room", back_populates="hotel")
    amenities = db.relationship("Amenities", secondary=hotel_amenities_association, back_populates="hotels")
    hotel_metadata = db.relationship("HotelMetaData", uselist=False, back_populates="hotel")  # One-to-One

class Room(db.Model):
    __tablename__ = 'room'

    room_id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.hotel_id'))
    room_type = db.Column(db.String(50))
    capacity = db.Column(db.Integer)
    price_per_night = db.Column(db.Float)
    availability = db.Column(db.Boolean)

    hotel = db.relationship("Hotel", back_populates="rooms")
    bookings = db.relationship("Booking", back_populates="room")

class Booking(db.Model):
    __tablename__ = 'booking'

    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'))
    check_in_date = db.Column(db.Date)
    check_out_date = db.Column(db.Date)
    total_price = db.Column(db.Float)

    user = db.relationship("User", back_populates="bookings")
    room = db.relationship("Room", back_populates="bookings")
    guests = db.relationship("Guest", back_populates="booking")

class Amenities(db.Model):
    __tablename__ = 'amenities'

    amenity_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    hotels = db.relationship("Hotel", secondary=hotel_amenities_association, back_populates="amenities")


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    message_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    session_id = db.Column(db.String(255), index=True)
    chat_subject = db.Column(db.String(255))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship("User", back_populates="chat_history") # many to one


class HotelMetaData(db.Model):
    __tablename__ = 'hotel_metadata'

    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.hotel_id'), primary_key=True)
    website_url = db.Column(db.String(255))
    photo_url = db.Column(db.String(255))

    hotel = db.relationship("Hotel", back_populates="hotel_metadata") # one to one


class Guest(db.Model):
    __tablename__ = 'guest'

    guest_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    ssn = db.Column(db.String(13))  

    booking = db.relationship("Booking", back_populates="guests")
