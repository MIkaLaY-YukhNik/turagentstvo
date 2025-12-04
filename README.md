MikolaTravelHub Платформа поиска и бронирования комфортных туров для пожилых путешественников и их семей

Общее описание

• Умный поиск туров по городу, типу (включая специальные программы для пожилых в горах), длительности и цене • Детальная страница тура с актуальной погодой (OpenWeatherMap) и встроенной интерактивной картой (Google Maps) • Уникальный поток «гость → бронирование → регистрация → автоматическое создание брони» • Полная мультиязычность: русский / английский / испанский с сохранением выбора в сессии • Система обратной связи с приоритетами и возможностью ответа администратора • Мощная административная панель для самостоятельного управления контентом и заказами • Специальная фильтрация elderly_mountain — безопасные горные туры для пожилых

🧰 Технологический стек
Проект построен на технологиях Backend и Frontend с использованием Python 3.11, Flask и Jinja2. В качестве шаблонизатора применяется Jinja2. Для хранения данных используются in-memory репозитории, при этом система готова к переходу на SQLAlchemy и PostgreSQL.

Интеграция осуществляется с внешними API, такими как OpenWeatherMap и Google Maps Embed API. Поддерживается мультиязычность благодаря кастомной системе переводов и Flask-Session.

Аутентификация реализована через сессии Flask и библиотеку werkzeug.security с использованием алгоритма pbkdf2:sha256. Для тестирования применяется pytest вместе с Flask test client — все тесты проходят успешно.

Конфигурация проекта управляется через библиотеку python-dotenv и файл .env.

📁 Структура проекта
mikola_travel_hub/
├── app/
│   ├── __init__.py              # create_app(), регистрация blueprint’ов
│   ├── config.py                # загрузка .env
│   ├── translations.py          # словарь переводов ru/en/es + get_translation()
│   ├── models.py                # dataclass Tour, User, Booking, Feedback
│   ├── repositories/            # in-memory репозитории
│   │   ├── tours_repo.py
│   │   ├── user_repo.py
│   │   ├── booking_repo.py
│   │   └── feedback_repo.py
│   ├── services/
│   │   ├── weather_service.py   # OpenWeatherMap + логика «подходит ли пожилым»
│   │   └── maps_service.py      # генерация embed-карты
│   ├── templates/               # все Jinja2-шаблоны
│   ├── static/
│   │   ├── css/
│   │   ├── img/
│   │   │   └── tours/           # фото туров
│   │   └── favicon.ico
│   └── blueprints/
│       ├── public_bp.py         # главная, поиск, tour/id, book/id, set_language
│       ├── auth_bp.py           # login, register, logout
│       └── admin_bp.py          # дашборд, CRUD туров, брони, пользователи, фидбек
├── tests/
│   └── test_app.py              # 13 интеграционных тестов
├── docs/
│   ├── images/                  # диаграммы, скриншоты
│   └── README.md
├── .env                         # SECRET_KEY, OPENWEATHER_API_KEY, GOOGLE_MAPS_KEY
├── requirements.txt
└── run.py                       # точка входа

📦 Как запустить проект

1. Клонировать
git clone https://github.com/MIkaLaY-YukhNik/mikola-travel-hub.git cd mikola-travel-hub

2. Создать виртуальное окружение
python -m venv venv source venv/bin/activate # Windows: venv\Scripts\activate

3. Установить зависимости
pip install -r requirements.txt

4. Создать .env
cp .env.example .env

Отредактируйте .env — вставьте свои ключи
5. Запустить
python run.py### 3. Настройка фронтенда Перейдите в папку с приложением

cd frontend
Основные функциональные модули • Public — главная, поиск, детальная страница тура, начало бронирования, смена языка • Auth — регистрация, вход, выход + автобронирование после регистрации • Admin — полный CRUD туров, просмотр всех бронирований и пользователей, работа с обратной связью • Weather & Maps — погода с рекомендациями для пожилых + интерактивная карта • Feedback System — обратная связь с приоритетами и ответами администратора • Multilanguage — переключение ru / en / es с сохранением в сессии

Ключевая особенность: Автобронирование после регистрации

Гость выбирает тур → вводит дату и количество человек
Данные сохраняются в session['pending_booking']
Редирект на регистрацию
После успешного создания аккаунта → бронирование автоматически создаётся
Пользователь сразу попадает на страницу подтверждения Это избавляет пожилых пользователей от необходимости повторно искать тур после регистрации.
Особенности архитектуры • Чёткое разделение на Blueprints • In-memory репозитории с единым интерфейсом → переход на SQLAlchemy за несколько часов • Dataclasses + строгая типизация • Сервисный слой для работы с внешними API • 100 % покрытие критических сценариев автоматизированными тестами • Готовность к масштабированию (Redis, Celery, Docker, продакшн-сервер)

Полезные ссылки • Flask Documentation – https://flask.palletsprojects.com • OpenWeatherMap API – https://openweathermap.org/api • Google Maps Embed API – https://developers.google.com/maps/documentation/embed • Jinja2 Documentation – https://jinja.palletsprojects.com

User Registration and Authentication
User Registration: Users can now register with passport details including:
Email and password
First name and last name
Phone number
Passport number, issuing authority, and issue date
User Login/Logout: Secure authentication system with session management
User Repository: Separate file (mikola/repository/user_repo.py) stores user data during registration
Enhanced Booking System
Passport Details: When booking a tour, clients must enter their passport details
Multiple Passengers: Users can book for multiple passengers with automatic price calculation
Booking Repository: Separate file (mikola/repository/booking_repo.py) manages all bookings
Booking Status: Track booking status (pending, confirmed, cancelled)
User Experience Improvements
Seamless Registration: If a user tries to book without being logged in, they're redirected to registration with pre-filled passport data
My Bookings: Logged-in users can view all their bookings
Dynamic Pricing: Real-time price calculation based on number of passengers
Flash Messages: User-friendly notifications for all actions
File Structure
New Files Created
mikola/blueprints/auth.py - Authentication blueprint with login/register/logout
mikola/repository/user_repo.py - User data storage and management
mikola/repository/booking_repo.py - Booking data storage and management
mikola/templates/auth/register.html - User registration form
mikola/templates/my_bookings.html - User's booking history
Modified Files
mikola/models.py - Updated User and Booking models with new fields
mikola/blueprints/public.py - Enhanced booking functionality
mikola/templates/auth/login.html - Improved login form
mikola/templates/tour_detail.html - Enhanced booking form with passport fields
mikola/templates/booking.html - Improved booking confirmation
mikola/templates/base.html - Added user navigation and flash messages
mikola/static/styles.css - Added styles for new components
How It Works
Registration Flow
User visits tour detail page and clicks "Book Tour"
If not logged in, they're redirected to registration
Registration form pre-fills passport data from booking attempt
After successful registration, user is automatically logged in and booking is created
User sees booking confirmation page
Booking Flow for Logged-in Users
User selects tour and fills booking form
System calculates total price based on passengers
Booking is immediately created and confirmed
User sees detailed booking confirmation
Data Storage
User Data: Stored in user_repo.py with passport details
Booking Data: Stored in booking_repo.py with tour, user, and passenger information
Session Management: Flask sessions handle user authentication state
Demo Access
Admin Account: admin@mikola.com / admin123
Regular Users: Can register with any email and passport details
Security Features
Password hashing using Werkzeug
Session-based authentication
Input validation and sanitization
CSRF protection through Flask forms
