from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import json
import random
from datetime import datetime, timedelta
import uuid
import os
from typing import Optional, List, Dict
from pydantic import BaseModel

app = FastAPI(
    title="RentalAI - Платформа аренды с ИИ",
    description="Современная площадка аренды с интегрированным ИИ-агентом",
    version="2.0.0"
)

# Создаем директории
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Подключаем шаблоны
templates = Jinja2Templates(directory="templates")

# Модели Pydantic
class Apartment(BaseModel):
    title: str
    description: str
    price: int
    rooms: int
    area: float
    address: str
    district: str
    metro: str
    photos: List[str] = []
    amenities: List[str] = []
    owner_name: str
    owner_phone: str
    is_ai_enabled: bool = False
    ai_strategies: List[str] = []

class AIStrategyRequest(BaseModel):
    apartment_id: str
    strategies: List[str]
    auto_reviews: bool = False
    auto_messages: bool = False
    analytics: bool = False
    notifications: bool = True

# Инициализация базы данных
def init_database():
    conn = sqlite3.connect("rental_ai.db")
    cursor = conn.cursor()
    
    # Квартиры
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS apartments (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        price INTEGER NOT NULL,
        price_history TEXT,  -- JSON массив исторических цен
        rooms INTEGER NOT NULL,
        area REAL NOT NULL,
        address TEXT NOT NULL,
        district TEXT NOT NULL,
        metro TEXT NOT NULL,
        metro_distance TEXT,
        photos TEXT,  -- JSON массив URL фото
        amenities TEXT,  -- JSON массив удобств
        is_active BOOLEAN DEFAULT 1,
        is_premium BOOLEAN DEFAULT 0,
        is_ai_enabled BOOLEAN DEFAULT 0,
        ai_strategies TEXT,  -- JSON массив стратегий
        views INTEGER DEFAULT 0,
        phone_views INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        owner_name TEXT NOT NULL,
        owner_phone TEXT NOT NULL,
        owner_email TEXT
    )
    ''')
    
    # AI настройки
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ai_settings (
        apartment_id TEXT PRIMARY KEY,
        strategies TEXT NOT NULL,  -- JSON массив
        auto_reviews BOOLEAN DEFAULT 0,
        auto_messages BOOLEAN DEFAULT 1,
        analytics_enabled BOOLEAN DEFAULT 1,
        notifications_enabled BOOLEAN DEFAULT 1,
        price_optimization BOOLEAN DEFAULT 0,
        competitor_analysis BOOLEAN DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (apartment_id) REFERENCES apartments (id)
    )
    ''')
    
    # AI аналитика
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ai_analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        apartment_id TEXT NOT NULL,
        metric TEXT NOT NULL,
        value REAL NOT NULL,
        period TEXT NOT NULL,  -- daily, weekly, monthly
        recorded_at TEXT NOT NULL,
        FOREIGN KEY (apartment_id) REFERENCES apartments (id)
    )
    ''')
    
    # Отзывы (AI генерируемые)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ai_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        apartment_id TEXT NOT NULL,
        review_text TEXT NOT NULL,
        rating INTEGER NOT NULL,
        author_name TEXT NOT NULL,
        is_ai_generated BOOLEAN DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY (apartment_id) REFERENCES apartments (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Генерация тестовых данных
def generate_apartments(count=100):
    conn = sqlite3.connect("rental_ai.db")
    cursor = conn.cursor()
    
    # Проверяем сколько уже есть
    cursor.execute("SELECT COUNT(*) FROM apartments")
    existing = cursor.fetchone()[0]
    
    if existing >= count:
        conn.close()
        return
    
    districts = [
        {"name": "ЦАО", "metros": ["Китай-город", "Охотный ряд", "Тверская", "Пушкинская", "Арбатская"], "price_mult": 1.3},
        {"name": "САО", "metros": ["Войковская", "Сокол", "Аэропорт", "Динамо"], "price_mult": 1.1},
        {"name": "ЮАО", "metros": ["Коломенская", "Нагатинская", "Орехово", "Домодедовская"], "price_mult": 1.0},
        {"name": "ЗАО", "metros": ["Кунцевская", "Молодежная", "Крылатское", "Строгино"], "price_mult": 1.2},
        {"name": "СВАО", "metros": ["ВДНХ", "Алексеевская", "Рижская", "Бабушкинская"], "price_mult": 1.0},
    ]
    
    photos_pool = [
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1558036117-15e82a2c9a9a?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&auto=format&fit=crop",
    ]
    
    amenities_pool = [
        "Wi-Fi", "Кондиционер", "Стиральная машина", "Посудомоечная машина",
        "Телевизор", "Холодильник", "Микроволновка", "Духовка", "Фен", "Утюг",
        "Балкон", "Лифт", "Консьерж", "Парковка", "Тренажерный зал", "Бассейн"
    ]
    
    street_names = [
        "Тверская", "Арбат", "Новый Арбат", "Пятницкая", "Большая Дорогомиловская",
        "Ленинский проспект", "Кутузовский проспект", "проспект Мира", "Шереметьевская",
        "Малая Бронная", "Петровка", "Мясницкая", "Сретенка", "Рождественка"
    ]
    
    owner_names = [
        "Анна Петрова", "Иван Сидоров", "Мария Иванова", "Алексей Смирнов",
        "Елена Кузнецова", "Дмитрий Попов", "Ольга Васильева", "Сергей Петров"
    ]
    
    for i in range(count - existing):
        district = random.choice(districts)
        metro = random.choice(district["metros"])
        rooms = random.choice([1, 2, 3, 4])
        
        # Генерация цены
        base_price = 25000 * rooms * district["price_mult"]
        price = int(base_price + random.randint(-3000, 8000))
        
        # Фото
        num_photos = random.randint(3, 6)
        photos = random.sample(photos_pool, num_photos)
        
        # Удобства
        num_amenities = random.randint(4, 10)
        amenities = random.sample(amenities_pool, num_amenities)
        
        # Адрес
        street = random.choice(street_names)
        address = f"г. Москва, {district['name']}, ул. {street}, д. {random.randint(1, 150)}"
        
        # Описание
        descriptions = [
            f"Просторная {rooms}-комнатная квартира с современным ремонтом в районе {district['name']}. "
            f"Рядом станция метро {metro} ({random.choice(['5', '7', '10', '15'])} минут пешком). "
            f"Идеально подходит для {random.choice(['семьи', 'пары', 'студентов', 'молодых специалистов'])}.",
            
            f"Уютная {rooms}-комнатная квартира в экологически чистом районе. "
            f"Современная планировка, все необходимое для комфортного проживания. "
            f"Развитая инфраструктура, хорошая транспортная доступность.",
            
            f"Светлая {rooms}-комнатная квартира с панорамными окнами. "
            f"Качественный евроремонт, новая техника. {random.choice(['Тихий двор', 'Зеленый двор', 'Двор без машин'])}. "
            f"Отличный вариант для постоянного проживания."
        ]
        
        apartment_id = str(uuid.uuid4())
        created_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Ценовая история (для аналитики)
        price_history = []
        for j in range(5):
            hist_date = created_date - timedelta(days=j*7)
            hist_price = price + random.randint(-2000, 2000)
            price_history.append({
                "date": hist_date.isoformat(),
                "price": hist_price
            })
        
        cursor.execute('''
        INSERT INTO apartments 
        (id, title, description, price, price_history, rooms, area, address, 
         district, metro, metro_distance, photos, amenities, is_active, is_premium,
         is_ai_enabled, ai_strategies, views, phone_views, created_at, updated_at,
         owner_name, owner_phone, owner_email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            apartment_id,
            f"{rooms}-комнатная квартира, {district['name']}, м. {metro}",
            random.choice(descriptions),
            price,
            json.dumps(price_history),
            rooms,
            rooms * 25 + random.randint(10, 30),
            address,
            district["name"],
            metro,
            f"{random.choice([5, 7, 10, 15])} минут пешком",
            json.dumps(photos),
            json.dumps(amenities),
            1,
            random.random() > 0.7,  # 30% премиум
            random.random() > 0.5,  # 50% с ИИ
            json.dumps([] if random.random() > 0.5 else ["price_optimization", "analytics"]),
            random.randint(50, 500),
            random.randint(5, 50),
            created_date.isoformat(),
            datetime.now().isoformat(),
            random.choice(owner_names),
            f"+7 (9{random.randint(10, 99)}) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
            f"owner{random.randint(1, 1000)}@example.com"
        ))
        
        # AI настройки для некоторых квартир
        if random.random() > 0.5:
            strategies = random.sample([
                "price_optimization", 
                "competitor_analysis", 
                "demand_prediction",
                "review_generation",
                "auto_messaging"
            ], random.randint(1, 3))
            
            cursor.execute('''
            INSERT INTO ai_settings 
            (apartment_id, strategies, auto_reviews, auto_messages, analytics_enabled, 
             notifications_enabled, price_optimization, competitor_analysis, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                apartment_id,
                json.dumps(strategies),
                random.random() > 0.3,
                random.random() > 0.2,
                random.random() > 0.1,
                random.random() > 0.1,
                "price_optimization" in strategies,
                "competitor_analysis" in strategies,
                created_date.isoformat(),
                datetime.now().isoformat()
            ))
        
        # AI отзывы для некоторых квартир
        if random.random() > 0.6:
            for _ in range(random.randint(1, 4)):
                cursor.execute('''
                INSERT INTO ai_reviews (apartment_id, review_text, rating, author_name, is_ai_generated, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    apartment_id,
                    random.choice([
                        "Отличная квартира, все соответствует описанию!",
                        "Очень понравилось, чистый ремонт, хорошая техника.",
                        "Удобное расположение, рядом метро и магазины.",
                        "Хозяева приятные, быстро решают все вопросы.",
                        "Рекомендую эту квартиру для аренды!"
                    ]),
                    random.randint(4, 5),
                    random.choice(["Анна", "Иван", "Мария", "Алексей", "Дмитрий"]),
                    1,
                    (created_date + timedelta(days=random.randint(1, 30))).isoformat()
                ))
    
    conn.commit()
    conn.close()

init_database()
generate_apartments(100)

# ==================== ВЕБ-ЭНДПОИНТЫ ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница"""
    conn = sqlite3.connect("rental_ai.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Премиум объявления
    cursor.execute("SELECT * FROM apartments WHERE is_premium = 1 AND is_active = 1 ORDER BY created_at DESC LIMIT 9")
    premium_apartments = []
    for row in cursor.fetchall():
        apt = dict(row)
        apt['photos'] = json.loads(apt['photos']) if apt['photos'] else []
        apt['amenities'] = json.loads(apt['amenities']) if apt['amenities'] else []
        premium_apartments.append(apt)
    
    # Статистика
    cursor.execute("SELECT COUNT(*) FROM apartments WHERE is_active = 1")
    total_apartments = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM apartments WHERE is_ai_enabled = 1 AND is_active = 1")
    ai_enabled = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(price) FROM apartments WHERE is_active = 1")
    avg_price = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM ai_settings")
    ai_settings_count = cursor.fetchone()[0]
    
    conn.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "premium_apartments": premium_apartments,
        "stats": {
            "total_apartments": total_apartments,
            "ai_enabled": ai_enabled,
            "avg_price": round(avg_price),
            "ai_settings_count": ai_settings_count
        }
    })

@app.get("/apartments", response_class=HTMLResponse)
async def apartments_list(
    request: Request,
    page: int = 1,
    per_page: int = 12,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    rooms: Optional[str] = None,
    district: Optional[str] = None,
    metro: Optional[str] = None,
    ai_enabled: Optional[bool] = None
):
    """Список всех объявлений"""
    conn = sqlite3.connect("rental_ai.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Формируем запрос
    query = "SELECT * FROM apartments WHERE is_active = 1"
    params = []
    
    if min_price:
        query += " AND price >= ?"
        params.append(min_price)
    if max_price:
        query += " AND price <= ?"
        params.append(max_price)
    if rooms:
        query += " AND rooms = ?"
        params.append(int(rooms))
    if district:
        query += " AND district = ?"
        params.append(district)
    if metro:
        query += " AND metro LIKE ?"
        params.append(f"%{metro}%")
    if ai_enabled is not None:
        query += " AND is_ai_enabled = ?"
        params.append(1 if ai_enabled else 0)
    
    # Общее количество
    count_query = f"SELECT COUNT(*) FROM ({query})"
    total_count = cursor.execute(count_query, params).fetchone()[0]
    
    # Пагинация
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    
    # Выполняем
    cursor.execute(query, params)
    
    apartments = []
    for row in cursor.fetchall():
        apt = dict(row)
        apt['photos'] = json.loads(apt['photos']) if apt['photos'] else []
        apt['amenities'] = json.loads(apt['amenities']) if apt['amenities'] else []
        apt['ai_strategies'] = json.loads(apt['ai_strategies']) if apt['ai_strategies'] else []
        apartments.append(apt)
    
    # Фильтры
    cursor.execute("SELECT DISTINCT district FROM apartments WHERE district IS NOT NULL ORDER BY district")
    districts = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT metro FROM apartments WHERE metro IS NOT NULL ORDER BY metro")
    metros = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return templates.TemplateResponse("apartments.html", {
        "request": request,
        "apartments": apartments,
        "page": page,
        "per_page": per_page,
        "total_count": total_count,
        "total_pages": (total_count + per_page - 1) // per_page,
        "districts": districts,
        "metros": metros,
        "filters": {
            "min_price": min_price,
            "max_price": max_price,
            "rooms": rooms,
            "district": district,
            "metro": metro,
            "ai_enabled": ai_enabled
        }
    })

@app.get("/apartment/{apartment_id}", response_class=HTMLResponse)
async def apartment_detail(request: Request, apartment_id: str):
    """Детальная страница объявления"""
    conn = sqlite3.connect("rental_ai.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Квартира
    cursor.execute("SELECT * FROM apartments WHERE id = ?", (apartment_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    
    apartment = dict(row)
    apartment['photos'] = json.loads(apartment['photos']) if apartment['photos'] else []
    apartment['amenities'] = json.loads(apartment['amenities']) if apartment['amenities'] else []
    apartment['ai_strategies'] = json.loads(apartment['ai_strategies']) if apartment['ai_strategies'] else []
    apartment['price_history'] = json.loads(apartment['price_history']) if apartment['price_history'] else []
    
    # AI настройки
    cursor.execute("SELECT * FROM ai_settings WHERE apartment_id = ?", (apartment_id,))
    ai_settings_row = cursor.fetchone()
    ai_settings = dict(ai_settings_row) if ai_settings_row else None
    if ai_settings and ai_settings.get('strategies'):
        ai_settings['strategies'] = json.loads(ai_settings['strategies'])
    
    # AI отзывы
    cursor.execute("SELECT * FROM ai_reviews WHERE apartment_id = ? ORDER BY created_at DESC LIMIT 5", (apartment_id,))
    ai_reviews = []
    for row in cursor.fetchall():
        review = dict(row)
        ai_reviews.append(review)
    
    # AI аналитика
    cursor.execute('''
    SELECT metric, value, period, recorded_at 
    FROM ai_analytics 
    WHERE apartment_id = ? AND period = 'monthly'
    ORDER BY recorded_at DESC LIMIT 10
    ''', (apartment_id,))
    analytics = [dict(row) for row in cursor.fetchall()]
    
    # Увеличиваем просмотры
    cursor.execute("UPDATE apartments SET views = views + 1 WHERE id = ?", (apartment_id,))
    
    # Похожие
    cursor.execute('''
    SELECT * FROM apartments 
    WHERE district = ? AND rooms = ? AND id != ? AND is_active = 1 
    ORDER BY RANDOM() LIMIT 3
    ''', (apartment['district'], apartment['rooms'], apartment_id))
    
    similar = []
    for row in cursor.fetchall():
        apt = dict(row)
        apt['photos'] = json.loads(apt['photos']) if apt['photos'] else []
        similar.append(apt)
    
    conn.commit()
    conn.close()
    
    return templates.TemplateResponse("apartment.html", {
        "request": request,
        "apartment": apartment,
        "ai_settings": ai_settings,
        "ai_reviews": ai_reviews,
        "analytics": analytics,
        "similar_apartments": similar
    })

@app.get("/add", response_class=HTMLResponse)
async def add_apartment_form(request: Request):
    """Форма добавления объявления"""
    return templates.TemplateResponse("add.html", {
        "request": request,
        "districts": ["ЦАО", "САО", "СВАО", "ВАО", "ЮВАО", "ЮАО", "ЮЗАО", "ЗАО", "СЗАО"],
        "metros": [
            "Китай-город", "Охотный ряд", "Тверская", "Пушкинская", "Чеховская",
            "Арбатская", "Библиотека им. Ленина", "Кропоткинская", "Парк Культуры"
        ],
        "amenities_list": [
            "Wi-Fi", "Кондиционер", "Стиральная машина", "Посудомоечная машина",
            "Телевизор", "Холодильник", "Микроволновка", "Духовка", "Фен", "Утюг",
            "Балкон", "Лифт", "Консьерж", "Парковка", "Тренажерный зал", "Бассейн"
        ]
    })

@app.post("/api/apartments")
async def create_apartment(
    title: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    rooms: int = Form(...),
    area: float = Form(...),
    address: str = Form(...),
    district: str = Form(...),
    metro: str = Form(...),
    amenities: List[str] = Form([]),
    owner_name: str = Form(...),
    owner_phone: str = Form(...),
    owner_email: str = Form(None),
    is_ai_enabled: bool = Form(False),
    ai_strategies: List[str] = Form([])
):
    """Создание нового объявления"""
    conn = sqlite3.connect("rental_ai.db")
    cursor = conn.cursor()
    
    apartment_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    # Создаем ценовую историю
    price_history = [{"date": now, "price": price}]
    
    cursor.execute('''
    INSERT INTO apartments 
    (id, title, description, price, price_history, rooms, area, address, 
     district, metro, photos, amenities, is_active, is_ai_enabled, ai_strategies,
     views, phone_views, created_at, updated_at, owner_name, owner_phone, owner_email)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        apartment_id,
        title,
        description,
        price,
        json.dumps(price_history),
        rooms,
        area,
        address,
        district,
        metro,
        json.dumps(["https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&auto=format&fit=crop"]),
        json.dumps(amenities),
        1,
        is_ai_enabled,
        json.dumps(ai_strategies),
        0,
        0,
        now,
        now,
        owner_name,
        owner_phone,
        owner_email
    ))
    
    # Если включен ИИ, создаем настройки
    if is_ai_enabled:
        cursor.execute('''
        INSERT INTO ai_settings 
        (apartment_id, strategies, auto_reviews, auto_messages, analytics_enabled, 
         notifications_enabled, price_optimization, competitor_analysis, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            apartment_id,
            json.dumps(ai_strategies),
            1 if "review_generation" in ai_strategies else 0,
            1 if "auto_messaging" in ai_strategies else 0,
            1 if "analytics" in ai_strategies else 0,
            1,
            1 if "price_optimization" in ai_strategies else 0,
            1 if "competitor_analysis" in ai_strategies else 0,
            now,
            now
        ))
    
    conn.commit()
    conn.close()
    
    return RedirectResponse(f"/apartment/{apartment_id}", status_code=303)

@app.get("/apartment/{apartment_id}/ai", response_class=HTMLResponse)
async def ai_configuration(request: Request, apartment_id: str):
    """Страница настройки ИИ-агента"""
    conn = sqlite3.connect("rental_ai.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM apartments WHERE id = ?", (apartment_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    
    apartment = dict(row)
    
    # AI настройки если есть
    cursor.execute("SELECT * FROM ai_settings WHERE apartment_id = ?", (apartment_id,))
    ai_settings_row = cursor.fetchone()
    ai_settings = dict(ai_settings_row) if ai_settings_row else {
        "strategies": [],
        "auto_reviews": False,
        "auto_messages": True,
        "analytics_enabled": True,
        "notifications_enabled": True,
        "price_optimization": False,
        "competitor_analysis": False
    }
    
    if ai_settings.get('strategies'):
        ai_settings['strategies'] = json.loads(ai_settings['strategies'])
    
    conn.close()
    
    return templates.TemplateResponse("ai_config.html", {
        "request": request,
        "apartment": apartment,
        "ai_settings": ai_settings,
        "strategies_list": [
            {"id": "price_optimization", "name": "Оптимизация цены", "desc": "Автоматическая корректировка цены на основе спроса"},
            {"id": "competitor_analysis", "name": "Анализ конкурентов", "desc": "Мониторинг цен конкурентов в районе"},
            {"id": "demand_prediction", "name": "Прогноз спроса", "desc": "Предсказание лучшего времени для аренды"},
            {"id": "review_generation", "name": "Генерация отзывов", "desc": "Автоматическое создание позитивных отзывов"},
            {"id": "auto_messaging", "name": "Автоответы на сообщения", "desc": "ИИ отвечает на вопросы арендаторов"},
            {"id": "analytics", "name": "Подробная аналитика", "desc": "Ежемесячные отчеты и рекомендации"}
        ]
    })

@app.post("/api/apartment/{apartment_id}/ai")
async def update_ai_settings(
    apartment_id: str,
    strategies: List[str] = Form([]),
    auto_reviews: bool = Form(False),
    auto_messages: bool = Form(True),
    analytics_enabled: bool = Form(True),
    notifications_enabled: bool = Form(True),
    price_optimization: bool = Form(False),
    competitor_analysis: bool = Form(False)
):
    """Обновление настроек ИИ"""
    conn = sqlite3.connect("rental_ai.db")
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # Проверяем есть ли уже настройки
    cursor.execute("SELECT COUNT(*) FROM ai_settings WHERE apartment_id = ?", (apartment_id,))
    exists = cursor.fetchone()[0] > 0
    
    if exists:
        cursor.execute('''
        UPDATE ai_settings SET
            strategies = ?,
            auto_reviews = ?,
            auto_messages = ?,
            analytics_enabled = ?,
            notifications_enabled = ?,
            price_optimization = ?,
            competitor_analysis = ?,
            updated_at = ?
        WHERE apartment_id = ?
        ''', (
            json.dumps(strategies),
            1 if auto_reviews else 0,
            1 if auto_messages else 0,
            1 if analytics_enabled else 0,
            1 if notifications_enabled else 0,
            1 if price_optimization else 0,
            1 if competitor_analysis else 0,
            now,
            apartment_id
        ))
    else:
        cursor.execute('''
        INSERT INTO ai_settings 
        (apartment_id, strategies, auto_reviews, auto_messages, analytics_enabled, 
         notifications_enabled, price_optimization, competitor_analysis, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            apartment_id,
            json.dumps(strategies),
            1 if auto_reviews else 0,
            1 if auto_messages else 0,
            1 if analytics_enabled else 0,
            1 if notifications_enabled else 0,
            1 if price_optimization else 0,
            1 if competitor_analysis else 0,
            now,
            now
        ))
    
    # Обновляем флаг в основной таблице
    cursor.execute("UPDATE apartments SET is_ai_enabled = ?, ai_strategies = ?, updated_at = ? WHERE id = ?", 
                  (1 if len(strategies) > 0 else 0, json.dumps(strategies), now, apartment_id))
    
    # Генерируем демо-аналитику если включена
    if analytics_enabled:
        metrics = [
            ("views", random.randint(50, 200)),
            ("contacts", random.randint(5, 20)),
            ("conversion", random.uniform(0.1, 0.3)),
            ("avg_response_time", random.uniform(1, 12)),
            ("satisfaction_score", random.uniform(3.5, 5.0))
        ]
        
        for metric, value in metrics:
            cursor.execute('''
            INSERT INTO ai_analytics (apartment_id, metric, value, period, recorded_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (apartment_id, metric, value, "monthly", now))
    
    conn.commit()
    conn.close()
    
    return RedirectResponse(f"/apartment/{apartment_id}", status_code=303)

@app.get("/api/ai/stats")
async def get_ai_stats():
    """Статистика использования ИИ"""
    conn = sqlite3.connect("rental_ai.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM apartments WHERE is_ai_enabled = 1")
    ai_enabled = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ai_settings")
    ai_settings = cursor.fetchone()[0]
    
    cursor.execute("SELECT strategies FROM ai_settings WHERE strategies IS NOT NULL")
    all_strategies = []
    for row in cursor.fetchall():
        if row[0]:
            all_strategies.extend(json.loads(row[0]))
    
    # Считаем популярность стратегий
    strategy_counts = {}
    for strategy in all_strategies:
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    
    conn.close()
    
    return {
        "status": "success",
        "ai_stats": {
            "total_ai_enabled": ai_enabled,
            "total_ai_settings": ai_settings,
            "strategy_popularity": strategy_counts
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)