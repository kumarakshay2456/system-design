from constant import City, SeatCategory


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


# show.py
class Show:
    def __init__(self):
        self.show_id = None
        self.movie = None
        self.screen = None
        self.show_start_time = None
        self.booked_seat_ids = []
    
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


# payment.py
class Payment:
    def __init__(self):
        self.payment_id = None
        # Other payment details


# booking.py
class Booking:
    def __init__(self):
        self.show = None
        self.booked_seats = []
        self.payment = None
    
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


# book_my_show.py
class BookMyShow:
    def __init__(self):
        self.movie_controller = MovieController()
        self.theatre_controller = TheatreController()
    
    def create_booking(self, user_city, movie_name):
        # 1. search movie by my location
        movies = self.movie_controller.get_movies_by_city(user_city)
        
        # 2. select the movie which you want to see
        interested_movie = None
        for movie in movies:
            if movie.get_movie_name() == movie_name:
                interested_movie = movie
                break
        
        if not interested_movie:
            print(f"Movie {movie_name} not found in {user_city.value}")
            return
        
        # 3. get all show of this movie in the location
        shows_theatre_wise = self.theatre_controller.get_all_show(interested_movie, user_city)
        
        if not shows_theatre_wise:
            print(f"No shows available for {movie_name} in {user_city.value}")
            return
        
        # 4. select the particular show user is interested in
        theatre, running_shows = next(iter(shows_theatre_wise.items()))
        interested_show = running_shows[0]
        
        # 5. select the seat
        seat_number = 30
        booked_seats = interested_show.get_booked_seat_ids()
        
        if seat_number not in booked_seats:
            booked_seats.append(seat_number)
            
            # start payment
            booking = Booking()
            my_booked_seats = []
            
            for screen_seat in interested_show.get_screen().get_seats():
                if screen_seat.get_seat_id() == seat_number:
                    my_booked_seats.append(screen_seat)
            
            booking.set_booked_seats(my_booked_seats)
            booking.set_show(interested_show)
            
            print("BOOKING SUCCESSFUL")
        else:
            print("seat already booked, try again")
            return
    
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
        show.set_show_start_time(show_start_time)  # 24 hrs time ex: 14 means 2pm and 8 means 8AM
        return show
    
    def create_seats(self):
        # creating 100 seats for testing purpose
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


# Main execution
if __name__ == "__main__":
    book_my_show = BookMyShow()
    book_my_show.initialize()
    
    # user1
    book_my_show.create_booking(City.BANGALORE, "BAAHUBALI")
    # user2
    book_my_show.create_booking(City.BANGALORE, "BAAHUBALI")