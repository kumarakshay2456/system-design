🔧 1. Class Design & OOP Concepts

Q1. Can you walk me through the overall class diagram of your BookMyShow system?

Answer:

	•	Entities: Movie, Theatre, Screen, Seat, Show, Booking, Payment
	•	Controllers: MovieController, TheatreController
	•	Central Coordinator: BookMyShow
	•	Relationships:
	•	Theatre has many Screens and Shows
	•	Screen has many Seats
	•	Show uses a Screen and references a Movie
	•	Booking has a Show, selected Seats, and a Payment

Q2. Why did you choose to separate MovieController and TheatreController?

Answer:
To follow the Single Responsibility Principle, each controller manages its own domain:

	•	MovieController manages movies per city
	•	TheatreController manages theatres and shows per city

This modularity makes the system easier to test and extend.

Q3. Is your class design easily extensible to support multiple cities and languages?

Answer:
Yes.

	•	Cities are abstracted as an enum (City), and can easily be extended.
	•	For multiple languages, we can extend the Movie class to include a language field or a list of available languages.

📦 2. Booking & Seat Management

Q4. How are you handling concurrent bookings for the same seat?

Answer:
In the current in-memory implementation, concurrency is not handled properly.
In a real-world scenario, we’d use:

	•	Pessimistic locking (database row lock)
	•	or Optimistic locking (version field)
	•	or distributed lock (like Redis Redlock)
To avoid race conditions during seat selection.

Q5. What happens if two users try to book the same seat at the same time?

Answer:
In this current design, both threads might pass the if seat_number not in booked_seats check before one updates.
To fix this:

	•	Use a thread-safe set (e.g., threading.Lock)
	•	or atomic DB operation

📅 3. Design Extension & Scalability

Q6. How would you support dynamic pricing or offers?

Answer:

	•	Add a price field in Seat or associate pricing per seat category.
	•	Add a PricingService to compute real-time pricing.
	•	Add Promotion or Coupon entities linked to Booking.

Q7. How would you support cancellation and refunds?

Answer:

	•	Add BookingStatus enum (BOOKED, CANCELLED)
	•	On cancel:
	•	Change status
	•	Free up seats in Show.booked_seat_ids
	•	Trigger refund via Payment service

Q8. How will you support different show timings across time zones?

Answer:

	•	Store all times in UTC
	•	Convert to local time at UI using user’s timezone
	•	Add a timezone field in Theatre

🌐 4. API Layer & Usage Flow

Q9. Describe the steps from selecting a movie to booking a seat.

Answer:

	1.	User selects city → fetch movies via get_movies_by_city
	2.	Select movie → fetch shows via get_all_show
	3.	Pick a show → choose seats
	4.	System checks seat availability
	5.	Creates Booking → calls Payment → confirms booking

Q10. How would you design APIs for BookMyShow?

Answer:
Design RESTful endpoints like:

	•	GET /cities
	•	GET /movies?city=Delhi
	•	GET /shows?movie_id=1&city=Delhi
	•	POST /booking (with show_id + seat_ids)
	•	POST /payment

🛠️ 5. Code Optimization and Improvements

Q11. Your current design uses many get_*/set_* methods. Is this Pythonic?

Answer:
No, it’s Java-style.
In Python, it’s better to use:

	•	Properties (@property, @<attr>.setter)
	•	or direct attribute access if encapsulation isn’t needed

Q12. What data structures are used to map shows and cities? Are they optimal?

Answer:
Yes:

	•	dict is used for city_vs_movies and city_vs_theatre, providing O(1) lookup
	•	Can scale for millions of users by shifting to DB-backed indices or caching (e.g., Redis)

🔒 6. Security and Validation

Q13. How would you ensure only valid seats are selected for a show?

Answer:

	•	Validate seat_id exists in the Show.screen.seats
	•	Check if seat_id is already booked
	•	Use transaction locks (if database is used) to prevent double booking

Q14. Is there user authentication and access control in your design?

Answer:
Not yet implemented.
We can:

	•	Add User entity
	•	Implement sessions or JWT tokens
	•	Link bookings to users

📊 7. Database Design & Persistence

Q15. How would you persist this data?

Answer:
Use an RDBMS like PostgreSQL. Sample schema:

	•	movies(id, name, duration)
	•	theatres(id, city, address)
	•	screens(id, theatre_id)
	•	seats(id, screen_id, category)
	•	shows(id, screen_id, movie_id, start_time)
	•	bookings(id, show_id, seat_ids[], payment_id)
	•	payments(id, status, amount)

Q16. How do you scale this system to handle millions of users?

Answer:

	•	Use caching for showtimes and seat availability (Redis)
	•	Shard data by city or theatre
	•	Use CDN for static content
	•	Use message queues for sending notifications, processing payments
	•	Database replication and read-write separation

🧩 8. Edge Cases & Fault Handling

Q17. What if payment fails after seat booking?

Answer:

	•	Use temporary holds on seat for a limited time
	•	If payment fails within timeout (e.g., 5 minutes), release the seat

Q18. Can a user book multiple seats in one go?

Answer:
Not currently.
Extend create_booking() to take a list of seat numbers and verify all are available atomically.

✅ Final Tips

	•	Follow SOLID principles
	•	Use UML or Class Diagrams to explain
	•	Be ready to extend the design (snacks, reviews, coupons)
	•	Discuss concurrency & data integrity
	•	Explain how to test and monitor the system
