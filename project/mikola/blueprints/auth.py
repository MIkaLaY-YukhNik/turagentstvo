from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ..repository.user_repo import user_repository
from ..models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login():
    is_admin_mode = request.args.get("admin") == "1"
    return render_template("auth/login.html", admin_mode=is_admin_mode)


@auth_bp.post("/login")
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    admin_mode = request.form.get("admin") == "1"
    
    user = user_repository.get_by_email(email)
    
    if user and check_password_hash(user.password_hash, password):
        session["user_id"] = user.id
        session["email"] = user.email
        session["role"] = user.role
        flash("Успешный вход в систему!", "success")
        if admin_mode and user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("public.home"))
    else:
        flash("Неверный email или пароль", "error")
        return redirect(url_for("auth.login", admin=(1 if admin_mode else None)))


@auth_bp.get("/register")
def register():
    return render_template("auth/register.html")


@auth_bp.post("/register")
def register_post():
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    phone = request.form.get("phone")
    
    # Validation
    if password != confirm_password:
        flash("Пароли не совпадают", "error")
        return redirect(url_for("auth.register"))
    
    if len(password) < 6:
        flash("Пароль должен содержать минимум 6 символов", "error")
        return redirect(url_for("auth.register"))
    
    if user_repository.get_by_email(email):
        flash("Пользователь с таким email уже существует", "error")
        return redirect(url_for("auth.register"))
    
    # Passport data no longer required/collected
    
    # Create new user
    new_id = user_repository.get_next_id()
    user = User(
        id=new_id,
        email=email,
        password_hash=generate_password_hash(password),
        role="client",
        first_name=first_name,
        last_name=last_name,
        phone=phone
    )
    
    user_repository.add_user(user)
    
    # Check if there's pending booking data
    booking_data = session.get("booking_data")
    if booking_data:
        # Validate booking date before creating booking
        try:
            travel_date_obj = datetime.strptime(booking_data["travel_date"], "%Y-%m-%d").date()
            today = datetime.now().date()
            
            if travel_date_obj < today:
                session.pop("booking_data", None)  # Clear invalid booking data
                flash("Дата поездки не может быть в прошлом. Пожалуйста, выберите будущую дату.", "error")
                return redirect(url_for("public.home"))
                
            # Check if date is too far in the future
            max_future_date = today.replace(year=today.year + 1)
            if travel_date_obj > max_future_date:
                session.pop("booking_data", None)
                flash("Дата поездки не может быть более чем на год в будущем", "error")
                return redirect(url_for("public.home"))
                
        except (ValueError, KeyError):
            session.pop("booking_data", None)
            flash("Неверные данные бронирования", "error")
            return redirect(url_for("public.home"))
        # Auto-login the user
        session["user_id"] = user.id
        session["email"] = user.email
        session["role"] = user.role
        
        # Create booking
        from ..repository.booking_repo import booking_repository
        from ..repository.tours_repo import tours_repository
        from ..models import Booking
        
        tour = tours_repository.get_by_id(booking_data["tour_id"])
        if tour:
            booking_id = booking_repository.get_next_id()
            total_price = tour.price * booking_data["passengers"]
            
            booking = Booking(
                id=booking_id,
                tour_id=booking_data["tour_id"],
                user_id=user.id,
                booking_date=datetime.now().strftime("%Y-%m-%d"),
                travel_date=booking_data["travel_date"],
                passengers=booking_data["passengers"],
                total_price=total_price,
                status="confirmed"
            )
            
            booking_repository.add_booking(booking)
            
            # Clear booking data from session
            session.pop("booking_data", None)
            
            flash("Регистрация и бронирование прошли успешно!", "success")
            return redirect(url_for("public.booking_confirmation", booking_id=booking_id))
    
    flash("Регистрация прошла успешно! Теперь вы можете войти в систему.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.get("/logout")
def logout():
    session.clear()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("public.home"))
