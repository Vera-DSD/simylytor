"""
Генератор тестовых данных для демо-сайта
"""
import random
import uuid
from datetime import datetime, timedelta

# Конфигурация
DISTRICTS = ["ЦАО", "САО", "СВАО", "ВАО", "ЮВАО", "ЮАО", "ЮЗАО", "ЗАО", "СЗАО"]
METRO_STATIONS = ["Китай-город", "Охотный ряд", "Тверская", "Пушкинская", "Чеховская", 
                  "Краснопресненская", "Баррикадная", "Арбатская", "Смоленская"]
STREETS = ["ул. Тверская", "ул. Арбат", "пр. Мира", "Ленинский пр-т", "Кутузовский пр-т"]
AMENITIES = ["Wi-Fi", "Кондиционер", "Телевизор", "Стиральная машина", "Холодильник", 
             "Микроволновка", "Духовка", "Посудомоечная машина", "Фен", "Утюг"]
PHOTOS = [
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800",
    "https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=800",
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800",
    "https://images.unsplash.com/photo-1558036117-15e82a2c9a9a?w=800"
]

def generate_apartment():
    """Генерация одной квартиры"""
    rooms = random.choice([1, 1, 2, 2, 3])  # Чаще 1-2 комнатные
    district = random.choice(DISTRICTS)
    metro = random.choice(METRO_STATIONS)
    
    # Цена зависит от комнат и района
    base_price = 25000 if district == "ЦАО" else 20000
    price_per_month = base_price * rooms + random.randint(-3000, 8000)
    
    # Площадь
    area = rooms * 25 + random.randint(-10, 20)
    
    # Этажность
    total_floors = random.choice([5, 9, 12, 16])
    floor = random.randint(1, total_floors)
    
    # Адрес
    street = random.choice(STREETS)
    house = random.randint(1, 100)
    address = f"{district}, {street}, д. {house}"
    
    # Фото
    num_photos = random.randint(2, 4)
    photos = random.sample(PHOTOS, num_photos)
    
    # Удобства
    num_amenities = random.randint(3, 8)
    amenities = random.sample(AMENITIES, num_amenities)
    
    # Телефон и владелец
    phone = f"+7 (9{random.randint(10, 99)}) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
    owners = ["Анна", "Иван", "Мария", "Алексей", "Елена", "Дмитрий"]
    owner_name = f"{random.choice(owners)} {random.choice(['Петрова', 'Сидоров', 'Иванова', 'Смирнов'])}"
    
    return {
        "id": str(uuid.uuid4()),
        "title": f"{rooms}-комнатная квартира в {district}",
        "description": f"Просторная {rooms}-комнатная квартира площадью {area} м². {random.choice(['Современный ремонт', 'Евроремонт', 'Уютная квартира'])}. Рядом метро {metro}.",
        "price_per_month": price_per_month,
        "area": round(area, 1),
        "rooms": rooms,
        "floor": floor,
        "total_floors": total_floors,
        "address": address,
        "district": district,
        "metro": metro,
        "metro_distance": f"{random.choice([5, 7, 10, 15])} мин пешком",
        "photos": photos,
        "amenities": amenities,
        "is_active": random.random() > 0.1,  # 90% активных
        "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
        "views": random.randint(0, 200),
        "phone": phone,
        "owner_name": owner_name
    }

def generate_apartments(count: int = 50):
    """Генерация списка квартир"""
    return [generate_apartment() for _ in range(count)]