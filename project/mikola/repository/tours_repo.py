from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from ..models import Tour
from ..services.ticketmaster_service import ticketmaster_service


class ToursRepository:
    _DEFAULT_PHOTO = "https://images.unsplash.com/photo-1470229538611-16ba8c7ffbd7?q=80&w=1600&auto=format&fit=crop"
    _MIN_LEAD_DAYS = 30

    def __init__(self) -> None:
        self._tours: List[Tour] = []
        self.sync_events()

    def sync_events(
        self,
        city: Optional[str] = None,
        keyword: Optional[str] = None,
        classification_id: Optional[str] = None,
    ) -> None:
        events = ticketmaster_service.fetch_events(
            city=city,
            keyword=keyword,
            classification_id=classification_id,
        )
        if events:
            mapped = self._map_events(events)
            self._tours = self._filter_future_ready(mapped)

    def _map_events(self, events: List[dict]) -> List[Tour]:
        mapped: List[Tour] = []
        for idx, event in enumerate(events, start=1):
            price_anchor = event.get("price_min") or event.get("price_max") or 0.0
            description = self._compose_description(event)
            photo_url = (
                event.get("image")
                or event.get("photo_url")
                or self._DEFAULT_PHOTO
            )
            mapped.append(
                Tour(
                    id=idx,
                    title=event.get("name", "Live Experience"),
                    description=description,
                    price=float(price_anchor),
                    city=event.get("city", ""),
                    country=event.get("country", ""),
                    type=event.get("classification", "experience"),
                    duration_days=event.get("duration_days") or 1,
                    photo_url=photo_url,
                    venue=event.get("venue"),
                    address=event.get("address"),
                    timezone=event.get("timezone"),
                    start_date=event.get("start_date"),
                    end_date=event.get("end_date"),
                    start_time=event.get("start_time"),
                    ticket_url=event.get("url"),
                    currency=event.get("currency"),
                    min_price=event.get("price_min"),
                    max_price=event.get("price_max"),
                    external_id=event.get("id"),
                    lat=event.get("lat"),
                    lng=event.get("lng"),
                    categories=event.get("genres") or [],
                )
            )
        return mapped

    def _filter_future_ready(self, tours: List[Tour]) -> List[Tour]:
        """Keep only tours that start at least `_MIN_LEAD_DAYS` in the future."""
        if not tours:
            return tours

        threshold = datetime.utcnow().date() + timedelta(days=self._MIN_LEAD_DAYS)
        filtered: List[Tour] = []
        for tour in tours:
            if not tour.start_date:
                filtered.append(tour)
                continue
            try:
                start_date = datetime.strptime(tour.start_date, "%Y-%m-%d").date()
            except ValueError:
                filtered.append(tour)
                continue
            if start_date >= threshold:
                filtered.append(tour)

        # If everything was filtered out, keep the original list so UI isn't empty.
        return filtered or tours

    def _compose_description(self, event: dict) -> str:
        base_description = event.get("description") or ""
        details: List[str] = [base_description] if base_description else []

        venue = event.get("venue")
        address = event.get("address")
        if venue or address:
            details.append(
                f"Площадка проведения: {venue or 'уточняется'} ({address or 'адрес уточняется'})."
            )

        schedule_bits = []
        if event.get("start_date"):
            start = event["start_date"]
            if event.get("start_time"):
                start = f"{start} в {event['start_time']}"
            schedule_bits.append(f"Старт программы: {start}")
        if event.get("end_date") and event["end_date"] != event.get("start_date"):
            schedule_bits.append(f"Завершение: {event['end_date']}")
        if schedule_bits:
            details.append("Расписание: " + "; ".join(schedule_bits))

        min_price = event.get("price_min")
        max_price = event.get("price_max")
        if min_price is not None or max_price is not None:
            currency = event.get("currency") or ""
            if min_price is not None and max_price is not None:
                details.append(
                    f"Диапазон стоимости билетов: {min_price:.0f}–{max_price:.0f} {currency}."
                )
            else:
                price = min_price if min_price is not None else max_price
                details.append(f"Ориентировочная стоимость: {price:.0f} {currency}.")

        if event.get("genres"):
            details.append("Категории тура: " + ", ".join(event["genres"]) + ".")

        if event.get("url"):
            details.append(f"Билеты и детали: {event['url']}")

        if not details:
            details.append(
                "Актуальная информация о мероприятии будет опубликована организатором Ticketmaster."
            )

        return "\n\n".join(details)

    def list_featured(self, limit: int = 6) -> List[Tour]:
        if not self._tours:
            self.sync_events()
        return self._tours[:limit]

    def get_by_id(self, tour_id: int) -> Optional[Tour]:
        return next((t for t in self._tours if t.id == tour_id), None)

    def search(
        self,
        location: str = "",
        type: str = "",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        duration: Optional[int] = None,
        keyword: str = "",
    ) -> List[Tour]:
        # Refresh from Ticketmaster with the provided query to keep data real-time.
        city_param = location or None
        keyword_param = keyword or None
        self.sync_events(city=city_param, keyword=keyword_param)

        q = [*self._tours]
        if location:
            loc = location.lower()
            q = [t for t in q if loc in t.city.lower() or loc in t.country.lower()]
        if type:
            q = [t for t in q if t.type.lower() == type.lower()]
        if min_price is not None:
            q = [t for t in q if (t.price or 0) >= min_price]
        if max_price is not None:
            q = [t for t in q if (t.price or 0) <= max_price]
        if duration is not None:
            q = [t for t in q if t.duration_days == duration]
        if keyword:
            kw = keyword.lower()
            q = [
                t
                for t in q
                if kw in t.title.lower() or kw in t.description.lower()
            ]
        return q


tours_repository = ToursRepository()

