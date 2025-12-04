from typing import List, Optional
from datetime import datetime
from ..models import Booking


class BookingRepository:
    def __init__(self):
        self._bookings: List[Booking] = []
        self._next_id = 1

    def get_next_id(self) -> int:
        """Get the next available booking ID"""
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def add_booking(self, booking: Booking) -> None:
        """Add a new booking to the repository"""
        self._bookings.append(booking)

    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID"""
        for booking in self._bookings:
            if booking.id == booking_id:
                return booking
        return None

    def get_by_user_id(self, user_id: int) -> List[Booking]:
        """Get all bookings for a specific user"""
        return [booking for booking in self._bookings if booking.user_id == user_id]

    def get_by_tour_id(self, tour_id: int) -> List[Booking]:
        """Get all bookings for a specific tour"""
        return [booking for booking in self._bookings if booking.tour_id == tour_id]

    def get_all(self) -> List[Booking]:
        """Get all bookings"""
        return self._bookings.copy()

    def update_booking(self, booking: Booking) -> bool:
        """Update an existing booking"""
        for i, existing_booking in enumerate(self._bookings):
            if existing_booking.id == booking.id:
                self._bookings[i] = booking
                return True
        return False

    def cancel_booking(self, booking_id: int) -> bool:
        """Cancel a booking by setting status to cancelled"""
        for booking in self._bookings:
            if booking.id == booking_id:
                booking.status = "cancelled"
                return True
        return False

    def get_confirmed_bookings_for_tour(self, tour_id: int) -> List[Booking]:
        """Get all confirmed bookings for a specific tour"""
        return [
            booking for booking in self._bookings 
            if booking.tour_id == tour_id and booking.status == "confirmed"
        ]


# Global instance
booking_repository = BookingRepository()
