from flask import Flask, render_template, request, redirect, jsonify
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Создаем директории если их нет
os.makedirs('data', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

DB_FILE = 'data/apartments.json'
AI_FILE = 'data/ai_settings.json'

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump([
                {
                    "id": "1", "title": "Светлая 2-комнатная в центре", "price": 85000,
                    "rooms": 2, "area": 65.5, "district": "Центральный", "metro": "Тверская",
                    "address": "ул. Тверская, д. 15", "description": "Просторная квартира с ремонтом",
                    "owner_name": "Иван Иванов", "owner_phone": "+7 (999) 123-45-67",
                    "is_ai_enabled": True, "is_premium": True, "views": 125,
                    "ai_strategies": ["price_optimization", "auto_messages"]
                },
                {
                    "id": "2", "title": "Уютная 1-комнатная у метро", "price": 45000,
                    "rooms": 1, "area": 38, "district": "СЗАО", "metro": "Строгино",
                    "address": "ул. Таллинская, д. 8", "description": "Уютная квартира",
                    "owner_name": "Анна Петрова", "owner_phone": "+7 (987) 654-32-10",
                    "is_ai_enabled": False, "is_premium": False, "views": 89,
                    "ai_strategies": []
                },
                {
                    "id": "3", "title": "Трешка в новостройке", "price": 120000,
                    "rooms": 3, "area": 95, "district": "ЮЗАО", "metro": "Тропарёво",
                    "address": "ул. Академика Анохина, д. 32", "description": "Современная квартира",
                    "owner_name": "Сергей Сидоров", "owner_phone": "+7 (926) 111-22-33",
                    "is_ai_enabled": True, "is_premium": True, "views": 210,
                    "ai_strategies": ["price_optimization", "analytics"]
                }
            ], f, indent=2)
    
    if not os.path.exists(AI_FILE):
        with open(AI_FILE, 'w') as f:
            json.dump({}, f)

def load_apartments():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_apartments(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_ai_settings():
    try:
        with open(AI_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

# Главная страница
@app.route('/')
def index():
    apartments = load_apartments()
    stats = {
        'total_apartments': len(apartments),
        'ai_enabled': len([a for a in apartments if a.get('is_ai_enabled', False)]),
        'avg_price': sum(a.get('price', 0) for a in apartments) / max(len(apartments), 1),
        'ai_settings_count': len(load_ai_settings())
    }
    return render_template('index.html', 
                         stats=stats, 
                         apartments=apartments[:6],
                         premium_apartments=[a for a in apartments if a.get('is_premium', False)][:3],
                         total_apartments=len(apartments))

# Страница всех объявлений
@app.route('/apartments')
def apartments_list():
    data = load_apartments()
    return render_template('apartments.html', 
                         apartments=data, 
                         total_count=len(data),
                         districts=["Центральный", "СЗАО", "ЮЗАО", "ВАО", "ЗАО"],
                         metros=["Тверская", "Строгино", "Тропарёво", "Курская", "Киевская"])

# Страница объявления
@app.route('/apartment/<id>')
def apartment_detail(id):
    data = load_apartments()
    apt = next((x for x in data if x['id'] == id), None)
    if not apt:
        return "Объявление не найдено", 404
    
    # Увеличиваем просмотры
    apt['views'] = apt.get('views', 0) + 1
    save_apartments(data)
    
    return render_template('apartment.html', apartment=apt)

# Форма добавления
@app.route('/add')
def add_form():
    return render_template('add.html')

# Сохранение объявления
@app.route('/api/apartments', methods=['POST'])
def save_apartment():
    data = load_apartments()
    new_id = str(uuid.uuid4())[:8]
    
    new_apt = {
        'id': new_id,
        'title': request.form.get('title', ''),
        'price': int(request.form.get('price', 0)),
        'rooms': int(request.form.get('rooms', 1)),
        'area': float(request.form.get('area', 0)),
        'district': request.form.get('district', ''),
        'metro': request.form.get('metro', ''),
        'address': request.form.get('address', ''),
        'description': request.form.get('description', ''),
        'owner_name': request.form.get('owner_name', ''),
        'owner_phone': request.form.get('owner_phone', ''),
        'owner_email': request.form.get('owner_email', ''),
        'is_ai_enabled': request.form.get('is_ai_enabled') == 'true',
        'is_premium': request.form.get('is_premium') == 'true',
        'photos': [],
        'amenities': request.form.getlist('amenities'),
        'views': 0,
        'created_at': datetime.now().isoformat(),
        'ai_strategies': request.form.getlist('ai_strategies')
    }
    
    data.append(new_apt)
    save_apartments(data)
    return redirect(f'/apartment/{new_id}')

# Страница настройки ИИ
@app.route('/apartment/<id>/ai')
def ai_config(id):
    data = load_apartments()
    apt = next((x for x in data if x['id'] == id), None)
    if not apt:
        return "Объявление не найдено", 404
    
    ai_settings = load_ai_settings().get(id, {
        'strategies': [],
        'auto_reviews': False,
        'auto_messages': False,
        'analytics_enabled': False,
        'max_price': apt.get('price', 0) * 1.3,
        'min_rent_days': 30,
        'priority': 'profit'
    })
    
    return render_template('ai_config.html', 
                         apartment=apt, 
                         ai_settings=ai_settings,
                         strategies_list=[
                             {'id': 'price_optimization', 'name': 'Оптимизация цены'},
                             {'id': 'auto_reviews', 'name': 'Работа с отзывами'},
                             {'id': 'auto_messages', 'name': 'Ответ на сообщения'},
                             {'id': 'analytics', 'name': 'Аналитика за месяц'}
                         ])

# Сохранение настроек ИИ
@app.route('/api/apartment/<id>/ai', methods=['POST'])
def save_ai_settings(id):
    ai_settings = load_ai_settings()
    
    ai_settings[id] = {
        'strategies': request.form.getlist('strategies'),
        'auto_reviews': request.form.get('auto_reviews') == 'true',
        'auto_messages': request.form.get('auto_messages') == 'true',
        'analytics_enabled': request.form.get('analytics_enabled') == 'true',
        'max_price': float(request.form.get('max_price', 0)),
        'min_rent_days': int(request.form.get('min_rent_days', 30)),
        'priority': request.form.get('priority', 'profit')
    }
    
    with open(AI_FILE, 'w') as f:
        json.dump(ai_settings, f, indent=2)
    
    # Обновляем объявление
    data = load_apartments()
    for apt in data:
        if apt['id'] == id:
            apt['is_ai_enabled'] = True
            apt['ai_strategies'] = ai_settings[id]['strategies']
            break
    
    save_apartments(data)
    return redirect(f'/apartment/{id}')

# API статистики
@app.route('/api/ai/stats')
def ai_stats():
    apartments = load_apartments()
    ai_settings = load_ai_settings()
    
    return jsonify({
        'total_apartments': len(apartments),
        'ai_enabled': len([a for a in apartments if a.get('is_ai_enabled', False)]),
        'ai_settings_count': len(ai_settings),
        'avg_price': sum(a.get('price', 0) for a in apartments) / max(len(apartments), 1)
    })

# API всех объявлений
@app.route('/api/apartments')
def api_apartments():
    return jsonify(load_apartments())

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
