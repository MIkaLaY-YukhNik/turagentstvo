from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_babel import get_locale, refresh
from datetime import datetime
from ..repository.tours_repo import tours_repository
from ..repository.user_repo import user_repository
from ..repository.booking_repo import booking_repository
from ..repository.feedback_repo import feedback_repository
from ..services.weather_service import weather_service
from ..services.maps_service import build_map_embed
from ..models import Booking, User, Feedback
from werkzeug.security import generate_password_hash


public_bp = Blueprint("public", __name__)


@public_bp.get("/")
def home():
    featured = tours_repository.list_featured(limit=6)
    return render_template("home.html", tours=featured)


@public_bp.get("/search")
def search():
    query = {
        "location": request.args.get("location", ""),
        "type": request.args.get("type", ""),
        "min_price": request.args.get("min_price", type=float),
        "max_price": request.args.get("max_price", type=float),
        "duration": request.args.get("duration", type=int),
        "keyword": request.args.get("keyword", ""),
    }
    results = tours_repository.search(**query)
    return render_template("search.html", tours=results, query=query)


@public_bp.get("/tour/<int:tour_id>")
def tour_detail(tour_id: int):
    tour = tours_repository.get_by_id(tour_id)
    if not tour:
        return render_template("404.html"), 404

    weather = weather_service.get_weather(tour.city, tour.country)
    weather_ok = weather_service.is_ok_for_elderly_mountain(weather) if tour.type == "elderly_mountain" else None
    map_url = build_map_embed(tour.city, tour.country, tour.lat, tour.lng)
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("tour_detail.html", tour=tour, weather=weather, weather_ok=weather_ok, map_url=map_url, today=today)


@public_bp.post("/book/<int:tour_id>")
def book_tour(tour_id: int):
    tour = tours_repository.get_by_id(tour_id)
    if not tour:
        return render_template("404.html"), 404
    
    # Get form data
    travel_date = request.form.get("travel_date")
    try:
        passengers = int(request.form.get("passengers", 1))
        if passengers < 1 or passengers > 10:
            flash("Количество пассажиров должно быть от 1 до 10", "error")
            return redirect(url_for("public.tour_detail", tour_id=tour_id))
    except ValueError:
        flash("Неверное количество пассажиров", "error")
        return redirect(url_for("public.tour_detail", tour_id=tour_id))
    
    # Validate travel date
    if not travel_date:
        flash("Пожалуйста, выберите дату поездки", "error")
        return redirect(url_for("public.tour_detail", tour_id=tour_id))
    
    # Check if date is in the future
    try:
        travel_date_obj = datetime.strptime(travel_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        
        if travel_date_obj < today:
            flash("Дата поездки не может быть в прошлом. Пожалуйста, выберите будущую дату.", "error")
            return redirect(url_for("public.tour_detail", tour_id=tour_id))
            
        # Optional: Check if date is too far in the future (e.g., more than 1 year)
        max_future_date = today.replace(year=today.year + 1)
        if travel_date_obj > max_future_date:
            flash("Дата поездки не может быть более чем на год в будущем", "error")
            return redirect(url_for("public.tour_detail", tour_id=tour_id))
            
    except ValueError:
        flash("Неверный формат даты", "error")
        return redirect(url_for("public.tour_detail", tour_id=tour_id))
    
    # Check if user is logged in
    if not session.get("user_id"):
        # If not logged in, redirect to registration with booking data
        session["booking_data"] = {
            "tour_id": tour_id,
            "travel_date": travel_date,
            "passengers": passengers
        }
        flash("Для завершения бронирования необходимо зарегистрироваться", "info")
        return redirect(url_for("auth.register"))
    
    # User is logged in, create booking
    user_id = session["user_id"]
    unit_price = (
        tour.min_price
        if tour.min_price is not None
        else (tour.max_price if tour.max_price is not None else tour.price)
    ) or 0
    total_price = unit_price * passengers
    
    # Create booking
    booking_id = booking_repository.get_next_id()
    booking = Booking(
        id=booking_id,
        tour_id=tour_id,
        user_id=user_id,
        booking_date=datetime.now().strftime("%Y-%m-%d"),
        travel_date=travel_date,
        passengers=passengers,
        total_price=total_price,
        status="confirmed"
    )
    
    booking_repository.add_booking(booking)
    
    # Get user info for confirmation
    user = user_repository.get_by_id(user_id)
    
    return render_template(
        "booking.html",
        tour=tour,
        booking=booking,
        user=user,
        passengers=passengers,
    )


@public_bp.get("/my-bookings")
def my_bookings():
    if not session.get("user_id"):
        flash("Необходимо войти в систему для просмотра бронирований", "warning")
        return redirect(url_for("auth.login"))
    
    user_id = session["user_id"]
    bookings = booking_repository.get_by_user_id(user_id)
    
    # Get tour details for each booking
    bookings_with_tours = []
    for booking in bookings:
        tour = tours_repository.get_by_id(booking.tour_id)
        bookings_with_tours.append({
            "booking": booking,
            "tour": tour
        })
    
    return render_template("my_bookings.html", bookings=bookings_with_tours)


@public_bp.get("/booking/<int:booking_id>")
def booking_confirmation(booking_id: int):
    booking = booking_repository.get_by_id(booking_id)
    if not booking:
        return render_template("404.html"), 404
    
    tour = tours_repository.get_by_id(booking.tour_id)
    user = user_repository.get_by_id(booking.user_id)
    
    return render_template("booking.html", 
                         tour=tour, 
                         booking=booking, 
                         user=user,
                         passengers=booking.passengers)


@public_bp.post("/booking/<int:booking_id>/cancel")
def cancel_booking(booking_id: int):
    if not session.get("user_id"):
        flash("Необходимо войти в систему для удаления бронирования", "warning")
        return redirect(url_for("auth.login"))
    
    booking = booking_repository.get_by_id(booking_id)
    if not booking:
        flash("Бронирование не найдено", "error")
        return redirect(url_for("public.my_bookings"))
    
    # Check if user owns this booking
    if booking.user_id != session["user_id"]:
        flash("У вас нет прав для удаления этого бронирования", "error")
        return redirect(url_for("public.my_bookings"))
    
    # Check if booking can be cancelled (e.g., not too close to travel date)
    try:
        travel_date_obj = datetime.strptime(booking.travel_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        
        # Allow cancellation up to 3 days before travel
        min_cancel_date = today.replace(day=today.day + 3) if today.day <= 28 else today.replace(month=today.month + 1, day=3)
        
        if travel_date_obj <= min_cancel_date:
            flash("Бронирование нельзя отменить менее чем за 3 дня до поездки", "error")
            return redirect(url_for("public.my_bookings"))
            
    except ValueError:
        flash("Ошибка в дате поездки", "error")
        return redirect(url_for("public.my_bookings"))
    
    # Cancel the booking (set status to cancelled instead of deleting)
    if booking_repository.cancel_booking(booking_id):
        flash("Бронирование успешно отменено", "success")
    else:
        flash("Ошибка при отмене бронирования", "error")
    
    return redirect(url_for("public.my_bookings"))


@public_bp.route("/set_language/<language>")
def set_language(language):
    """Set the language for the current session"""
    if language in ['ru', 'en', 'es']:
        session['language'] = language
        refresh()  # Refresh the locale
    return redirect(request.referrer or url_for('public.home'))


@public_bp.get("/feedback")
def feedback_form():
    """Show feedback form"""
    if not session.get("user_id"):
        flash("Необходимо войти в систему для отправки обратной связи", "warning")
        return redirect(url_for("auth.login"))
    return render_template("feedback.html")


@public_bp.post("/feedback")
def submit_feedback():
    """Submit feedback from user"""
    if not session.get("user_id"):
        flash("Необходимо войти в систему для отправки обратной связи", "warning")
        return redirect(url_for("auth.login"))
    
    user_id = session["user_id"]
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()
    category = request.form.get("category", "general")
    priority = request.form.get("priority", "normal")
    
    # Validation
    if not subject:
        flash("Пожалуйста, укажите тему сообщения", "error")
        return redirect(url_for("public.feedback_form"))
    
    if not message:
        flash("Пожалуйста, напишите сообщение", "error")
        return redirect(url_for("public.feedback_form"))
    
    if len(subject) > 200:
        flash("Тема сообщения слишком длинная (максимум 200 символов)", "error")
        return redirect(url_for("public.feedback_form"))
    
    if len(message) > 2000:
        flash("Сообщение слишком длинное (максимум 2000 символов)", "error")
        return redirect(url_for("public.feedback_form"))
    
    # Create feedback
    feedback_id = feedback_repository.get_next_id()
    feedback = Feedback(
        id=feedback_id,
        user_id=user_id,
        subject=subject,
        message=message,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        status="new",
        priority=priority,
        category=category
    )
    
    feedback_repository.add_feedback(feedback)
    flash("Ваше сообщение отправлено! Мы ответим в ближайшее время.", "success")
    return redirect(url_for("public.my_feedback"))


@public_bp.get("/my-feedback")
def my_feedback():
    """Show user's feedback history"""
    if not session.get("user_id"):
        flash("Необходимо войти в систему для просмотра обратной связи", "warning")
        return redirect(url_for("auth.login"))
    
    user_id = session["user_id"]
    feedback_list = feedback_repository.get_by_user_id(user_id)
    
    return render_template("my_feedback.html", feedback_list=feedback_list)


