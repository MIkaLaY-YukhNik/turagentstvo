from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from ..repository.tours_repo import tours_repository
from ..repository.feedback_repo import feedback_repository
from ..repository.user_repo import user_repository
from ..repository.booking_repo import booking_repository
from ..models import Feedback


admin_bp = Blueprint("admin", __name__)


def _is_admin() -> bool:
    return session.get("role") == "admin"


@admin_bp.get("/")
def dashboard():
    if not _is_admin():
        return redirect(url_for("auth.login", admin=1))
    tours = tours_repository.search()
    # Provide small counters for quick overview
    bookings_count = len(booking_repository.get_all())
    users_count = len(user_repository.get_all())
    feedback_count = len(feedback_repository.get_all())
    return render_template(
        "admin/dashboard.html",
        tours=tours,
        bookings_count=bookings_count,
        users_count=users_count,
        feedback_count=feedback_count,
    )


@admin_bp.get("/add")
def add_form():
    if not _is_admin():
        return redirect(url_for("auth.login", admin=1))
    return render_template("admin/add_tour.html")


@admin_bp.post("/add")
def add_tour():
    if not _is_admin():
        return redirect(url_for("auth.login", admin=1))
    form = request.form
    new_id = max((t.id for t in tours_repository.search()), default=0) + 1
    from ..models import Tour

    tour = Tour(
        id=new_id,
        title=form.get("title", "New Tour"),
        description=form.get("description", ""),
        price=float(form.get("price", 0) or 0),
        city=form.get("city", ""),
        country=form.get("country", ""),
        type=form.get("type", "city"),
        duration_days=int(form.get("duration_days", 1) or 1),
        photo_url=form.get("photo_url", ""),
    )
    tours_repository._tours.append(tour)
    return redirect(url_for("admin.dashboard"))


@admin_bp.get("/feedback")
def feedback_management():
    """Admin feedback management page"""
    if not _is_admin():
        return redirect(url_for("auth.login", admin=1))
    
    # Get feedback statistics
    stats = feedback_repository.get_feedback_stats()
    
    # Get all feedback sorted by priority and date
    all_feedback = feedback_repository.get_all()
    all_feedback.sort(key=lambda x: (
        {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}[x.priority],
        x.created_at
    ), reverse=True)
    
    return render_template("admin/feedback.html", feedback_list=all_feedback, stats=stats)


@admin_bp.get("/feedback/<int:feedback_id>")
def view_feedback(feedback_id: int):
    """View specific feedback"""
    if not _is_admin():
        return redirect(url_for("auth.login", admin=1))
    
    feedback = feedback_repository.get_by_id(feedback_id)
    if not feedback:
        flash("Сообщение не найдено", "error")
        return redirect(url_for("admin.feedback_management"))
    
    # Get user info
    user = user_repository.get_by_id(feedback.user_id)
    
    return render_template("admin/view_feedback.html", feedback=feedback, user=user)


@admin_bp.post("/feedback/<int:feedback_id>/respond")
def respond_to_feedback(feedback_id: int):
    """Respond to feedback"""
    if not _is_admin():
        return redirect(url_for("auth.login", admin=1))
    
    feedback = feedback_repository.get_by_id(feedback_id)
    if not feedback:
        flash("Сообщение не найдено", "error")
        return redirect(url_for("admin.feedback_management"))
    
    admin_response = request.form.get("admin_response", "").strip()
    if not admin_response:
        flash("Пожалуйста, напишите ответ", "error")
        return redirect(url_for("admin.view_feedback", feedback_id=feedback_id))
    
    if len(admin_response) > 2000:
        flash("Ответ слишком длинный (максимум 2000 символов)", "error")
        return redirect(url_for("admin.view_feedback", feedback_id=feedback_id))
    
    admin_id = session["user_id"]
    if feedback_repository.respond_to_feedback(feedback_id, admin_response, admin_id):
        flash("Ответ отправлен пользователю", "success")
    else:
        flash("Ошибка при отправке ответа", "error")
    
    return redirect(url_for("admin.view_feedback", feedback_id=feedback_id))


@admin_bp.post("/feedback/<int:feedback_id>/status")
def change_feedback_status(feedback_id: int):
    """Change feedback status"""
    if not _is_admin():
        return redirect(url_for("auth.login", admin=1))
    
    new_status = request.form.get("status")
    if new_status in ['new', 'in_progress', 'resolved', 'closed']:
        if feedback_repository.change_status(feedback_id, new_status):
            flash("Статус обновлен", "success")
        else:
            flash("Ошибка при обновлении статуса", "error")
    else:
        flash("Неверный статус", "error")
    
    return redirect(url_for("admin.view_feedback", feedback_id=feedback_id))


@admin_bp.post("/feedback/<int:feedback_id>/priority")
def change_feedback_priority(feedback_id: int):
    """Change feedback priority"""
    if not _is_admin():
        return redirect(url_for("auth.login", admin=1))
    
    new_priority = request.form.get("priority")
    if new_priority in ['low', 'normal', 'high', 'urgent']:
        if feedback_repository.change_priority(feedback_id, new_priority):
            flash("Приоритет обновлен", "success")
        else:
            flash("Ошибка при обновлении приоритета", "error")
    else:
        flash("Неверный приоритет", "error")
    
    return redirect(url_for("admin.view_feedback", feedback_id=feedback_id))


# --- Additional admin management routes ---

@admin_bp.get("/tours")
def manage_tours():
    if not _is_admin():
        return redirect(url_for("auth.login"))
    tours = tours_repository.search()
    return render_template("admin/manage_tours.html", tours=tours)


@admin_bp.get("/tours/<int:tour_id>/edit")
def edit_tour_form(tour_id: int):
    if not _is_admin():
        return redirect(url_for("auth.login"))
    tour = tours_repository.get_by_id(tour_id)
    if not tour:
        flash("Тур не найден", "error")
        return redirect(url_for("admin.manage_tours"))
    return render_template("admin/edit_tour.html", tour=tour)


@admin_bp.post("/tours/<int:tour_id>/edit")
def edit_tour(tour_id: int):
    if not _is_admin():
        return redirect(url_for("auth.login"))
    tour = tours_repository.get_by_id(tour_id)
    if not tour:
        flash("Тур не найден", "error")
        return redirect(url_for("admin.manage_tours"))

    form = request.form
    tour.title = form.get("title", tour.title)
    tour.description = form.get("description", tour.description)
    try:
        tour.price = float(form.get("price", tour.price) or tour.price)
    except ValueError:
        flash("Неверная цена", "error")
        return redirect(url_for("admin.edit_tour_form", tour_id=tour_id))
    tour.city = form.get("city", tour.city)
    tour.country = form.get("country", tour.country)
    tour.type = form.get("type", tour.type)
    try:
        tour.duration_days = int(form.get("duration_days", tour.duration_days) or tour.duration_days)
    except ValueError:
        flash("Неверная длительность", "error")
        return redirect(url_for("admin.edit_tour_form", tour_id=tour_id))
    tour.photo_url = form.get("photo_url", tour.photo_url)

    flash("Тур обновлён", "success")
    return redirect(url_for("admin.manage_tours"))


@admin_bp.get("/bookings")
def all_bookings():
    if not _is_admin():
        return redirect(url_for("auth.login"))
    bookings = booking_repository.get_all()
    # Enrich bookings with tour and user
    enriched = []
    for b in bookings:
        enriched.append({
            "booking": b,
            "tour": tours_repository.get_by_id(b.tour_id),
            "user": user_repository.get_by_id(b.user_id),
        })
    return render_template("admin/bookings.html", bookings=enriched)


@admin_bp.get("/users")
def users_list():
    if not _is_admin():
        return redirect(url_for("auth.login"))
    users = user_repository.get_all()
    return render_template("admin/users.html", users=users)


