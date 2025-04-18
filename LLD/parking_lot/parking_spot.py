from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
import uuid


# ------------------- Vehicle ----------------------

class Vehicle:
    def __init__(self, vehicle_number: str, vehicle_type: str):
        self.vehicle_number = vehicle_number
        self.vehicle_type = vehicle_type  # e.g., 'two_wheeler', 'four_wheeler'


# ------------------- Parking Spot -----------------

class ParkingSpot(ABC):
    def __init__(self, spot_id: str, price: float):
        self.id = spot_id
        self.price = price
        self.is_empty = True
        self.vehicle: Optional[Vehicle] = None

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        if self.is_empty:
            self.vehicle = vehicle
            self.is_empty = False
            return True
        return False

    def remove_vehicle(self) -> Optional[Vehicle]:
        if not self.is_empty:
            vehicle = self.vehicle
            self.vehicle = None
            self.is_empty = True
            return vehicle
        return None


class TwoWheelerParkingSpot(ParkingSpot):
    def __init__(self, spot_id: str):
        super().__init__(spot_id, price=10.0)


class FourWheelerParkingSpot(ParkingSpot):
    def __init__(self, spot_id: str):
        super().__init__(spot_id, price=50.0)


# ------------------- Ticket -----------------------

class Ticket:
    def __init__(self, vehicle: Vehicle, parking_spot: ParkingSpot):
        self.ticket_id = str(uuid.uuid4())
        self.entry_time = datetime.now()
        self.vehicle = vehicle
        self.parking_spot = parking_spot


# ------------------- Parking Spot Manager ---------

class ParkingSpotManager(ABC):
    def __init__(self):
        self.spots: List[ParkingSpot] = []

    def add_space(self, spot: ParkingSpot):
        self.spots.append(spot)

    def remove_parking(self, spot_id: str):
        self.spots = [spot for spot in self.spots if spot.id != spot_id]

    def find_parking_space(self) -> Optional[ParkingSpot]:
        for spot in self.spots:
            if spot.is_empty:
                return spot
        return None

    def park_vehicle(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        spot = self.find_parking_space()
        if spot and spot.park_vehicle(vehicle):
            return spot
        return None

    def remove_vehicle(self, vehicle_number: str) -> Optional[ParkingSpot]:
        for spot in self.spots:
            if spot.vehicle and spot.vehicle.vehicle_number == vehicle_number:
                spot.remove_vehicle()
                return spot
        return None


class TwoWheelerParkingSpotManager(ParkingSpotManager):
    pass


class FourWheelerParkingSpotManager(ParkingSpotManager):
    pass


# ------------------- Factory ----------------------

class ParkingSpotFactory:
    def __init__(self, two_mgr: TwoWheelerParkingSpotManager, four_mgr: FourWheelerParkingSpotManager):
        self.two_mgr = two_mgr
        self.four_mgr = four_mgr

    def get_psm(self, vehicle: Vehicle) -> ParkingSpotManager:
        if vehicle.vehicle_type == 'two_wheeler':
            return self.two_mgr
        elif vehicle.vehicle_type == 'four_wheeler':
            return self.four_mgr
        else:
            raise Exception("Unknown vehicle type")


# ------------------- Entrance Gate ----------------

class EntranceGate:
    def __init__(self, ps_factory: ParkingSpotFactory):
        self.ps_factory = ps_factory

    def find_space(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        manager = self.ps_factory.get_psm(vehicle)
        return manager.find_parking_space()

    def book_space(self, vehicle: Vehicle) -> Optional[Ticket]:
        manager = self.ps_factory.get_psm(vehicle)
        spot = manager.park_vehicle(vehicle)
        if spot:
            return Ticket(vehicle, spot)
        return None


# ------------------- Exit Gate --------------------

class ExitGate:
    def __init__(self, ps_factory: ParkingSpotFactory):
        self.ps_factory = ps_factory

    def cost_computation(self, ticket: Ticket) -> float:
        duration = (datetime.now() - ticket.entry_time).seconds / 60  # in minutes
        price = ticket.parking_spot.price
        return round(price * max(1, duration / 60), 2)  # Charge per hour

    def free_the_space(self, ticket: Ticket):
        manager = self.ps_factory.get_psm(ticket.vehicle)
        manager.remove_vehicle(ticket.vehicle.vehicle_number)


# ------------------- Example Test ------------------

def test_parking_lot():
    # Setup
    two_mgr = TwoWheelerParkingSpotManager()
    four_mgr = FourWheelerParkingSpotManager()

    # Add parking spots
    for i in range(3):
        two_mgr.add_space(TwoWheelerParkingSpot(f"TW-{i+1}"))
        four_mgr.add_space(FourWheelerParkingSpot(f"FW-{i+1}"))

    factory = ParkingSpotFactory(two_mgr, four_mgr)
    entrance = EntranceGate(factory)
    exit_gate = ExitGate(factory)

    # Vehicle comes in
    vehicle1 = Vehicle("KA01AB1234", "two_wheeler")
    ticket1 = entrance.book_space(vehicle1)
    print(f"Ticket issued: {ticket1.ticket_id} for vehicle {vehicle1.vehicle_number}")

    # Wait some time if needed
    import time
    time.sleep(2)

    # Exit
    cost = exit_gate.cost_computation(ticket1)
    print(f"Parking cost for vehicle {vehicle1.vehicle_number}: ₹{cost}")
    exit_gate.free_the_space(ticket1)
    print(f"Spot {ticket1.parking_spot.id} is now free again.")

if __name__ == "__main__":
    test_parking_lot()