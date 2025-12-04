from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from flask import current_app


class TicketmasterService:
    """Small helper around the Ticketmaster Discovery API."""

    _BASE_URL = "https://app.ticketmaster.com/discovery/v2"

    def __init__(self) -> None:
        self._session = requests.Session()

    def fetch_events(
        self,
        city: Optional[str] = None,
        country_code: Optional[str] = None,
        keyword: Optional[str] = None,
        classification_id: Optional[str] = None,
        size: int = 32,
    ) -> List[Dict[str, Any]]:
        api_key = self._get_api_key()
        if not api_key:
            return self._mock_events()

        params: Dict[str, Any] = {
            "apikey": api_key,
            "locale": "*",
            "size": min(size, 200),
            "sort": "date,asc",
        }

        default_country = self._get_config_value("TICKETMASTER_DEFAULT_COUNTRY", "US")
        params["countryCode"] = country_code or default_country

        if city:
            params["city"] = city
        default_keyword = self._get_config_value("TICKETMASTER_DEFAULT_KEYWORD", "tour")
        params["keyword"] = keyword or default_keyword
        if classification_id:
            params["classificationId"] = classification_id

        try:
            response = self._session.get(
                f"{self._BASE_URL}/events.json", params=params, timeout=8
            )
            response.raise_for_status()
            data = response.json()
            events = data.get("_embedded", {}).get("events") or []
            normalized = [self._normalize_event(event) for event in events]
            return normalized or self._mock_events()
        except Exception:
            return self._mock_events()

    def _get_api_key(self) -> str:
        try:
            value = current_app.config.get("TICKETMASTER_API_KEY")
            if value:
                return value
        except RuntimeError:
            pass
        return os.getenv("TICKETMASTER_API_KEY", "")

    def _get_config_value(self, key: str, fallback: str) -> str:
        try:
            return current_app.config.get(key, fallback)
        except RuntimeError:
            return os.getenv(key, fallback)

    def _normalize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        venues = (event.get("_embedded") or {}).get("venues") or [{}]
        venue = venues[0] or {}
        city = (venue.get("city") or {}).get("name") or event.get("city") or ""
        country = (venue.get("country") or {}).get("name") or event.get("country") or ""
        address_parts = [
            venue.get("address", {}).get("line1"),
            venue.get("city", {}).get("name"),
            venue.get("state", {}).get("name"),
            venue.get("country", {}).get("name"),
        ]
        address = ", ".join(filter(None, address_parts))
        images = event.get("images") or []
        hero = next(
            (
                img
                for img in images
                if img.get("ratio") == "16_9" and (img.get("width") or 0) >= 1024
            ),
            images[0] if images else {},
        )
        photo_url = hero.get("url") or "https://images.unsplash.com/photo-1470229538611-16ba8c7ffbd7?q=80&w=1600"

        price_ranges = event.get("priceRanges") or []
        price_min = price_ranges[0].get("min") if price_ranges else None
        price_max = price_ranges[0].get("max") if price_ranges else None
        currency = price_ranges[0].get("currency") if price_ranges else None

        classifications = event.get("classifications") or []
        classification = ""
        genres: List[str] = []
        if classifications:
            primary = classifications[0]
            segment = (primary.get("segment") or {}).get("name")
            genre = (primary.get("genre") or {}).get("name")
            subgenre = (primary.get("subGenre") or {}).get("name")
            classification = genre or segment or ""
            genres = [name for name in [segment, genre, subgenre] if name]

        dates = event.get("dates") or {}
        start = dates.get("start") or {}
        end = dates.get("end") or {}
        start_date = start.get("localDate")
        end_date = end.get("localDate")
        start_time = start.get("localTime")
        duration_days = 1
        try:
            if start_date and end_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                duration_days = max((end_dt - start_dt).days + 1, 1)
        except ValueError:
            duration_days = 1

        description = self._compose_description(
            event,
            venue_name=venue.get("name"),
            address=address,
            city=city,
            country=country,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            price_min=price_min,
            price_max=price_max,
            currency=currency,
            genres=genres,
        )

        return {
            "id": event.get("id"),
            "name": event.get("name", "Live Experience"),
            "city": city or "",
            "country": country or "",
            "address": address,
            "venue": venue.get("name"),
            "timezone": venue.get("timezone") or dates.get("timezone"),
            "image": photo_url,
            "price_min": price_min,
            "price_max": price_max,
            "currency": currency,
            "classification": classification or "experience",
            "genres": genres,
            "start_date": start_date,
            "end_date": end_date,
            "start_time": start_time,
            "url": event.get("url"),
            "description": description,
            "lat": (venue.get("location") or {}).get("latitude"),
            "lng": (venue.get("location") or {}).get("longitude"),
            "duration_days": duration_days,
        }

    def _compose_description(
        self,
        event: Dict[str, Any],
        venue_name: Optional[str],
        address: str,
        city: str,
        country: str,
        start_date: Optional[str],
        start_time: Optional[str],
        end_date: Optional[str],
        price_min: Optional[float],
        price_max: Optional[float],
        currency: Optional[str],
        genres: List[str],
    ) -> str:
        parts: List[str] = []

        info = event.get("info")
        if info:
            parts.append(info.strip())

        please_note = event.get("pleaseNote")
        if please_note:
            parts.append(f"Важно знать: {please_note.strip()}")

        venue_bits = [bit for bit in [venue_name, address] if bit]
        if venue_bits:
            parts.append(f"Площадка: {', '.join(venue_bits)}")

        schedule_bits = []
        if start_date:
            schedule_bits.append(f"Начало: {start_date}")
        if start_time:
            schedule_bits[-1] = f"{schedule_bits[-1]} в {start_time}"
        if end_date and end_date != start_date:
            schedule_bits.append(f"Завершение: {end_date}")
        if schedule_bits:
            parts.append("Расписание: " + "; ".join(schedule_bits))

        if price_min is not None or price_max is not None:
            if price_min is not None and price_max is not None:
                parts.append(
                    f"Билеты: от {price_min:.0f} до {price_max:.0f} {currency or ''}".strip()
                )
            else:
                price_value = price_min or price_max
                parts.append(f"Билеты: {price_value:.0f} {currency or ''}".strip())

        if genres:
            parts.append("Жанры и категории: " + ", ".join(genres))

        seat_map = (event.get("seatmap") or {}).get("staticUrl")
        if seat_map:
            parts.append(f"План зала: {seat_map}")

        if not parts:
            parts.append(f"Тур в {city}, {country}. Живая программа от Ticketmaster.")

        return "\n\n".join(parts)

    def _mock_events(self) -> List[Dict[str, Any]]:
        """Fallback dataset curation — 15 авторских горных туров с программами."""
        return [
            {
                "id": "ALTAI2026BEL",
                "name": "Алтай. Тропа Белухи EXP",
                "city": "Горно-Алтайск",
                "country": "Россия",
                "address": "Эко-станция Тюнгур, Усть-Коксинский район",
                "venue": "Кэмп «Катунь Скай»",
                "timezone": "Asia/Barnaul",
                "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1600&auto=format&fit=crop",
                "price_min": 1190.0,
                "price_max": 1490.0,
                "currency": "USD",
                "classification": "mountain",
                "genres": ["Mountain", "Tracking", "Russia"],
                "start_date": "2026-06-14",
                "end_date": "2026-06-24",
                "start_time": "08:30",
                "url": "https://mikola-travel.example/altai-belukha",
                "description": (
                    "Полноценная 11-дневная программа с акклиматизацией на плато Трёх озёр. "
                    "День 1—2: прибытие в Тюнгур, выпуск в радиальные выходы, проживание в глэмпинге. "
                    "День 3—7: переходы к леднику Акилбек, ночёвки в стационарных домиках с печами, банный день. "
                    "День 8—9: выход к перевалу Делон, восход на рассвете, страховка проводников 60+. "
                    "День 10—11: сплав по бурной Катуни, дегустация алтайского мёда, трансфер в аэропорт. "
                    "Даты выездов: 14.06, 05.07, 19.07. Проживание: 4 ночи в шале, 5 — в комфортабельных палатках, 2 — в гостевом доме."
                ),
                "lat": "50.1067",
                "lng": "86.9953",
                "duration_days": 11,
            },
            {
                "id": "SVANETI2026GEO",
                "name": "Грузия. Сванетия и Ушгули",
                "city": "Местиа",
                "country": "Грузия",
                "address": "Местиа, ул. Лахамула 5",
                "venue": "Бутик-отель Tetnuldi Rise",
                "timezone": "Asia/Tbilisi",
                "image": "https://images.unsplash.com/photo-1476041800959-2f6bb412c8ce?w=1600&auto=format&fit=crop",
                "price_min": 980.0,
                "price_max": 1280.0,
                "currency": "USD",
                "classification": "mountain",
                "genres": ["Mountain", "Culture", "Georgia"],
                "start_date": "2026-07-02",
                "end_date": "2026-07-10",
                "start_time": "09:00",
                "url": "https://mikola-travel.example/svaneti",
                "description": (
                    "9-дневная программа с тремя уровневым маршрутами: для подготовленных, мягкая треккинг-группа и возрастная 55+. "
                    "День 1—2: прилёт в Кутаиси, трансфер в Местиа, исторический брифинг и винный ужин. "
                    "День 3: радиальный маршрут к леднику Чалаади. "
                    "День 4—5: переход Местиа — Адиши — Ипрали, сопровождают джипы с багажом, ночёвки в гостевых домах с душем. "
                    "День 6—7: посещение Ушгули, музей сванских башен, фотосессия на хребте Лагами. "
                    "День 8: релакс в термальных ваннах Цхалтубо. День 9: вылет. "
                    "Каждое размещение — двухместные комнаты с удобствами."
                ),
                "lat": "43.0451",
                "lng": "42.7265",
                "duration_days": 9,
            },
            {
                "id": "PAMIR2026KGZ",
                "name": "Кыргызстан. Пик Ленина BaseCamp",
                "city": "Ош",
                "country": "Кыргызстан",
                "address": "Ош, пр. Масалиева, 17 (офис выдачи)",
                "venue": "Юрточный лагерь «Ачик-Таш»",
                "timezone": "Asia/Bishkek",
                "image": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=1600&auto=format&fit=crop",
                "price_min": 1490.0,
                "price_max": 1990.0,
                "currency": "USD",
                "classification": "mountain",
                "genres": ["Expedition", "Pamir", "Acclimatization"],
                "start_date": "2026-07-18",
                "end_date": "2026-08-01",
                "start_time": "07:45",
                "url": "https://mikola-travel.example/pamirstage",
                "description": (
                    "15 дней: базовый альплагерь у ледника Ленина с мягкой высотной лестницей. "
                    "День 1—3: прибытие в Ош, перелёт в лагерь Ачик-Таш, занятия по ледовой технике. "
                    "День 4—7: подъем в Кэмп 1 (4400 м), ночёвки в утепленных палатках, питание шеф-повара. "
                    "День 8—11: фиксация верёвок, восхождение на пик Раздельная, проживание в домиках 2+1. "
                    "День 12—14: выход на вершину Ленина (по погоде), резервный день. "
                    "День 15: возвращение в Ош, баня, сертификаты. "
                    "Даты старта: 18.07, 02.08, 16.08. Размещение — юрты с печами и комнатами отдыха."
                ),
                "lat": "39.3390",
                "lng": "72.7343",
                "duration_days": 15,
            },
            {
                "id": "ARARAT2026ARM",
                "name": "Армения. Кольцо Арарата 60+",
                "city": "Ереван",
                "country": "Армения",
                "address": "ул. Абовяна 14, Ереван",
                "venue": "Отель Cascade Light",
                "timezone": "Asia/Yerevan",
                "image": "https://images.unsplash.com/photo-1500534310682-0670a3f56d81?w=1600&auto=format&fit=crop",
                "price_min": 870.0,
                "price_max": 1090.0,
                "currency": "USD",
                "classification": "mountain",
                "genres": ["Soft Trek", "Culture", "Armenia"],
                "start_date": "2026-05-12",
                "end_date": "2026-05-20",
                "start_time": "10:00",
                "url": "https://mikola-travel.example/ararat60",
                "description": (
                    "Программа для спокойных горных прогулок: максимум 12 км в день, медслужба 24/7. "
                    "День 1—2: прогулка по Еревану, мастер-класс долмы. "
                    "День 3: панорамы Арарата с монастыря Хор Вирап, дегустация армянских вин. "
                    "День 4—6: мягкий трек по ущелью Нор-Ава, проживание в винодельческих бутик-отелях. "
                    "День 7—8: подъём канатной дорогой Татев, день релакса в СПА на высоте. "
                    "День 9: выезд домой. "
                    "Проживание: 4* номера, 2 ночи — эковиллы Dilijan Lodge. Вылеты каждые две недели с 12 мая по 14 сентября."
                ),
                "lat": "40.1792",
                "lng": "44.4991",
                "duration_days": 9,
            },
            {
                "id": "PYRENEES2026ESP",
                "name": "Испания. Пиренеи Camino del Cielo",
                "city": "Барбастро",
                "country": "Испания",
                "address": "Refugio de Gabardito, Huesca",
                "venue": "Refugio del Cielo",
                "timezone": "Europe/Madrid",
                "image": "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=1600&auto=format&fit=crop",
                "price_min": 1320.0,
                "price_max": 1680.0,
                "currency": "EUR",
                "classification": "mountain",
                "genres": ["Trek", "Pyrenees", "Spain"],
                "start_date": "2026-09-04",
                "end_date": "2026-09-13",
                "start_time": "08:00",
                "url": "https://mikola-travel.example/camino-cielo",
                "description": (
                    "10-дневный маршрут через парк Ордеса-И-Монте-Пердидо. "
                    "День 1: встреча в Барселоне, переезд в долину Арагон. "
                    "День 2—4: трек по каньону Ордеса с ночёвками в горных рефуджио с горячим душем. "
                    "День 5: отдых, гастрономический тур по вину сомонтано. "
                    "День 6—8: переход к границе Франции, восхождение на Монте-Пердидо (3355 м) с гидом UIAGM. "
                    "День 9—10: спуск через долину Пинета, завершающий ужин в Сарагосе. "
                    "Даты стартов: 04.09 и 18.09. Размещение — 4 ночи в бутик-отелях, 5 — в оборудованных рефуджио."
                ),
                "lat": "42.6834",
                "lng": "0.1252",
                "duration_days": 10,
            },
            {
                "id": "DOLOMITI2026ITA",
                "name": "Италия. Доломиты Alta Via Relax",
                "city": "Кортина-д'Ампеццо",
                "country": "Италия",
                "address": "Via Roma 45, Cortina",
                "venue": "Hotel Cristallo Trail",
                "timezone": "Europe/Rome",
                "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1600&auto=format&fit=crop",
                "price_min": 1520.0,
                "price_max": 1890.0,
                "currency": "EUR",
                "classification": "mountain",
                "genres": ["Via Ferrata", "Italy", "Wellness"],
                "start_date": "2026-07-11",
                "end_date": "2026-07-19",
                "start_time": "09:15",
                "url": "https://mikola-travel.example/dolomiti",
                "description": (
                    "8 ходовых дней + 2 дня восстановления. "
                    "День 1—2: ознакомительные маршруты на Тре-Чиме, проживание 5*. "
                    "День 3—6: участки Alta Via 1, ночёвки в рефуджио с панорамой Лагазуой. "
                    "День 7: СПА-день в Cortina Wellness с криокапсулами. "
                    "День 8—9: экскурсия по винодельням Вальдоббьядене и поход на рассвет к озеру Брайес. "
                    "День 10: отъезд. "
                    "Каждая дата (11.07, 08.08, 05.09) включает частного гида и трансфер багажа."
                ),
                "lat": "46.5405",
                "lng": "12.1357",
                "duration_days": 9,
            },
            {
                "id": "PATAGONIA2026CHL",
                "name": "Чили. Торрес-дель-Пайне W+Ice",
                "city": "Пуэрто-Наталес",
                "country": "Чили",
                "address": "Puerto Natales, Manuel Bulnes 236",
                "venue": "Эко-лодж Grey Lights",
                "timezone": "America/Punta_Arenas",
                "image": "https://images.unsplash.com/photo-1500534312191-6722050c5f4c?w=1600&auto=format&fit=crop",
                "price_min": 1990.0,
                "price_max": 2590.0,
                "currency": "USD",
                "classification": "mountain",
                "genres": ["Patagonia", "Glacier", "Chile"],
                "start_date": "2026-11-06",
                "end_date": "2026-11-16",
                "start_time": "07:30",
                "url": "https://mikola-travel.example/patagonia-w",
                "description": (
                    "11-дневный маршрут W с расширением на ледник Грей. "
                    "День 1—2: Сантьяго → Пунта-Аренас → Puerto Natales, чек-лист с гидами. "
                    "День 3—6: участки Base Las Torres и Valle del Francés, ночёвки в домиках Refugio Central и Cuernos. "
                    "День 7—8: катамаран по озеру Пеое, ледовое треккинг-шоу на Grey. "
                    "День 9: день отдыха, уроки кухни на траве Матэ. "
                    "День 10—11: переезд в Пунта-Аренас и вылет. "
                    "Проживание: 6 ночей в домиках, 3 — в эко-лодже, 1 — в отеле 4*."
                ),
                "lat": "-51.6723",
                "lng": "-72.5056",
                "duration_days": 11,
            },
            {
                "id": "ANNAPURNA2026NPL",
                "name": "Непал. Панорама Аннапурны Light",
                "city": "Покхара",
                "country": "Непал",
                "address": "Lakeside Rd 6, Pokhara",
                "venue": "Boutique Lake View",
                "timezone": "Asia/Kathmandu",
                "image": "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?w=1600&auto=format&fit=crop",
                "price_min": 1380.0,
                "price_max": 1750.0,
                "currency": "USD",
                "classification": "mountain",
                "genres": ["Himalaya", "Tea House", "Nepal"],
                "start_date": "2026-10-05",
                "end_date": "2026-10-17",
                "start_time": "06:45",
                "url": "https://mikola-travel.example/annapurna-light",
                "description": (
                    "12-дневный маршрут Ghorepani — Poon Hill — Mardi Ridge. "
                    "День 1—3: Катманду, перелёт в Покхару, подготовка с гидом. "
                    "День 4—8: трек по чайным домикам (макс 9 км/день), зарядки йогой на рассвете. "
                    "День 9: подъём на Mardi View (4200 м), вид на Аннапурну и Мачапучаре. "
                    "День 10: отдых в горячих источниках Джину Данда. "
                    "День 11—12: возврат и шопинг в Тамеле. "
                    "Проживание: 5 ночей — бутик-отели, 6 — лучшие tea-houses с душем."
                ),
                "lat": "28.2096",
                "lng": "83.9856",
                "duration_days": 12,
            },
            {
                "id": "ATLAS2026MAR",
                "name": "Марокко. Вершины Высокого Атласа",
                "city": "Имлиль",
                "country": "Марокко",
                "address": "Imlil Center, High Atlas",
                "venue": "Kasbah Atlas Lodge",
                "timezone": "Africa/Casablanca",
                "image": "https://images.unsplash.com/photo-1500534312119-1c58b7b6ee4d?w=1600&auto=format&fit=crop",
                "price_min": 1180.0,
                "price_max": 1440.0,
                "currency": "EUR",
                "classification": "mountain",
                "genres": ["Atlas", "Culture", "Morocco"],
                "start_date": "2026-03-08",
                "end_date": "2026-03-16",
                "start_time": "08:00",
                "url": "https://mikola-travel.example/atlas",
                "description": (
                    "8 ходовых дней с восхождением на Джебель Тубкаль (4167 м). "
                    "День 1—2: Марракеш, кулинарный тур. День 3—4: трек до святилища Сиди-Шамхаруш, ночёвки в риядах. "
                    "День 5: восхождение на Тубкаль на восходе, сопровождает команда мулаев. "
                    "День 6: хаммам и медитация в долине Ассаи. "
                    "День 7—8: переезд в Эссуэйру, океанские прогулки. "
                    "Проживание: 3 ночи — рияд 4*, 3 — горный приют, 2 — бутик-отель на побережье. "
                    "Даты стартов: ежемесячно с марта по май."
                ),
                "lat": "31.1317",
                "lng": "-7.9216",
                "duration_days": 9,
            },
            {
                "id": "KILI2026TZA",
                "name": "Танзания. Килиманджаро Lemosho Comfort",
                "city": "Моши",
                "country": "Танзания",
                "address": "Shantytown Rd, Moshi",
                "venue": "Kibo View Hotel",
                "timezone": "Africa/Dar_es_Salaam",
                "image": "https://images.unsplash.com/photo-1454496522488-7a8e488e8606?w=1600&auto=format&fit=crop",
                "price_min": 2350.0,
                "price_max": 2890.0,
                "currency": "USD",
                "classification": "mountain",
                "genres": ["Summit", "Africa", "Safari"],
                "start_date": "2026-01-15",
                "end_date": "2026-01-26",
                "start_time": "07:00",
                "url": "https://mikola-travel.example/kilimanjaro",
                "description": (
                    "11-дневная экспедиция по маршруту Лемошо с поддержкой носильщиков и оксиген-станцией. "
                    "День 1—2: прибытие в Моши, проверка снаряжения. "
                    "День 3—8: постепенные переходы через лес, ширу-плато и лавовые башни, тёплые шатры Walk-in. "
                    "День 9: ночной штурм Ухуру, спуск к Миллениум Кэмп. "
                    "День 10—11: сафари в Нгоронгоро, перелёт домой. "
                    "Проживание: 4* отель + комфортабельные палатки с кроватями."
                ),
                "lat": "-3.3349",
                "lng": "37.3473",
                "duration_days": 11,
            },
            {
                "id": "LOFOTEN2026NOR",
                "name": "Норвегия. Лофотены Sky Cabins",
                "city": "Свольвер",
                "country": "Норвегия",
                "address": "Svolvær Havn, Lofoten",
                "venue": "Aurora Sky Cabins",
                "timezone": "Europe/Oslo",
                "image": "https://images.unsplash.com/photo-1482192505345-5655af888cc4?w=1600&auto=format&fit=crop",
                "price_min": 1860.0,
                "price_max": 2190.0,
                "currency": "EUR",
                "classification": "mountain",
                "genres": ["Arctic", "Northern Lights", "Norway"],
                "start_date": "2026-02-14",
                "end_date": "2026-02-22",
                "start_time": "10:30",
                "url": "https://mikola-travel.example/lofoten",
                "description": (
                    "Зимняя программа с мягкими подъёмами и охотой за северным сиянием. "
                    "День 1—2: прибытие в Бодо, переход на экспресс-корабле в Свольвер, размещение в стеклянных кабинах. "
                    "День 3—5: снегоходные туры на плато Хеннингсвер, посещение саамского лагеря. "
                    "День 6: каякинг среди фьордов. День 7: трек к пляжу Квалвика, фотосессия с гидом. "
                    "День 8—9: свободный день, дегустация трески, обратный вылет. "
                    "Размещение: Sky-cabins с панорамой, завтраки Nordic."
                ),
                "lat": "68.2345",
                "lng": "14.5683",
                "duration_days": 9,
            },
            {
                "id": "ALMATY2026KAZ",
                "name": "Казахстан. Тянь-Шань Alpine Escape",
                "city": "Алматы",
                "country": "Казахстан",
                "address": "ул. Тәуелсіздік 32, Алматы",
                "venue": "Alatau Wellness Resort",
                "timezone": "Asia/Almaty",
                "image": "https://images.unsplash.com/photo-1465804575741-338df8554e02?w=1600&auto=format&fit=crop",
                "price_min": 960.0,
                "price_max": 1290.0,
                "currency": "USD",
                "classification": "mountain",
                "genres": ["Kazakhstan", "Glacier", "Wellness"],
                "start_date": "2026-06-01",
                "end_date": "2026-06-08",
                "start_time": "08:00",
                "url": "https://mikola-travel.example/almaty",
                "description": (
                    "7-дневная программа с проживанием на курорте 4* и ежедневными выходами в горы. "
                    "День 1: обзорная по Алматы, вечер в банном комплексе. "
                    "День 2—3: трек к Большому Алматинскому озеру и леднику Турген. "
                    "День 4: мастер-класс кочевой кухни, конный переход по Каскелена. "
                    "День 5: восхождение на пик Фурманова (3355 м) со страховкой. "
                    "День 6: свободное время, СПА. День 7: вылет. "
                    "Проживание: двухместные номера Superior, питание HB."
                ),
                "lat": "43.2220",
                "lng": "76.8512",
                "duration_days": 7,
            },
            {
                "id": "LADAKH2026IND",
                "name": "Индия. Высокогорный Ладакх и Тсо-Мори",
                "city": "Лех",
                "country": "Индия",
                "address": "Leh Bazaar Rd, Ladakh",
                "venue": "Heritage Stok Palace",
                "timezone": "Asia/Kolkata",
                "image": "https://images.unsplash.com/photo-1482192597420-4817fdd7e8b0?w=1600&auto=format&fit=crop",
                "price_min": 1670.0,
                "price_max": 2090.0,
                "currency": "USD",
                "classification": "mountain",
                "genres": ["Himalaya", "Culture", "India"],
                "start_date": "2026-08-09",
                "end_date": "2026-08-20",
                "start_time": "09:30",
                "url": "https://mikola-travel.example/ladakh",
                "description": (
                    "12-дневное путешествие по храмам и солёным озёрам Ладакха. "
                    "День 1—3: акклиматизация в Лехе, монастыри Химис и Тиксей, дыхательные практики. "
                    "День 4—6: джип-сафари через перевал Чанла (5360 м) к озеру Панггонг, ночёвка в юрточном кемпе. "
                    "День 7—9: трек вдоль озера Тсо-Мори с палатками и мобильным душем. "
                    "День 10: горячие источники Чуматанг. День 11—12: перелёт домой через Дели. "
                    "Проживание: 5 ночей — бутик-отели Heritage, 4 — кемп на высоте, 2 — палатки повышенной комфортности."
                ),
                "lat": "34.1526",
                "lng": "77.5770",
                "duration_days": 12,
            },
            {
                "id": "COLORADO2026USA",
                "name": "США. Колорадо High Country 4x4",
                "city": "Аспен",
                "country": "США",
                "address": "Aspen Highlands Village, CO",
                "venue": "Basecamp Maroon Bells",
                "timezone": "America/Denver",
                "image": "https://images.unsplash.com/photo-1500534314215-5f23a5cd5243?w=1600&auto=format&fit=crop",
                "price_min": 1890.0,
                "price_max": 2350.0,
                "currency": "USD",
                "classification": "mountain",
                "genres": ["Rockies", "Overland", "USA"],
                "start_date": "2026-07-25",
                "end_date": "2026-08-02",
                "start_time": "08:00",
                "url": "https://mikola-travel.example/colorado",
                "description": (
                    "8 ходовых дней по альпийским лугам и перевалам Maroon Bells—Snowmass. "
                    "День 1—2: обучение вождения 4x4, подбор высотного питания. "
                    "День 3—5: комбинированные маршруты пешком + Jeep к перевалам Independence и Cottonwood, ночёвки в шале. "
                    "День 6: рыбалка на озере Турквойз и барбекю. "
                    "День 7: восхождение на Mt. Elbert (4399 м) в формате рассветного выхода. "
                    "День 8—9: расслабление в Glenwood Hot Springs, вылет. "
                    "Проживание: 5* ложи, питание full board."
                ),
                "lat": "39.1911",
                "lng": "-106.8175",
                "duration_days": 9,
            },
            {
                "id": "JAPAN2026ALPS",
                "name": "Япония. Северные Альпы и онсены",
                "city": "Мацумото",
                "country": "Япония",
                "address": "Kamikochi Bus Terminal, Nagano",
                "venue": "Kamikochi Imperial Lodge",
                "timezone": "Asia/Tokyo",
                "image": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=1600&auto=format&fit=crop",
                "price_min": 2140.0,
                "price_max": 2590.0,
                "currency": "USD",
                "classification": "mountain",
                "genres": ["Japan Alps", "Onsen", "Gastronomy"],
                "start_date": "2026-09-16",
                "end_date": "2026-09-25",
                "start_time": "09:00",
                "url": "https://mikola-travel.example/japan-alps",
                "description": (
                    "10-дневная программа: пики Яридакэ и Хотаке, онсен-отели и дегустации кайсэки. "
                    "День 1—2: Токио → Мацумото, экскурсия по замку. "
                    "День 3—6: поход по долине Камикочи, ночёвки в горных рёканах с татами. "
                    "День 7: подъём на Яридакэ (3180 м) с легкими перилами. "
                    "День 8: отдых в онсене Хираиуа, чайная церемония. "
                    "День 9—10: переезд в Токио, гастрономический тур. "
                    "Размещение: 4 ночи — рёканы, 3 — горные домики, 2 — отель в Токио."
                ),
                "lat": "36.2354",
                "lng": "137.6460",
                "duration_days": 10,
            },
        ]


ticketmaster_service = TicketmasterService()



