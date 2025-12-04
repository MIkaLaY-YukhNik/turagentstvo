# Simple translation system for MikolaTravelHub
# This is a basic implementation without Flask-Babel for simplicity

TRANSLATIONS = {
    'ru': {
        # Navigation
        'search': 'Поиск',
        'my_bookings': 'Мои бронирования',
        'login': 'Войти',
        'register': 'Регистрация',
        'logout': 'Выйти',
        'admin': 'Админ',
        'home': 'На главную',
        
        # Common
        'price': 'Цена',
        'days': 'дн.',
        'passengers': 'пассажиров',
        'total_cost': 'Общая стоимость',
        'status': 'Статус',
        'confirmed': 'Подтверждено',
        'cancelled': 'Отменено',
        'pending': 'Ожидает подтверждения',
        
        # Booking
        'booking': 'Бронирование',
        'booking_confirmed': 'Бронирование подтверждено!',
        'booking_details': 'Детали бронирования',
        'booking_number': 'Номер бронирования',
        'tour': 'Тур',
        'place': 'Место',
        'travel_date': 'Дата поездки',
        'booking_date': 'Дата бронирования',
        'contact_info': 'Контактная информация',
        'name': 'Имя',
        'email': 'Email',
        'phone': 'Телефон',
        'cancel_booking': 'Отменить бронирование',
        'cancel': 'Отменить',
        
        # Auth
        'login_title': 'Вход в систему',
        'register_title': 'Регистрация',
        'password': 'Пароль',
        'confirm_password': 'Подтвердите пароль',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'passport_number': 'Номер паспорта',
        'passport_issued_by': 'Кем выдан паспорт',
        'passport_issued_date': 'Дата выдачи паспорта',
        'demo_admin': 'Демо-доступ администратора:',
        
        # Messages
        'booking_cancelled': 'Бронирование успешно отменено',
        'booking_error': 'Ошибка при отмене бронирования',
        'login_required': 'Необходимо войти в систему',
        'booking_not_found': 'Бронирование не найдено',
        'no_permission': 'У вас нет прав для удаления этого бронирования',
        'too_close_to_travel': 'Бронирование нельзя отменить менее чем за 3 дня до поездки',
        'date_error': 'Ошибка в дате поездки',
        'registration_success': 'Регистрация прошла успешно! Теперь вы можете войти в систему.',
        'login_success': 'Успешный вход в систему!',
        'logout_success': 'Вы вышли из системы',
        'invalid_credentials': 'Неверный email или пароль',
        'passwords_dont_match': 'Пароли не совпадают',
        'user_exists': 'Пользователь с таким email уже существует',
        
        # Forms
        'required': 'обязательно',
        'min_passengers': 'Количество пассажиров',
        'travel_date_label': 'Дата поездки',
        'passport_details': 'Паспортные данные',
        'booking_summary': 'Сводка бронирования',
        'price_per_person': 'Цена за человека',
        
        # Search
        'search_title': 'Поиск',
        'location': 'Локация',
        'type': 'Тип',
        'city': 'Городской',
        'mountain': 'Горный',
        'elderly_mountain': 'Горный 60+',
        'group': 'Групповой',
        'min_price': 'Мин. цена',
        'max_price': 'Макс. цена',
        'duration': 'Длительность (дни)',
        'search_button': 'Искать',
        'reset': 'Сбросить',
        'nothing_found': 'Ничего не найдено',
        
        # My Bookings
        'my_bookings_title': 'Мои бронирования',
        'no_bookings': 'У вас пока нет бронирований.',
        'view_tours': 'Посмотреть туры',
        'view_tour': 'Посмотреть тур',
        
        # Weather
        'weather': 'Погода',
        'suitable_for_elderly': 'Подходит для 60+ восхождений',
        'weather_warning': 'Предупреждение: неблагоприятно',
    },
    
    'en': {
        # Navigation
        'search': 'Search',
        'my_bookings': 'My Bookings',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'admin': 'Admin',
        'home': 'Home',
        
        # Common
        'price': 'Price',
        'days': 'days',
        'passengers': 'passengers',
        'total_cost': 'Total Cost',
        'status': 'Status',
        'confirmed': 'Confirmed',
        'cancelled': 'Cancelled',
        'pending': 'Pending',
        
        # Booking
        'booking': 'Booking',
        'booking_confirmed': 'Booking Confirmed!',
        'booking_details': 'Booking Details',
        'booking_number': 'Booking Number',
        'tour': 'Tour',
        'place': 'Place',
        'travel_date': 'Travel Date',
        'booking_date': 'Booking Date',
        'contact_info': 'Contact Information',
        'name': 'Name',
        'email': 'Email',
        'phone': 'Phone',
        'cancel_booking': 'Cancel Booking',
        'cancel': 'Cancel',
        
        # Auth
        'login_title': 'Login',
        'register_title': 'Registration',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'passport_number': 'Passport Number',
        'passport_issued_by': 'Issued By',
        'passport_issued_date': 'Issue Date',
        'demo_admin': 'Demo Admin Access:',
        
        # Messages
        'booking_cancelled': 'Booking successfully cancelled',
        'booking_error': 'Error cancelling booking',
        'login_required': 'Login required',
        'booking_not_found': 'Booking not found',
        'no_permission': 'You do not have permission to delete this booking',
        'too_close_to_travel': 'Booking cannot be cancelled less than 3 days before travel',
        'date_error': 'Error in travel date',
        'registration_success': 'Registration successful! You can now log in.',
        'login_success': 'Successfully logged in!',
        'logout_success': 'You have logged out',
        'invalid_credentials': 'Invalid email or password',
        'passwords_dont_match': 'Passwords do not match',
        'user_exists': 'User with this email already exists',
        
        # Forms
        'required': 'required',
        'min_passengers': 'Number of Passengers',
        'travel_date_label': 'Travel Date',
        'passport_details': 'Passport Details',
        'booking_summary': 'Booking Summary',
        'price_per_person': 'Price per Person',
        
        # Search
        'search_title': 'Search',
        'location': 'Location',
        'type': 'Type',
        'city': 'City',
        'mountain': 'Mountain',
        'elderly_mountain': 'Elderly Mountain',
        'group': 'Group',
        'min_price': 'Min Price',
        'max_price': 'Max Price',
        'duration': 'Duration (days)',
        'search_button': 'Search',
        'reset': 'Reset',
        'nothing_found': 'Nothing found',
        
        # My Bookings
        'my_bookings_title': 'My Bookings',
        'no_bookings': 'You have no bookings yet.',
        'view_tours': 'View Tours',
        'view_tour': 'View Tour',
        
        # Weather
        'weather': 'Weather',
        'suitable_for_elderly': 'Suitable for 60+ climbs',
        'weather_warning': 'Warning: unfavorable conditions',
    },
    
    'es': {
        # Navigation
        'search': 'Buscar',
        'my_bookings': 'Mis Reservas',
        'login': 'Iniciar Sesión',
        'register': 'Registrarse',
        'logout': 'Cerrar Sesión',
        'admin': 'Admin',
        'home': 'Inicio',
        
        # Common
        'price': 'Precio',
        'days': 'días',
        'passengers': 'pasajeros',
        'total_cost': 'Costo Total',
        'status': 'Estado',
        'confirmed': 'Confirmado',
        'cancelled': 'Cancelado',
        'pending': 'Pendiente',
        
        # Booking
        'booking': 'Reserva',
        'booking_confirmed': '¡Reserva Confirmada!',
        'booking_details': 'Detalles de la Reserva',
        'booking_number': 'Número de Reserva',
        'tour': 'Tour',
        'place': 'Lugar',
        'travel_date': 'Fecha de Viaje',
        'booking_date': 'Fecha de Reserva',
        'contact_info': 'Información de Contacto',
        'name': 'Nombre',
        'email': 'Email',
        'phone': 'Teléfono',
        'cancel_booking': 'Cancelar Reserva',
        'cancel': 'Cancelar',
        
        # Auth
        'login_title': 'Iniciar Sesión',
        'register_title': 'Registro',
        'password': 'Contraseña',
        'confirm_password': 'Confirmar Contraseña',
        'first_name': 'Nombre',
        'last_name': 'Apellido',
        'passport_number': 'Número de Pasaporte',
        'passport_issued_by': 'Emitido Por',
        'passport_issued_date': 'Fecha de Emisión',
        'demo_admin': 'Acceso Demo Admin:',
        
        # Messages
        'booking_cancelled': 'Reserva cancelada exitosamente',
        'booking_error': 'Error al cancelar la reserva',
        'login_required': 'Inicio de sesión requerido',
        'booking_not_found': 'Reserva no encontrada',
        'no_permission': 'No tienes permisos para eliminar esta reserva',
        'too_close_to_travel': 'La reserva no puede cancelarse menos de 3 días antes del viaje',
        'date_error': 'Error en la fecha de viaje',
        'registration_success': '¡Registro exitoso! Ahora puedes iniciar sesión.',
        'login_success': '¡Sesión iniciada exitosamente!',
        'logout_success': 'Has cerrado sesión',
        'invalid_credentials': 'Email o contraseña inválidos',
        'passwords_dont_match': 'Las contraseñas no coinciden',
        'user_exists': 'Ya existe un usuario con este email',
        
        # Forms
        'required': 'requerido',
        'min_passengers': 'Número de Pasajeros',
        'travel_date_label': 'Fecha de Viaje',
        'passport_details': 'Detalles del Pasaporte',
        'booking_summary': 'Resumen de Reserva',
        'price_per_person': 'Precio por Persona',
        
        # Search
        'search_title': 'Buscar',
        'location': 'Ubicación',
        'type': 'Tipo',
        'city': 'Ciudad',
        'mountain': 'Montaña',
        'elderly_mountain': 'Montaña para Mayores',
        'group': 'Grupo',
        'min_price': 'Precio Mín',
        'max_price': 'Precio Máx',
        'duration': 'Duración (días)',
        'search_button': 'Buscar',
        'reset': 'Restablecer',
        'nothing_found': 'Nada encontrado',
        
        # My Bookings
        'my_bookings_title': 'Mis Reservas',
        'no_bookings': 'Aún no tienes reservas.',
        'view_tours': 'Ver Tours',
        'view_tour': 'Ver Tour',
        
        # Weather
        'weather': 'Clima',
        'suitable_for_elderly': 'Adecuado para escaladas 60+',
        'weather_warning': 'Advertencia: condiciones desfavorables',
    }
}

def get_translation(key, language='ru'):
    """Get translation for a key in the specified language"""
    return TRANSLATIONS.get(language, TRANSLATIONS['ru']).get(key, key)

def get_current_language():
    """Get current language from session or default to Russian"""
    from flask import session
    return session.get('language', 'ru')






