from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Tour:
    id: int
    title: str
    description: str
    price: float
    city: str
    country: str
    type: str  # 'city', 'mountain', 'elderly_mountain', 'group'
    duration_days: int
    photo_url: Optional[str] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    timezone: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    start_time: Optional[str] = None
    ticket_url: Optional[str] = None
    currency: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    external_id: Optional[str] = None
    lat: Optional[str] = None
    lng: Optional[str] = None
    categories: List[str] = field(default_factory=list)


@dataclass
class User:
    id: int
    email: str
    password_hash: str
    role: str  # 'admin' or 'client'
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    passport_number: Optional[str] = None
    passport_issued_by: Optional[str] = None
    passport_issued_date: Optional[str] = None


@dataclass
class Booking:
    id: int
    tour_id: int
    user_id: int
    booking_date: str
    travel_date: str
    passengers: int
    total_price: float
    status: str  # 'pending', 'confirmed', 'cancelled'


@dataclass
class Feedback:
    id: int
    user_id: int
    subject: str
    message: str
    created_at: str
    status: str  # 'new', 'in_progress', 'resolved', 'closed'
    admin_response: Optional[str] = None
    admin_id: Optional[int] = None
    responded_at: Optional[str] = None
    priority: str = 'normal'  # 'low', 'normal', 'high', 'urgent'
    category: str = 'general'  # 'general', 'booking', 'technical', 'complaint', 'suggestion'

