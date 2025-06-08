Great question! You're absolutely right that we need to handle concurrency to prevent race conditions when multiple users try to book the same seat simultaneously. Let me show you several approaches to implement this, including optimistic locking.I've implemented comprehensive concurrency control for the BookMyShow system with three different approaches. Here's what I've added:

## 🔒 **Three Concurrency Control Approaches:**

### 1. **Optimistic Locking** ✅
- **How it works**: Uses version numbers to detect conflicts
- **Process**: Read → Process → Check version → Update if unchanged
- **Best for**: High concurrency, low conflict scenarios
- **Retries**: Automatically retries on version conflicts

### 2. **Pessimistic Locking** 🔒
- **How it works**: Acquires lock before any operation
- **Process**: Lock → Check → Update → Release
- **Best for**: High conflict scenarios
- **Trade-off**: Lower throughput but guaranteed consistency

### 3. **Two-Phase Booking** 🎯
- **How it works**: Reserve → Process Payment → Confirm/Cancel
- **Process**: 
  - Phase 1: Reserve seat with timeout (10 min default)
  - Phase 2: Process payment and confirm
- **Best for**: Real-world scenarios with payment processing
- **Features**: Automatic cleanup of expired reservations

## 🛡️ **Key Concurrency Features:**

### **Race Condition Prevention:**
```python
# Optimistic Locking
if show.version != current_version:
    # Retry - someone else modified
    continue

# Pessimistic Locking  
with show.lock:
    # Exclusive access guaranteed

# Two-Phase
show.reserve_seat(seat_id, user_id)  # Temporary hold
show.confirm_booking(seat_id, user_id)  # Final booking
```

### **Thread Safety:**
- `threading.RLock()` for reentrant locks
- Atomic operations with version checking
- Proper cleanup of expired reservations

### **Timeout Management:**
- Seat reservations expire after 10 minutes
- Automatic cleanup of expired reservations
- Payment timeout simulation

## 🧪 **Testing Concurrent Scenarios:**

The code includes a comprehensive test that simulates 5 users trying to book the same seat simultaneously:

```python
def test_concurrent_booking():
    # Tests all three approaches with 5 concurrent users
    # Only one user should succeed, others should fail gracefully
```

## 📊 **When to Use Each Approach:**

| Approach | Use Case | Pros | Cons |
|----------|----------|------|------|
| **Optimistic** | Low conflict rate, high throughput needed | Fast, scalable | Retries needed |
| **Pessimistic** | High conflict rate, simple logic needed | Guaranteed consistency | Lower throughput |
| **Two-Phase** | Real payment processing, user experience | Realistic, holds seats during payment | More complex |

## 🎯 **Real-World Considerations:**

1. **Database Integration**: In production, you'd use database-level locking
2. **Distributed Systems**: Consider using Redis or database locks across servers
3. **User Experience**: Two-phase approach provides the best UX
4. **Performance**: Optimistic locking scales better under load

## 🚀 **Running the Code:**

The test will show output like:
```
=== Testing Optimistic Locking ===
User User1: Booking successful
User User2: Version conflict, retrying... (attempt 1)
User User2: Seat already booked
User User3: Seat already booked
...

=== Testing Two-Phase Booking ===
User User1: Processing payment for seat 30...
User User1: Booking confirmed
User User2: Seat not available
...
```

This implementation ensures that no two users can book the same seat, handles race conditions gracefully, and provides different strategies based on your specific requirements!