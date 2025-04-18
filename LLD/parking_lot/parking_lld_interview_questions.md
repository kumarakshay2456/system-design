
# 🚗 Parking Lot LLD - Interview Preparation

This document contains possible interview questions and well-structured answers related to a Parking Lot Low-Level Design (LLD) system implemented in Python.

---

## 🔍 1. Design-Oriented Questions

### Q: Why did you choose to use abstract classes for `ParkingSpot` and `ParkingSpotManager`?
**A:** Abstract classes provide a contract for common functionality while allowing specific implementations to vary. Both two-wheel and four-wheel managers share logic but differ in price or allocation logic.

### Q: How does the Factory Pattern help in this system?
**A:** It encapsulates logic to select the appropriate manager based on vehicle type. This simplifies the code and supports new vehicle types in the future.

### Q: What design patterns have you used here?
- Factory Pattern
- Strategy Pattern (conceptually via pricing)
- Single Responsibility Principle
- Open/Closed Principle

### Q: Can this design scale to support multiple parking lots or floors?
**A:** Yes. Introduce a `ParkingLot` class that manages multiple managers. A central manager can coordinate across lots/floors.

### Q: How would you design a real-time dashboard showing available spots?
**A:** Expose APIs that return availability. Push updates via WebSocket. Cache availability in Redis for fast access.

### Q: How would you ensure thread-safety if multiple gates operate simultaneously?
**A:** Use `threading.Lock` or Redis-based locking. For distributed systems, use DB-level transactions or optimistic/pessimistic locking.

### Q: Why did you keep pricing in the spot instead of a config?
**A:** Different spots may have different prices (e.g., covered vs uncovered). This provides flexibility.

### Q: What if prices vary by hour or demand?
**A:** Use a `PricingService` to compute dynamic pricing during billing.

### Q: How would you extend the design for reserved parking?
**A:** Add an `is_reserved` flag and maintain a reservation mapping for vehicles or slots.

---

## 🛠️ 2. Code Implementation Questions

### Q: What are the time complexities of `park_vehicle` and `remove_vehicle`?
**A:** O(n). Use a heap or queue for O(1) access and a map from vehicle → spot.

### Q: Could you improve available spot search?
**A:** Maintain a min-heap of available spots. Push/pop on parking/unparking.

### Q: How would you refactor to use a database?
**A:** Abstract storage using repositories and use an ORM or SQL layer.

### Q: Can you mock or test this system?
```python
from unittest.mock import MagicMock

def test_entrance_gate_booking():
    vehicle = Vehicle("AB123", "two_wheeler")
    manager = MagicMock()
    manager.park_vehicle.return_value = MagicMock()
    factory = MagicMock()
    factory.get_psm.return_value = manager

    gate = EntranceGate(factory)
    ticket = gate.book_space(vehicle)
    assert ticket is not None
```

---

## 🔄 3. System Behavior Questions

### Q: What if all spots are full?
**A:** Return `None` from `find_parking_space()`, show "Parking Full".

### Q: What if someone exits without a ticket?
**A:** Lookup by vehicle number and manually compute cost or charge a penalty.

### Q: What if a vehicle enters twice?
**A:** Maintain active parking state and deny re-entry.

### Q: Can multiple spots have same ID?
**A:** No. Validate uniqueness in manager or DB constraint.

### Q: What if a vehicle parks in wrong spot type?
**A:** Factory ensures correct manager; validate spot before assignment.

---

## 🧠 4. Advanced Topics

### Q: How to support multi-city parking?
**A:** Deploy regional services. Central coordinator tracks regions. Sync using Kafka.

### Q: How to persist tickets?
**A:** Store in DB and optionally cache in Redis.

### Q: How to handle concurrency?
**A:** Lock spots or use distributed locks.

### Q: Can message queues help?
**A:** Yes, log entry/exit events for analytics, billing, alerting.

---

## 🧩 5. Extensibility

### Q: How to support EV charging?
**A:** Add `EVChargingSpot`, `charging_speed`, new manager, update factory.

### Q: How to support monthly passes?
**A:** Add `User` model and pass validation in billing step.

### Q: How to notify users of free spots?
**A:** Integrate with SMS/email APIs and notify on low availability.

### Q: Can it support mobile payments?
**A:** Yes. Use QR codes, scan at gates, integrate with payment gateways.

---

## 🧪 6. Testing and Quality

### Q: How to test this system?
- Unit tests for components
- Integration test for parking flow
- Time mocking for billing logic

### Q: Edge cases to test?
- Full lot, invalid vehicle, duplicate vehicle number, invalid ticket

### Q: Sample unit test?
```python
def test_two_wheeler_parking():
    mgr = TwoWheelerParkingSpotManager()
    spot = TwoWheelerParkingSpot("T-01")
    mgr.add_space(spot)
    vehicle = Vehicle("MH12DE1432", "two_wheeler")
    parked_spot = mgr.park_vehicle(vehicle)
    assert parked_spot == spot
    assert not spot.is_empty
```

---

