
# 📘 Parking Lot LLD UML Diagram Explanation

## 🔗 Relationships and Multiplicity
In UML diagrams, the numbers like `1..1`, `0..1`, `0..*` indicate **multiplicity**, showing how many instances of a class relate to another.

- `1..1`: Exactly **one**
- `0..1`: **Zero or one**
- `0..*`: **Zero or many**
- `1..*`: **One or more**

---

## 🧱 Class Descriptions and Relationships

### 🚗 Vehicle
- **Attributes:** `vehicle_number`, `vehicle_type`
- **Relationships:**  
  - `1..0..1` with `Ticket`: A ticket can be linked to one vehicle, and a vehicle may or may not have a ticket.

---

### 🎫 Ticket
- **Attributes:** `entry_time`, `vehicle`, `parking_spot`
- **Relationships:**
  - `1..1` with `ParkingSpot`: Ticket is tied to a specific parking spot.
  - `1..1` with `Vehicle`: Each ticket has one vehicle.
  - `1..1` with `ExitGate`: Used to process the exit.

---

### 🅿️ ParkingSpot
- **Attributes:** `id`, `is_empty`, `price`, `vehicle`
- **Relationships:**
  - `1..0..*` with `ParkingSpotManager`: Managed by one or more managers.
  - Tied to `Vehicle` and `Ticket` when occupied.

---

### 🧠 ParkingSpotManager
- **Attributes:** `parking_spots` (a collection)
- **Relationships:**
  - Manages multiple `ParkingSpot`s.
  - Used by the `ParkingSpotFactory`.

---

### 🏭 ParkingSpotFactory
- **Function:** `get_psm(vehicle)` returns correct manager based on vehicle type.
- **Relationships:**
  - Associated with multiple `ParkingSpotManager`s.
  - Used by the `EntranceGate`.

---

### 🚪 EntranceGate
- **Attributes:** `factory`, `manager`
- **Responsibilities:**
  - Uses `ParkingSpotFactory` to find the correct manager.
  - Finds and books space.
  - Generates a `Ticket`.

---

### 🚪 ExitGate
- **Attributes:** `ticket`
- **Responsibilities:**
  - Uses the `Ticket` to compute parking cost.
  - Frees the associated `ParkingSpot`.

---

## 📌 Summary of Key Multiplicity Relationships

| From → To                         | Multiplicity | Description |
|----------------------------------|--------------|-------------|
| `Vehicle → Ticket`               | 0..1         | A vehicle may have a ticket. |
| `Ticket → Vehicle`               | 1..1         | Each ticket must have one vehicle. |
| `Ticket → ParkingSpot`           | 1..1         | Each ticket is assigned to one parking spot. |
| `ExitGate → Ticket`              | 1..1         | Exit gate processes one ticket at a time. |
| `ParkingSpotManager → ParkingSpot` | 0..*       | Manages zero or more parking spots. |
| `ParkingSpotFactory → ParkingSpotManager` | 0..* | Can produce multiple managers. |
| `EntranceGate → Factory/Manager` | 1..1         | Each gate uses one factory and one manager. |
