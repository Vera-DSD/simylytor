"""
Генератор тестовых данных для демо-сайта аренды жилья
"""
import random
import json
from datetime import datetime, timedelta
import uuid

# Конфигурация
DISTRICTS = [
    "ЦАО (Центральный)", "САО (Северный)", "СВАО (Северо-Восточный)",
    "ВАО (Восточный)", "ЮВАО (Юго-Восточный)", "ЮАО (Южный)",
    "ЮЗАО (Юго-Западный)", "ЗАО (Западный)", "СЗАО (Северо-Западный)"
]

METRO_STATIONS = [
    "Китай-город", "Охотный ряд", "Тверская", "Пушкинская", "Чеховская",
    "Краснопресненская", "Баррикадная", "Арбатская", "Смоленская",
    "Кропоткинская", "Библиотека им. Ленина", "Александровский сад",
    "Боровицкая", "Полянка", "Серпуховская", "Тульская", "Нагатинская",
    "Нагорная", "Нахимовский проспект", "Севастопольская", "Чертановская"
]

STREETS = [
    "ул. Тверская", "ул. Арбат", "пр. Мира", "Ленинский проспект",
    "Кутузовский проспект", "ул. Новый Арбат", "ул. Пятницкая",
    "ул. Большая Дорогомиловская", "ул. Маросейка", "ул. Покровка",
    "ул. Мясницкая", "ул. Сретенка", "ул. Рождественка", "ул. Петровка",
    "ул. Неглинная", "ул. Дмитровка", "ул. Страстной бульвар",
    "ул. Цветной бульвар", "ул. Чистопрудный бульвар", "ул. Гоголевский бульвар"
]

AMENITIES = [
    "Wi-Fi", "Кондиционер", "Телевизор", "Стиральная машина",
    "Посудомоечная машина", "Холодильник", "Микроволновая печь",
    "Духовка", "Кофемашина", "Фен", "Утюг", "Гладильная доска",
    "Отопление", "Горячая вода", "Лифт", "Консьерж",
    "Парковка", "Тренажерный зал", "Бассейн", "Спа"
]

PHOTOS_POOL = [
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800",
    "https://images.unsplash.com/photo-1518780664697-55e3ad937233?w-800",
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800",
    "https://images.unsplash.com/photo-1558036117-15e82a2c9a9a?w=800",
    "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800",
    "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?w=800",
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800",
    "https://images.unsplash.com/photo-1600566752355-35792bedcfea?w=800",
    "https://images.unsplash.com/photo-1600607687644-c7171b42498b?w=800"
]

OWNER_NAMES = [
    "Анна Петрова", "Иван Сидоров", "Мария Иванова", "Алексей Смирнов",
    "Елена Кузнецова", "Дмитрий Попов", "Ольга Васильева", "Сергей Петров",
    "Татьяна Николаева", "Андрей Орлов", "Наталья Волкова", "Павел Семенов"
]

PHONE_NUMBERS = [
    "+7 (916) 123-45-67", "+7 (925) 234-56-78", "+7 (903) 345-67-89",
    "+7 (985) 456-78-90", "+7 (999) 567-89-01", "+7 (977) 678-90-12"
]

def generate_title(rooms: int, district: str) -> str:
    """Генерация заголовка объявления"""
    room_names = {
        1: "Однокомнатная",
        2: "Двухкомнатная", 
        3: "Трехкомнатная",
        4: "Четырехкомнатная",
        5: "Пятикомнатная"
    }
    
    room_word = room_names.get(rooms, f"{rooms}-комнатная")
    adjectives = ["Светлая", "Уютная", "Современная", "Просторная", "Стильная"]
    
    return f"{random.choice(adjectives)} {room_word} квартира в {district}"

def generate_description(rooms: int, area: float, amenities: list) -> str:
    """Генерация описания"""
    base_descriptions = [
        f"Просторная {rooms}-комнатная квартира площадью {area} м².",
        f"Уютное жилье для комфортного проживания.",
        f"Идеальный вариант для семьи или работы в Москве.",
        f"Современный ремонт, все необходимое для жизни.",
        f"Отличное расположение, развитая инфраструктура."
    ]
    
    amenities_text = ", ".join(amenities[:5])
    
    return f"{random.choice(base_descriptions)} В квартире есть: {amenities_text}."

def generate_address(district: str, metro: str) -> str:
    """Генерация адреса"""
    street = random.choice(STREETS)
    house = random.randint(1, 150)
    building = random.choice(["", f", корпус {random.randint(1, 10)}"])
    
    return f"{district}, {street}, д. {house}{building}"

def generate_metro_distance() -> str:
    """Генерация расстояния до метро"""
    distances = ["5 минут пешком", "10 минут пешком", "15 минут пешком", 
                 "5 минут на транспорте", "10 минут на транспорте"]
    return random.choice(distances)

def generate_photos() -> list:
    """Генерация списка фото"""
    num_photos = random.randint(3, 8)
    return random.sample(PHOTOS_POOL, num_photos)

def generate_amenities() -> list:
    """Генерация списка удобств"""
    num_amenities = random.randint(5, 12)
    return random.sample(AMENITIES, num_amenities)

def generate_apartment() -> dict:
    """Генерация одной квартиры"""
    rooms = random.choice([1, 2, 3, 4])
    district = random.choice(DISTRICTS)
    metro = random.choice(METRO_STATIONS)
    
    # Цена зависит от количества комнат
    base_price = rooms * 25000
    price_per_month = random.randint(base_price - 5000, base_price + 15000)
    price = price_per_month * random.randint(200, 300)  # общая стоимость
    
    # Площадь зависит от комнат
    base_area = rooms * 30
    area = random.uniform(base_area - 10, base_area + 20)
    
    # Генерация координат (Москва)
    lat = 55.7 + random.uniform(-0.1, 0.1)
    lon = 37.6 + random.uniform(-0.1, 0.1)
    
    # Этажность
    total_floors = random.choice([5, 9, 12, 16, 25])
    floor = random.randint(1, total_floors)
    
    amenities = generate_amenities()
    
    apartment = {
        "id": str(uuid.uuid4()),
        "title": generate_title(rooms, district),
        "description": generate_description(rooms, area, amenities),
        "price": price,
        "price_per_month": price_per_month,
        "area": round(area, 1),
        "rooms": rooms,
        "floor": floor,
        "total_floors": total_floors,
        "address": generate_address(district, metro),
        "district": district,
        "metro": metro,
        "metro_distance": generate_metro_distance(),
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "photos": generate_photos(),
        "amenities": amenities,
        "is_active": random.random() > 0.1,  # 90% активных
        "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
        "updated_at": datetime.now().isoformat(),
        "views": random.randint(0, 500),
        "phone": random.choice(PHONE_NUMBERS),
        "owner_name": random.choice(OWNER_NAMES)
    }
    
    return apartment

def generate_apartments(count: int = 100) -> list:
    """Генерация списка квартир"""
    return [generate_apartment() for _ in range(count)]

if __name__ == "__main__":
    # Тест генерации
    apt = generate_apartment()
    print(f"Сгенерирована квартира: {apt['title']}")
    print(f"Цена: {apt['price_per_month']} руб/мес")
    print(f"Адрес: {apt['address']}")
    print(f"Метро: {apt['metro']} ({apt['metro_distance']})")