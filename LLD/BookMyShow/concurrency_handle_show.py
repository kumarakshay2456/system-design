# enums.py
from enum import Enum
import threading
import time
import uuid
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import random

class City(Enum):
    BANGALORE = "Bangalore"
    DELHI = "Delhi"

class SeatCategory(Enum):
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

class BookingStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


# movie.py
class Movie:
    def __init__(self):
        self.movie_id = None
        self.movie_name = None
        self.movie_duration_in_minutes = None
    
    def get_movie_id(self):
        return self.movie_id
    
    def set_movie_id(self, movie_id):
        self.movie_id = movie_id
    
    def get_movie_name(self):
        return self.movie_name
    
    def set_movie_name(self, movie_name):
        self.movie_name = movie_name
    
    def get_movie_duration(self):
        return self.movie_duration_in_minutes
    
    def set_movie_duration(self, movie_duration):
        self.movie_duration_in_minutes = movie_duration


# seat.py
class Seat:
    def __init__(self):
        self.seat_id = None
        self.row = None
        self.seat_category = None
        self.is_booked = False
        self.version = 0  # For optimistic locking
        self.lock = threading.RLock()  # For pessimistic locking
    
    def get_seat_id(self):
        return self.seat_id
    
    def set_seat_id(self, seat_id):
        self.seat_id = seat_id
    
    def get_row(self):
        return self.row
    
    def set_row(self, row):
        self.row = row
    
    def get_seat_category(self):
        return self.seat_category
    
    def set_seat_category(self, seat_category):
        self.seat_category = seat_category


# screen.py
class Screen:
    def __init__(self):
        self.screen_id = None
        self.seats = []
    
    def get_screen_id(self):
        return self.screen_id
    
    def set_screen_id(self, screen_id):
        self.screen_id = screen_id
    
    def get_seats(self):
        return self.seats
    
    def set_seats(self, seats):
        self.seats = seats


# Seat reservation for temporary holds
class SeatReservation:
    def __init__(self, seat_id, user_id, expiry_time):
        self.seat_id = seat_id
        self.user_id = user_id
        self.expiry_time = expiry_time
        self.is_active = True
    
    def is_expired(self):
        return datetime.now() > self.expiry_time
    
    def cancel(self):
        self.is_active = False


# show.py with concurrency control
class Show:
    def __init__(self):
        self.show_id = None
        self.movie = None
        self.screen = None
        self.show_start_time = None
        self.booked_seat_ids = []
        self.version = 0  # For optimistic locking
        self.lock = threading.RLock()  # For pessimistic locking
        self.seat_reservations = {}  # seat_id -> SeatReservation
        self.reservation_lock = threading.RLock()
    
    def get_show_id(self):
        return self.show_id
    
    def set_show_id(self, show_id):
        self.show_id = show_id
    
    def get_movie(self):
        return self.movie
    
    def set_movie(self, movie):
        self.movie = movie
    
    def get_screen(self):
        return self.screen
    
    def set_screen(self, screen):
        self.screen = screen
    
    def get_show_start_time(self):
        return self.show_start_time
    
    def set_show_start_time(self, show_start_time):
        self.show_start_time = show_start_time
    
    def get_booked_seat_ids(self):
        return self.booked_seat_ids
    
    def set_booked_seat_ids(self, booked_seat_ids):
        self.booked_seat_ids = booked_seat_ids
    
    def cleanup_expired_reservations(self):
        """Remove expired reservations"""
        with self.reservation_lock:
            expired_seats = []
            for seat_id, reservation in self.seat_reservations.items():
                if reservation.is_expired():
                    expired_seats.append(seat_id)
            
            for seat_id in expired_seats:
                del self.seat_reservations[seat_id]
    
    def is_seat_available(self, seat_id):
        """Check if seat is available (not booked and not reserved)"""
        self.cleanup_expired_reservations()
        
        with self.reservation_lock:
            # Check if seat is already booked
            if seat_id in self.booked_seat_ids:
                return False
            
            # Check if seat is reserved by another user
            if seat_id in self.seat_reservations:
                reservation = self.seat_reservations[seat_id]
                if reservation.is_active and not reservation.is_expired():
                    return False
            
            return True
    
    def reserve_seat(self, seat_id, user_id, hold_time_minutes=10):
        """Reserve a seat temporarily"""
        self.cleanup_expired_reservations()
        
        with self.reservation_lock:
            if not self.is_seat_available(seat_id):
                return False
            
            expiry_time = datetime.now() + timedelta(minutes=hold_time_minutes)
            reservation = SeatReservation(seat_id, user_id, expiry_time)
            self.seat_reservations[seat_id] = reservation
            return True
    
    def confirm_booking(self, seat_id, user_id):
        """Confirm the booking and remove reservation"""
        with self.reservation_lock:
            if seat_id not in self.seat_reservations:
                return False
            
            reservation = self.seat_reservations[seat_id]
            if reservation.user_id != user_id or reservation.is_expired():
                return False
            
            # Move from reservation to booked
            self.booked_seat_ids.append(seat_id)
            del self.seat_reservations[seat_id]
            return True
    
    def cancel_reservation(self, seat_id, user_id):
        """Cancel the reservation"""
        with self.reservation_lock:
            if seat_id in self.seat_reservations:
                reservation = self.seat_reservations[seat_id]
                if reservation.user_id == user_id:
                    del self.seat_reservations[seat_id]
                    return True
            return False


# Optimistic locking implementation
class OptimisticLockingBookingService:
    def __init__(self):
        pass
    
    def book_seat_optimistic(self, show, seat_id, user_id, max_retries=3):
        """Book seat using optimistic locking"""
        for attempt in range(max_retries):
            try:
                # Read current version
                current_version = show.version
                current_booked_seats = show.booked_seat_ids.copy()
                
                # Check if seat is available
                if seat_id in current_booked_seats:
                    return False, "Seat already booked"
                
                # Simulate some processing time
                time.sleep(random.uniform(0.01, 0.05))
                
                # Try to update with version check (atomic operation)
                with show.lock:
                    if show.version != current_version:
                        # Version changed, retry
                        print(f"User {user_id}: Version conflict, retrying... (attempt {attempt + 1})")
                        continue
                    
                    # Double-check seat availability
                    if seat_id in show.booked_seat_ids:
                        return False, "Seat already booked"
                    
                    # Book the seat and increment version
                    show.booked_seat_ids.append(seat_id)
                    show.version += 1
                    
                    return True, "Booking successful"
                
            except Exception as e:
                print(f"User {user_id}: Error during booking: {e}")
                continue
        
        return False, "Booking failed after retries"


# Pessimistic locking implementation
class PessimisticLockingBookingService:
    def __init__(self):
        pass
    
    def book_seat_pessimistic(self, show, seat_id, user_id):
        """Book seat using pessimistic locking"""
        with show.lock:
            if seat_id in show.booked_seat_ids:
                return False, "Seat already booked"
            
            # Simulate processing time
            time.sleep(random.uniform(0.01, 0.05))
            
            show.booked_seat_ids.append(seat_id)
            return True, "Booking successful"


# Two-phase booking implementation
class TwoPhaseBookingService:
    def __init__(self):
        pass
    
    def book_seat_two_phase(self, show, seat_id, user_id):
        """Book seat using two-phase approach (reserve + confirm)"""
        # Phase 1: Reserve the seat
        if not show.reserve_seat(seat_id, user_id):
            return False, "Seat not available"
        
        try:
            # Simulate payment processing
            print(f"User {user_id}: Processing payment for seat {seat_id}...")
            time.sleep(random.uniform(0.5, 2.0))  # Simulate payment time
            
            # Simulate payment success/failure (90% success rate)
            payment_success = random.random() < 0.9
            
            if payment_success:
                # Phase 2: Confirm the booking
                if show.confirm_booking(seat_id, user_id):
                    return True, "Booking confirmed"
                else:
                    return False, "Booking confirmation failed"
            else:
                # Cancel reservation if payment fails
                show.cancel_reservation(seat_id, user_id)
                return False, "Payment failed"
                
        except Exception as e:
            # Cancel reservation if any error occurs
            show.cancel_reservation(seat_id, user_id)
            return False, f"Booking failed: {e}"


# payment.py
class Payment:
    def __init__(self):
        self.payment_id = None
        # Other payment details


# booking.py
class Booking:
    def __init__(self):
        self.booking_id = str(uuid.uuid4())
        self.show = None
        self.booked_seats = []
        self.payment = None
        self.user_id = None
        self.booking_time = datetime.now()
        self.status = BookingStatus.PENDING
    
    def get_show(self):
        return self.show
    
    def set_show(self, show):
        self.show = show
    
    def get_booked_seats(self):
        return self.booked_seats
    
    def set_booked_seats(self, booked_seats):
        self.booked_seats = booked_seats
    
    def get_payment(self):
        return self.payment
    
    def set_payment(self, payment):
        self.payment = payment


# theatre.py
class Theatre:
    def __init__(self):
        self.theatre_id = None
        self.address = None
        self.city = None
        self.screens = []
        self.shows = []
    
    def get_theatre_id(self):
        return self.theatre_id
    
    def set_theatre_id(self, theatre_id):
        self.theatre_id = theatre_id
    
    def get_address(self):
        return self.address
    
    def set_address(self, address):
        self.address = address
    
    def get_screens(self):
        return self.screens
    
    def set_screens(self, screens):
        self.screens = screens
    
    def get_shows(self):
        return self.shows
    
    def set_shows(self, shows):
        self.shows = shows
    
    def get_city(self):
        return self.city
    
    def set_city(self, city):
        self.city = city


# movie_controller.py
class MovieController:
    def __init__(self):
        self.city_vs_movies = {}
        self.all_movies = []
    
    def add_movie(self, movie, city):
        self.all_movies.append(movie)
        
        if city not in self.city_vs_movies:
            self.city_vs_movies[city] = []
        
        self.city_vs_movies[city].append(movie)
    
    def get_movie_by_name(self, movie_name):
        for movie in self.all_movies:
            if movie.get_movie_name() == movie_name:
                return movie
        return None
    
    def get_movies_by_city(self, city):
        return self.city_vs_movies.get(city, [])


# theatre_controller.py
class TheatreController:
    def __init__(self):
        self.city_vs_theatre = {}
        self.all_theatre = []
    
    def add_theatre(self, theatre, city):
        self.all_theatre.append(theatre)
        
        if city not in self.city_vs_theatre:
            self.city_vs_theatre[city] = []
        
        self.city_vs_theatre[city].append(theatre)
    
    def get_all_show(self, movie, city):
        theatre_vs_shows = {}
        theatres = self.city_vs_theatre.get(city, [])
        
        for theatre in theatres:
            given_movie_shows = []
            shows = theatre.get_shows()
            
            for show in shows:
                if show.movie.get_movie_id() == movie.get_movie_id():
                    given_movie_shows.append(show)
            
            if given_movie_shows:
                theatre_vs_shows[theatre] = given_movie_shows
        
        return theatre_vs_shows


# book_my_show.py with concurrency control
class BookMyShow:
    def __init__(self):
        self.movie_controller = MovieController()
        self.theatre_controller = TheatreController()
        self.optimistic_service = OptimisticLockingBookingService()
        self.pessimistic_service = PessimisticLockingBookingService()
        self.two_phase_service = TwoPhaseBookingService()
    
    def create_booking_optimistic(self, user_city, movie_name, user_id, seat_number=30):
        """Create booking using optimistic locking"""
        print(f"User {user_id}: Starting optimistic booking...")
        
        interested_show = self._get_show(user_city, movie_name)
        if not interested_show:
            return
        
        success, message = self.optimistic_service.book_seat_optimistic(
            interested_show, seat_number, user_id
        )
        
        if success:
            booking = self._create_booking_object(interested_show, seat_number, user_id)
            print(f"User {user_id}: {message}")
        else:
            print(f"User {user_id}: {message}")
    
    def create_booking_pessimistic(self, user_city, movie_name, user_id, seat_number=30):
        """Create booking using pessimistic locking"""
        print(f"User {user_id}: Starting pessimistic booking...")
        
        interested_show = self._get_show(user_city, movie_name)
        if not interested_show:
            return
        
        success, message = self.pessimistic_service.book_seat_pessimistic(
            interested_show, seat_number, user_id
        )
        
        if success:
            booking = self._create_booking_object(interested_show, seat_number, user_id)
            print(f"User {user_id}: {message}")
        else:
            print(f"User {user_id}: {message}")
    
    def create_booking_two_phase(self, user_city, movie_name, user_id, seat_number=30):
        """Create booking using two-phase approach"""
        print(f"User {user_id}: Starting two-phase booking...")
        
        interested_show = self._get_show(user_city, movie_name)
        if not interested_show:
            return
        
        success, message = self.two_phase_service.book_seat_two_phase(
            interested_show, seat_number, user_id
        )
        
        if success:
            booking = self._create_booking_object(interested_show, seat_number, user_id)
            print(f"User {user_id}: {message}")
        else:
            print(f"User {user_id}: {message}")
    
    def _get_show(self, user_city, movie_name):
        """Helper method to get show"""
        movies = self.movie_controller.get_movies_by_city(user_city)
        
        interested_movie = None
        for movie in movies:
            if movie.get_movie_name() == movie_name:
                interested_movie = movie
                break
        
        if not interested_movie:
            print(f"Movie {movie_name} not found in {user_city.value}")
            return None
        
        shows_theatre_wise = self.theatre_controller.get_all_show(interested_movie, user_city)
        
        if not shows_theatre_wise:
            print(f"No shows available for {movie_name} in {user_city.value}")
            return None
        
        theatre, running_shows = next(iter(shows_theatre_wise.items()))
        return running_shows[0]
    
    def _create_booking_object(self, show, seat_number, user_id):
        """Helper method to create booking object"""
        booking = Booking()
        booking.user_id = user_id
        my_booked_seats = []
        
        for screen_seat in show.get_screen().get_seats():
            if screen_seat.get_seat_id() == seat_number:
                my_booked_seats.append(screen_seat)
        
        booking.set_booked_seats(my_booked_seats)
        booking.set_show(show)
        booking.status = BookingStatus.CONFIRMED
        
        return booking
    
    def initialize(self):
        # create movies
        self.create_movies()
        
        # create theater with screens, seats and shows
        self.create_theatre()
    
    def create_theatre(self):
        avenger_movie = self.movie_controller.get_movie_by_name("AVENGERS")
        baahubali = self.movie_controller.get_movie_by_name("BAAHUBALI")
        
        # Create INOX Theatre
        inox_theatre = Theatre()
        inox_theatre.set_theatre_id(1)
        inox_theatre.set_screens(self.create_screen())
        inox_theatre.set_city(City.BANGALORE)
        
        inox_shows = []
        inox_morning_show = self.create_shows(1, inox_theatre.get_screens()[0], avenger_movie, 8)
        inox_evening_show = self.create_shows(2, inox_theatre.get_screens()[0], baahubali, 16)
        inox_shows.extend([inox_morning_show, inox_evening_show])
        inox_theatre.set_shows(inox_shows)
        
        # Create PVR Theatre
        pvr_theatre = Theatre()
        pvr_theatre.set_theatre_id(2)
        pvr_theatre.set_screens(self.create_screen())
        pvr_theatre.set_city(City.DELHI)
        
        pvr_shows = []
        pvr_morning_show = self.create_shows(3, pvr_theatre.get_screens()[0], avenger_movie, 13)
        pvr_evening_show = self.create_shows(4, pvr_theatre.get_screens()[0], baahubali, 20)
        pvr_shows.extend([pvr_morning_show, pvr_evening_show])
        pvr_theatre.set_shows(pvr_shows)
        
        self.theatre_controller.add_theatre(inox_theatre, City.BANGALORE)
        self.theatre_controller.add_theatre(pvr_theatre, City.DELHI)
    
    def create_screen(self):
        screens = []
        screen1 = Screen()
        screen1.set_screen_id(1)
        screen1.set_seats(self.create_seats())
        screens.append(screen1)
        return screens
    
    def create_shows(self, show_id, screen, movie, show_start_time):
        show = Show()
        show.set_show_id(show_id)
        show.set_screen(screen)
        show.set_movie(movie)
        show.set_show_start_time(show_start_time)
        return show
    
    def create_seats(self):
        seats = []
        
        # 0 to 39: SILVER
        for i in range(40):
            seat = Seat()
            seat.set_seat_id(i)
            seat.set_seat_category(SeatCategory.SILVER)
            seats.append(seat)
        
        # 40 to 69: GOLD
        for i in range(40, 70):
            seat = Seat()
            seat.set_seat_id(i)
            seat.set_seat_category(SeatCategory.GOLD)
            seats.append(seat)
        
        # 70 to 99: PLATINUM
        for i in range(70, 100):
            seat = Seat()
            seat.set_seat_id(i)
            seat.set_seat_category(SeatCategory.PLATINUM)
            seats.append(seat)
        
        return seats
    
    def create_movies(self):
        # create Movie 1
        avengers = Movie()
        avengers.set_movie_id(1)
        avengers.set_movie_name("AVENGERS")
        avengers.set_movie_duration(128)
        
        # create Movie 2
        baahubali = Movie()
        baahubali.set_movie_id(2)
        baahubali.set_movie_name("BAAHUBALI")
        baahubali.set_movie_duration(180)
        
        # add movies against the cities
        self.movie_controller.add_movie(avengers, City.BANGALORE)
        self.movie_controller.add_movie(avengers, City.DELHI)
        self.movie_controller.add_movie(baahubali, City.BANGALORE)
        self.movie_controller.add_movie(baahubali, City.DELHI)


def test_concurrent_booking():
    """Test concurrent booking with different approaches"""
    
    def test_approach(approach_name, booking_method):
        print(f"\n=== Testing {approach_name} ===")
        
        book_my_show = BookMyShow()
        book_my_show.initialize()
        
        # Create multiple users trying to book the same seat
        users = [f"User{i}" for i in range(1, 6)]
        seat_number = 30
        
        def book_for_user(user_id):
            booking_method(City.BANGALORE, "BAAHUBALI", user_id, seat_number)
        
        # Execute concurrent bookings
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(book_for_user, user) for user in users]
            
            # Wait for all bookings to complete
            for future in futures:
                future.result()
        
        print(f"Final booked seats: {book_my_show._get_show(City.BANGALORE, 'BAAHUBALI').booked_seat_ids}")
    
    # Test different approaches
    book_my_show = BookMyShow()
    
    test_approach("Optimistic Locking", book_my_show.create_booking_optimistic)
    test_approach("Pessimistic Locking", book_my_show.create_booking_pessimistic)
    test_approach("Two-Phase Booking", book_my_show.create_booking_two_phase)


# Main execution
if __name__ == "__main__":
    test_concurrent_booking()