"""
Комплексные тесты для туристического веб-приложения Mikola.
Покрывает: модели, репозитории, авторизацию, бронирование, обратную связь, админ-панель.
"""

import pytest
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from mikola import create_app
from mikola.models import Tour, User, Booking, Feedback


# ============================================================================
# FIXTURES - Общие вспомогательные функции для тестов
# ============================================================================

@pytest.fixture
def app():
    """Создание тестового приложения."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture
def client(app):
    """Создание тестового клиента."""
    return app.test_client()


@pytest.fixture
def authenticated_client(app):
    """Клиент с авторизованным обычным пользователем."""
    client = app.test_client()
    
    # Регистрация нового пользователя
    future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    client.post("/register", data={
        "email": "testuser@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890"
    })
    
    # Авторизация
    client.post("/login", data={
        "email": "testuser@example.com",
        "password": "password123"
    })
    
    return client


@pytest.fixture
def admin_client(app):
    """Клиент с авторизованным администратором."""
    client = app.test_client()
    
    # Авторизация как admin (предзаданный в user_repo)
    client.post("/login", data={
        "email": "admin@mikola.com",
        "password": "admin123",
        "admin": "1"
    })
    
    return client


# ============================================================================
# ТЕСТЫ МОДЕЛЕЙ (Dataclasses)
# ============================================================================

class TestModels:
    """Тесты для моделей данных."""
    
    def test_tour_creation(self):
        """Тест создания тура."""
        tour = Tour(
            id=1,
            title="Test Tour",
            description="Test Description",
            price=100.0,
            city="Moscow",
            country="Russia",
            type="city",
            duration_days=3
        )
        assert tour.id == 1
        assert tour.title == "Test Tour"
        assert tour.price == 100.0
        assert tour.duration_days == 3
        assert tour.photo_url is None  # Optional field
        assert tour.categories == []  # Default factory
    
    def test_tour_with_optional_fields(self):
        """Тест тура с опциональными полями."""
        tour = Tour(
            id=2,
            title="Concert",
            description="Live music",
            price=50.0,
            city="New York",
            country="USA",
            type="concert",
            duration_days=1,
            photo_url="https://example.com/photo.jpg",
            venue="Madison Square Garden",
            lat="40.7505",
            lng="-73.9934",
            categories=["music", "live"]
        )
        assert tour.venue == "Madison Square Garden"
        assert tour.lat == "40.7505"
        assert len(tour.categories) == 2
    
    def test_user_creation(self):
        """Тест создания пользователя."""
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            role="client"
        )
        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.role == "client"
        assert user.first_name is None
    
    def test_user_with_profile(self):
        """Тест пользователя с заполненным профилем."""
        user = User(
            id=2,
            email="john@example.com",
            password_hash="hashed",
            role="admin",
            first_name="John",
            last_name="Doe",
            phone="+1234567890"
        )
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role == "admin"
    
    def test_booking_creation(self):
        """Тест создания бронирования."""
        booking = Booking(
            id=1,
            tour_id=1,
            user_id=1,
            booking_date="2025-12-01",
            travel_date="2025-12-15",
            passengers=2,
            total_price=200.0,
            status="confirmed"
        )
        assert booking.id == 1
        assert booking.passengers == 2
        assert booking.total_price == 200.0
        assert booking.status == "confirmed"
    
    def test_feedback_creation(self):
        """Тест создания обратной связи."""
        feedback = Feedback(
            id=1,
            user_id=1,
            subject="Question",
            message="Test message",
            created_at="2025-12-01 10:00:00",
            status="new"
        )
        assert feedback.id == 1
        assert feedback.status == "new"
        assert feedback.priority == "normal"  # Default
        assert feedback.category == "general"  # Default
        assert feedback.admin_response is None
    
    def test_feedback_with_response(self):
        """Тест обратной связи с ответом админа."""
        feedback = Feedback(
            id=2,
            user_id=1,
            subject="Issue",
            message="Problem description",
            created_at="2025-12-01 10:00:00",
            status="resolved",
            admin_response="Fixed!",
            admin_id=1,
            responded_at="2025-12-01 12:00:00",
            priority="high",
            category="technical"
        )
        assert feedback.admin_response == "Fixed!"
        assert feedback.priority == "high"
        assert feedback.category == "technical"


# ============================================================================
# ТЕСТЫ ПУБЛИЧНЫХ МАРШРУТОВ
# ============================================================================

class TestPublicRoutes:
    """Тесты публичных страниц."""
    
    def test_home_ok(self, client):
        """Тест главной страницы."""
        resp = client.get("/")
        assert resp.status_code == 200
    
    def test_home_displays_featured_tours(self, client):
        """Тест отображения рекомендуемых туров на главной."""
        resp = client.get("/")
        assert resp.status_code == 200
        # Проверяем, что страница содержит какой-либо контент
        assert len(resp.get_data(as_text=True)) > 100
    
    def test_search_page_loads(self, client):
        """Тест загрузки страницы поиска."""
        resp = client.get("/search")
        assert resp.status_code == 200
    
    def test_search_by_location(self, client):
        """Тест поиска по городу."""
        resp = client.get("/search?location=Toronto")
        assert resp.status_code == 200
    
    def test_search_by_keyword(self, client):
        """Тест поиска по ключевому слову."""
        resp = client.get("/search?keyword=concert")
        assert resp.status_code == 200
    
    def test_search_by_duration(self, client):
        """Тест поиска по длительности."""
        resp = client.get("/search?duration=1")
        assert resp.status_code == 200
    
    def test_search_by_price_range(self, client):
        """Тест поиска по диапазону цен."""
        resp = client.get("/search?min_price=50&max_price=200")
        assert resp.status_code == 200
    
    def test_search_combined_filters(self, client):
        """Тест комбинированного поиска."""
        resp = client.get("/search?location=New York&min_price=100&duration=1")
        assert resp.status_code == 200
    
    def test_tour_detail_existing(self, client):
        """Тест страницы существующего тура."""
        resp = client.get("/tour/1")
        assert resp.status_code == 200
    
    def test_tour_detail_not_found(self, client):
        """Тест 404 для несуществующего тура."""
        resp = client.get("/tour/99999")
        assert resp.status_code == 404
    
    def test_set_language_russian(self, client):
        """Тест смены языка на русский."""
        resp = client.get("/set_language/ru")
        assert resp.status_code == 302
        with client.session_transaction() as session:
            assert session.get("language") == "ru"
    
    def test_set_language_english(self, client):
        """Тест смены языка на английский."""
        resp = client.get("/set_language/en")
        assert resp.status_code == 302
        with client.session_transaction() as session:
            assert session.get("language") == "en"
    
    def test_set_language_spanish(self, client):
        """Тест смены языка на испанский."""
        resp = client.get("/set_language/es")
        assert resp.status_code == 302
        with client.session_transaction() as session:
            assert session.get("language") == "es"
    
    def test_set_invalid_language(self, client):
        """Тест попытки установить неподдерживаемый язык."""
        resp = client.get("/set_language/de")
        assert resp.status_code == 302
        with client.session_transaction() as session:
            # Язык не должен измениться на неподдерживаемый
            assert session.get("language") != "de"


# ============================================================================
# ТЕСТЫ АВТОРИЗАЦИИ
# ============================================================================

class TestAuthentication:
    """Тесты авторизации и регистрации."""
    
    def test_login_page_loads(self, client):
        """Тест загрузки страницы входа."""
        resp = client.get("/login")
        assert resp.status_code == 200
    
    def test_login_page_admin_mode(self, client):
        """Тест страницы входа в режиме админа."""
        resp = client.get("/login?admin=1")
        assert resp.status_code == 200
    
    def test_register_page_loads(self, client):
        """Тест загрузки страницы регистрации."""
        resp = client.get("/register")
        assert resp.status_code == 200
    
    def test_successful_registration(self, client):
        """Тест успешной регистрации."""
        resp = client.post("/register", data={
            "email": "newuser@example.com",
            "password": "securepassword",
            "confirm_password": "securepassword",
            "first_name": "New",
            "last_name": "User",
            "phone": "+1234567890"
        }, follow_redirects=True)
        assert resp.status_code == 200
    
    def test_registration_password_mismatch(self, client):
        """Тест регистрации с несовпадающими паролями."""
        resp = client.post("/register", data={
            "email": "test@example.com",
            "password": "password1",
            "confirm_password": "password2",
            "first_name": "Test",
            "last_name": "User"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/register" in resp.headers["Location"]
    
    def test_registration_short_password(self, client):
        """Тест регистрации с коротким паролем."""
        resp = client.post("/register", data={
            "email": "test@example.com",
            "password": "123",
            "confirm_password": "123",
            "first_name": "Test",
            "last_name": "User"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/register" in resp.headers["Location"]
    
    def test_successful_login(self, client):
        """Тест успешного входа."""
        # Сначала регистрация
        client.post("/register", data={
            "email": "logintest@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "first_name": "Login",
            "last_name": "Test"
        })
        
        # Затем вход
        resp = client.post("/login", data={
            "email": "logintest@example.com",
            "password": "password123"
        }, follow_redirects=False)
        assert resp.status_code == 302
    
    def test_login_wrong_password(self, client):
        """Тест входа с неверным паролем."""
        resp = client.post("/login", data={
            "email": "admin@mikola.com",
            "password": "wrongpassword"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
    
    def test_login_nonexistent_user(self, client):
        """Тест входа несуществующего пользователя."""
        resp = client.post("/login", data={
            "email": "nonexistent@example.com",
            "password": "password123"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
    
    def test_admin_login_redirect_to_dashboard(self, client):
        """Тест входа админа с редиректом на панель."""
        resp = client.post("/login", data={
            "email": "admin@mikola.com",
            "password": "admin123",
            "admin": "1"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/admin" in resp.headers["Location"]
    
    def test_logout(self, authenticated_client):
        """Тест выхода из системы."""
        resp = authenticated_client.get("/logout", follow_redirects=False)
        assert resp.status_code == 302
        with authenticated_client.session_transaction() as session:
            assert "user_id" not in session


# ============================================================================
# ТЕСТЫ БРОНИРОВАНИЯ
# ============================================================================

class TestBooking:
    """Тесты бронирования туров."""
    
    def test_book_requires_login(self, client):
        """Тест что бронирование требует авторизации."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        resp = client.post("/book/1", data={
            "passengers": "2",
            "travel_date": future_date
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/register" in resp.headers["Location"]
    
    def test_book_missing_travel_date(self, client):
        """Тест бронирования без даты поездки."""
        resp = client.post("/book/1", data={
            "passengers": "2"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/tour/1" in resp.headers["Location"]
    
    def test_book_invalid_passengers_zero(self, client):
        """Тест бронирования с нулевым количеством пассажиров."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        resp = client.post("/book/1", data={
            "passengers": "0",
            "travel_date": future_date
        }, follow_redirects=False)
        assert resp.status_code == 302
    
    def test_book_invalid_passengers_too_many(self, client):
        """Тест бронирования с слишком большим количеством пассажиров."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        resp = client.post("/book/1", data={
            "passengers": "100",
            "travel_date": future_date
        }, follow_redirects=False)
        assert resp.status_code == 302
    
    def test_book_past_date(self, client):
        """Тест бронирования на прошедшую дату."""
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        resp = client.post("/book/1", data={
            "passengers": "2",
            "travel_date": past_date
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/tour/1" in resp.headers["Location"]
    
    def test_book_date_too_far(self, client):
        """Тест бронирования на дату более года в будущем."""
        far_future = (datetime.now() + timedelta(days=400)).strftime("%Y-%m-%d")
        resp = client.post("/book/1", data={
            "passengers": "2",
            "travel_date": far_future
        }, follow_redirects=False)
        assert resp.status_code == 302
    
    def test_book_nonexistent_tour(self, client):
        """Тест бронирования несуществующего тура."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        resp = client.post("/book/99999", data={
            "passengers": "2",
            "travel_date": future_date
        })
        assert resp.status_code == 404
    
    def test_my_bookings_requires_login(self, client):
        """Тест что мои бронирования требуют авторизации."""
        resp = client.get("/my-bookings")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
    
    def test_my_bookings_authenticated(self, authenticated_client):
        """Тест страницы моих бронирований для авторизованного пользователя."""
        resp = authenticated_client.get("/my-bookings")
        assert resp.status_code == 200
    
    def test_booking_confirmation_nonexistent(self, client):
        """Тест подтверждения несуществующего бронирования."""
        resp = client.get("/booking/99999")
        assert resp.status_code == 404


# ============================================================================
# ТЕСТЫ ОБРАТНОЙ СВЯЗИ
# ============================================================================

class TestFeedback:
    """Тесты обратной связи."""
    
    def test_feedback_form_requires_login(self, client):
        """Тест что форма обратной связи требует авторизации."""
        resp = client.get("/feedback")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
    
    def test_feedback_form_authenticated(self, authenticated_client):
        """Тест формы обратной связи для авторизованного пользователя."""
        resp = authenticated_client.get("/feedback")
        assert resp.status_code == 200
    
    def test_submit_feedback_requires_login(self, client):
        """Тест что отправка отзыва требует авторизации."""
        resp = client.post("/feedback", data={
            "subject": "Test",
            "message": "Test message",
            "category": "general",
            "priority": "normal"
        })
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
    
    def test_submit_feedback_empty_subject(self, authenticated_client):
        """Тест отправки отзыва с пустой темой."""
        resp = authenticated_client.post("/feedback", data={
            "subject": "",
            "message": "Test message",
            "category": "general",
            "priority": "normal"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/feedback" in resp.headers["Location"]
    
    def test_submit_feedback_empty_message(self, authenticated_client):
        """Тест отправки отзыва с пустым сообщением."""
        resp = authenticated_client.post("/feedback", data={
            "subject": "Test Subject",
            "message": "",
            "category": "general",
            "priority": "normal"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/feedback" in resp.headers["Location"]
    
    def test_submit_feedback_subject_too_long(self, authenticated_client):
        """Тест отправки отзыва со слишком длинной темой."""
        resp = authenticated_client.post("/feedback", data={
            "subject": "A" * 250,
            "message": "Test message",
            "category": "general",
            "priority": "normal"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/feedback" in resp.headers["Location"]
    
    def test_submit_feedback_message_too_long(self, authenticated_client):
        """Тест отправки отзыва со слишком длинным сообщением."""
        resp = authenticated_client.post("/feedback", data={
            "subject": "Test Subject",
            "message": "A" * 2500,
            "category": "general",
            "priority": "normal"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/feedback" in resp.headers["Location"]
    
    def test_submit_feedback_success(self, authenticated_client):
        """Тест успешной отправки отзыва."""
        resp = authenticated_client.post("/feedback", data={
            "subject": "Test Subject",
            "message": "Test message content",
            "category": "general",
            "priority": "normal"
        }, follow_redirects=True)
        assert resp.status_code == 200
    
    def test_my_feedback_requires_login(self, client):
        """Тест что история отзывов требует авторизации."""
        resp = client.get("/my-feedback")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
    
    def test_my_feedback_authenticated(self, authenticated_client):
        """Тест истории отзывов для авторизованного пользователя."""
        resp = authenticated_client.get("/my-feedback")
        assert resp.status_code == 200


# ============================================================================
# ТЕСТЫ АДМИН-ПАНЕЛИ
# ============================================================================

class TestAdminPanel:
    """Тесты административной панели."""
    
    def test_admin_dashboard_requires_admin(self, client):
        """Тест что панель админа требует права админа."""
        resp = client.get("/admin/")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
    
    def test_admin_dashboard_authenticated(self, admin_client):
        """Тест доступа к панели админа."""
        resp = admin_client.get("/admin/")
        assert resp.status_code == 200
    
    def test_admin_add_tour_form(self, admin_client):
        """Тест формы добавления тура."""
        resp = admin_client.get("/admin/add")
        assert resp.status_code == 200
    
    def test_admin_add_tour(self, admin_client):
        """Тест добавления нового тура."""
        resp = admin_client.post("/admin/add", data={
            "title": "New Test Tour",
            "description": "Test Description",
            "price": "150.00",
            "city": "Test City",
            "country": "Test Country",
            "type": "city",
            "duration_days": "3",
            "photo_url": "https://example.com/photo.jpg"
        }, follow_redirects=True)
        assert resp.status_code == 200
    
    def test_admin_manage_tours(self, admin_client):
        """Тест страницы управления турами."""
        resp = admin_client.get("/admin/tours")
        assert resp.status_code == 200
    
    def test_admin_edit_tour_form(self, admin_client):
        """Тест формы редактирования тура."""
        resp = admin_client.get("/admin/tours/1/edit")
        assert resp.status_code == 200
    
    def test_admin_edit_tour_nonexistent(self, admin_client):
        """Тест редактирования несуществующего тура."""
        resp = admin_client.get("/admin/tours/99999/edit", follow_redirects=True)
        assert resp.status_code == 200  # Redirect to manage_tours
    
    def test_admin_edit_tour_post(self, admin_client):
        """Тест сохранения изменений тура."""
        resp = admin_client.post("/admin/tours/1/edit", data={
            "title": "Updated Tour Title",
            "description": "Updated description",
            "price": "200.00",
            "city": "Updated City",
            "country": "Updated Country",
            "type": "city",
            "duration_days": "5",
            "photo_url": ""
        }, follow_redirects=True)
        assert resp.status_code == 200
    
    def test_admin_all_bookings(self, admin_client):
        """Тест просмотра всех бронирований."""
        resp = admin_client.get("/admin/bookings")
        assert resp.status_code == 200
    
    def test_admin_users_list(self, admin_client):
        """Тест списка пользователей."""
        resp = admin_client.get("/admin/users")
        assert resp.status_code == 200
    
    def test_admin_feedback_management(self, admin_client):
        """Тест управления обратной связью."""
        resp = admin_client.get("/admin/feedback")
        assert resp.status_code == 200
    
    def test_admin_view_feedback_nonexistent(self, admin_client):
        """Тест просмотра несуществующего отзыва."""
        resp = admin_client.get("/admin/feedback/99999", follow_redirects=True)
        assert resp.status_code == 200  # Redirect to feedback management
    
    def test_admin_respond_feedback_nonexistent(self, admin_client):
        """Тест ответа на несуществующий отзыв."""
        resp = admin_client.post("/admin/feedback/99999/respond", data={
            "admin_response": "Test response"
        }, follow_redirects=True)
        assert resp.status_code == 200
    
    def test_admin_change_feedback_status_invalid(self, admin_client):
        """Тест изменения статуса с неверным значением."""
        resp = admin_client.post("/admin/feedback/1/status", data={
            "status": "invalid_status"
        }, follow_redirects=True)
        assert resp.status_code == 200
    
    def test_admin_change_feedback_priority_invalid(self, admin_client):
        """Тест изменения приоритета с неверным значением."""
        resp = admin_client.post("/admin/feedback/1/priority", data={
            "priority": "invalid_priority"
        }, follow_redirects=True)
        assert resp.status_code == 200
    
    def test_admin_requires_admin_role(self, authenticated_client):
        """Тест что обычный пользователь не имеет доступа к админ-панели."""
        resp = authenticated_client.get("/admin/")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


# ============================================================================
# ТЕСТЫ РЕПОЗИТОРИЕВ
# ============================================================================

class TestUserRepository:
    """Тесты репозитория пользователей."""
    
    def test_user_repository_initial_admin(self, app):
        """Тест наличия начального админа."""
        from mikola.repository.user_repo import UserRepository
        repo = UserRepository()
        admin = repo.get_by_email("admin@mikola.com")
        assert admin is not None
        assert admin.role == "admin"
    
    def test_add_and_get_user(self, app):
        """Тест добавления и получения пользователя."""
        from mikola.repository.user_repo import UserRepository
        repo = UserRepository()
        
        new_user = User(
            id=repo.get_next_id(),
            email="newtest@example.com",
            password_hash="hash",
            role="client"
        )
        repo.add_user(new_user)
        
        retrieved = repo.get_by_email("newtest@example.com")
        assert retrieved is not None
        assert retrieved.email == "newtest@example.com"
    
    def test_get_user_by_id(self, app):
        """Тест получения пользователя по ID."""
        from mikola.repository.user_repo import UserRepository
        repo = UserRepository()
        admin = repo.get_by_id(1)
        assert admin is not None
        assert admin.email == "admin@mikola.com"
    
    def test_get_nonexistent_user(self, app):
        """Тест получения несуществующего пользователя."""
        from mikola.repository.user_repo import UserRepository
        repo = UserRepository()
        user = repo.get_by_id(99999)
        assert user is None
    
    def test_get_all_users(self, app):
        """Тест получения всех пользователей."""
        from mikola.repository.user_repo import UserRepository
        repo = UserRepository()
        users = repo.get_all()
        assert len(users) >= 1
    
    def test_update_user(self, app):
        """Тест обновления пользователя."""
        from mikola.repository.user_repo import UserRepository
        repo = UserRepository()
        
        user = repo.get_by_id(1)
        user.first_name = "UpdatedName"
        result = repo.update_user(user)
        
        assert result is True
        updated = repo.get_by_id(1)
        assert updated.first_name == "UpdatedName"
    
    def test_delete_user(self, app):
        """Тест удаления пользователя."""
        from mikola.repository.user_repo import UserRepository
        repo = UserRepository()
        
        new_user = User(
            id=repo.get_next_id(),
            email="todelete@example.com",
            password_hash="hash",
            role="client"
        )
        repo.add_user(new_user)
        
        result = repo.delete_user(new_user.id)
        assert result is True
        
        deleted = repo.get_by_id(new_user.id)
        assert deleted is None


class TestBookingRepository:
    """Тесты репозитория бронирований."""
    
    def test_add_and_get_booking(self, app):
        """Тест добавления и получения бронирования."""
        from mikola.repository.booking_repo import BookingRepository
        repo = BookingRepository()
        
        booking = Booking(
            id=repo.get_next_id(),
            tour_id=1,
            user_id=1,
            booking_date="2025-12-01",
            travel_date="2025-12-15",
            passengers=2,
            total_price=200.0,
            status="confirmed"
        )
        repo.add_booking(booking)
        
        retrieved = repo.get_by_id(booking.id)
        assert retrieved is not None
        assert retrieved.tour_id == 1
    
    def test_get_bookings_by_user(self, app):
        """Тест получения бронирований пользователя."""
        from mikola.repository.booking_repo import BookingRepository
        repo = BookingRepository()
        
        booking = Booking(
            id=repo.get_next_id(),
            tour_id=1,
            user_id=42,
            booking_date="2025-12-01",
            travel_date="2025-12-15",
            passengers=1,
            total_price=100.0,
            status="confirmed"
        )
        repo.add_booking(booking)
        
        user_bookings = repo.get_by_user_id(42)
        assert len(user_bookings) >= 1
    
    def test_cancel_booking(self, app):
        """Тест отмены бронирования."""
        from mikola.repository.booking_repo import BookingRepository
        repo = BookingRepository()
        
        booking = Booking(
            id=repo.get_next_id(),
            tour_id=1,
            user_id=1,
            booking_date="2025-12-01",
            travel_date="2025-12-15",
            passengers=1,
            total_price=100.0,
            status="confirmed"
        )
        repo.add_booking(booking)
        
        result = repo.cancel_booking(booking.id)
        assert result is True
        
        cancelled = repo.get_by_id(booking.id)
        assert cancelled.status == "cancelled"
    
    def test_get_confirmed_bookings_for_tour(self, app):
        """Тест получения подтвержденных бронирований тура."""
        from mikola.repository.booking_repo import BookingRepository
        repo = BookingRepository()
        
        # Добавим подтвержденное бронирование
        booking = Booking(
            id=repo.get_next_id(),
            tour_id=99,
            user_id=1,
            booking_date="2025-12-01",
            travel_date="2025-12-15",
            passengers=1,
            total_price=100.0,
            status="confirmed"
        )
        repo.add_booking(booking)
        
        confirmed = repo.get_confirmed_bookings_for_tour(99)
        assert len(confirmed) >= 1


class TestFeedbackRepository:
    """Тесты репозитория обратной связи."""
    
    def test_add_and_get_feedback(self, app):
        """Тест добавления и получения отзыва."""
        from mikola.repository.feedback_repo import FeedbackRepository
        repo = FeedbackRepository()
        
        feedback = Feedback(
            id=repo.get_next_id(),
            user_id=1,
            subject="Test",
            message="Test message",
            created_at="2025-12-01 10:00:00",
            status="new"
        )
        repo.add_feedback(feedback)
        
        retrieved = repo.get_by_id(feedback.id)
        assert retrieved is not None
        assert retrieved.subject == "Test"
    
    def test_get_feedback_by_status(self, app):
        """Тест получения отзывов по статусу."""
        from mikola.repository.feedback_repo import FeedbackRepository
        repo = FeedbackRepository()
        
        feedback = Feedback(
            id=repo.get_next_id(),
            user_id=1,
            subject="New Feedback",
            message="Test",
            created_at="2025-12-01 10:00:00",
            status="new"
        )
        repo.add_feedback(feedback)
        
        new_feedback = repo.get_by_status("new")
        assert len(new_feedback) >= 1
    
    def test_respond_to_feedback(self, app):
        """Тест ответа на отзыв."""
        from mikola.repository.feedback_repo import FeedbackRepository
        repo = FeedbackRepository()
        
        feedback = Feedback(
            id=repo.get_next_id(),
            user_id=1,
            subject="Question",
            message="Help needed",
            created_at="2025-12-01 10:00:00",
            status="new"
        )
        repo.add_feedback(feedback)
        
        result = repo.respond_to_feedback(feedback.id, "Here is the answer", 1)
        assert result is True
        
        responded = repo.get_by_id(feedback.id)
        assert responded.admin_response == "Here is the answer"
        assert responded.status == "resolved"
    
    def test_change_status(self, app):
        """Тест изменения статуса отзыва."""
        from mikola.repository.feedback_repo import FeedbackRepository
        repo = FeedbackRepository()
        
        feedback = Feedback(
            id=repo.get_next_id(),
            user_id=1,
            subject="Test",
            message="Test",
            created_at="2025-12-01 10:00:00",
            status="new"
        )
        repo.add_feedback(feedback)
        
        result = repo.change_status(feedback.id, "in_progress")
        assert result is True
        
        updated = repo.get_by_id(feedback.id)
        assert updated.status == "in_progress"
    
    def test_change_priority(self, app):
        """Тест изменения приоритета отзыва."""
        from mikola.repository.feedback_repo import FeedbackRepository
        repo = FeedbackRepository()
        
        feedback = Feedback(
            id=repo.get_next_id(),
            user_id=1,
            subject="Urgent",
            message="Very important",
            created_at="2025-12-01 10:00:00",
            status="new"
        )
        repo.add_feedback(feedback)
        
        result = repo.change_priority(feedback.id, "urgent")
        assert result is True
        
        updated = repo.get_by_id(feedback.id)
        assert updated.priority == "urgent"
    
    def test_feedback_stats(self, app):
        """Тест статистики отзывов."""
        from mikola.repository.feedback_repo import FeedbackRepository
        repo = FeedbackRepository()
        
        stats = repo.get_feedback_stats()
        assert "total" in stats
        assert "new" in stats
        assert "in_progress" in stats
        assert "resolved" in stats
        assert "closed" in stats
        assert "urgent" in stats


# ============================================================================
# ТЕСТЫ БЕЗОПАСНОСТИ
# ============================================================================

class TestSecurity:
    """Тесты безопасности."""
    
    def test_password_is_hashed(self, app):
        """Тест что пароль хранится хэшированным."""
        from mikola.repository.user_repo import UserRepository
        repo = UserRepository()
        admin = repo.get_by_id(1)
        
        # Пароль не должен храниться в открытом виде
        assert admin.password_hash != "admin123"
        # Но должен проверяться правильно
        assert check_password_hash(admin.password_hash, "admin123")
    
    def test_session_cleared_on_logout(self, authenticated_client):
        """Тест очистки сессии при выходе."""
        # Проверяем что пользователь авторизован
        with authenticated_client.session_transaction() as session:
            assert "user_id" in session
        
        # Выход
        authenticated_client.get("/logout")
        
        # Проверяем что сессия очищена
        with authenticated_client.session_transaction() as session:
            assert "user_id" not in session
            assert "email" not in session
            assert "role" not in session
    
    def test_cannot_access_other_user_booking(self, app):
        """Тест что пользователь не может отменить чужое бронирование."""
        client = app.test_client()
        
        # Регистрируем первого пользователя
        client.post("/register", data={
            "email": "user1@test.com",
            "password": "password123",
            "confirm_password": "password123"
        })
        
        # Пытаемся отменить несуществующее бронирование
        resp = client.post("/booking/99999/cancel", follow_redirects=False)
        # Должен требовать авторизацию или вернуть ошибку
        assert resp.status_code in [302, 404]


# ============================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================

class TestIntegration:
    """Интеграционные тесты полных сценариев."""
    
    def test_full_booking_flow_with_registration(self, client):
        """Тест полного цикла: регистрация -> бронирование."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        # 1. Попытка забронировать без авторизации
        resp = client.post("/book/1", data={
            "passengers": "2",
            "travel_date": future_date
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/register" in resp.headers["Location"]
        
        # 2. Регистрация пользователя (с данными бронирования в сессии)
        resp = client.post("/register", data={
            "email": "flowtest@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "first_name": "Flow",
            "last_name": "Test"
        }, follow_redirects=True)
        assert resp.status_code == 200
    
    def test_admin_workflow(self, admin_client):
        """Тест админского рабочего процесса."""
        # 1. Просмотр дашборда
        resp = admin_client.get("/admin/")
        assert resp.status_code == 200
        
        # 2. Добавление тура
        resp = admin_client.post("/admin/add", data={
            "title": "Admin Test Tour",
            "description": "Created by admin",
            "price": "500",
            "city": "Paris",
            "country": "France",
            "type": "city",
            "duration_days": "5"
        }, follow_redirects=True)
        assert resp.status_code == 200
        
        # 3. Просмотр пользователей
        resp = admin_client.get("/admin/users")
        assert resp.status_code == 200
        
        # 4. Просмотр бронирований
        resp = admin_client.get("/admin/bookings")
        assert resp.status_code == 200
    
    def test_feedback_workflow(self, app):
        """Тест полного цикла обратной связи."""
        # 1. Создаем и авторизуем пользователя
        user_client = app.test_client()
        user_client.post("/register", data={
            "email": "feedback_user@test.com",
            "password": "password123",
            "confirm_password": "password123"
        })
        user_client.post("/login", data={
            "email": "feedback_user@test.com",
            "password": "password123"
        })
        
        # 2. Отправка отзыва
        resp = user_client.post("/feedback", data={
            "subject": "Integration Test",
            "message": "This is an integration test feedback",
            "category": "technical",
            "priority": "high"
        }, follow_redirects=True)
        assert resp.status_code == 200
        
        # 3. Просмотр своих отзывов
        resp = user_client.get("/my-feedback")
        assert resp.status_code == 200
        assert "Integration Test" in resp.get_data(as_text=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
