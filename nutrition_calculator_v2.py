import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# Настройка страницы
st.set_page_config(
    page_title="Калькулятор БЖУ v3.0",
    page_icon="🧁",
    layout="wide"
)

# Заголовок
st.title("🧁 Калькулятор пищевой ценности v3.0")
st.markdown("### Расчет БЖУ, калорийности, стоимости и состава")

# Загрузка данных об ингредиентах
@st.cache_data
def load_ingredients():
    """Загружает базу данных ингредиентов из CSV файла"""
    df = pd.read_csv('ingredients_v2.csv', encoding='utf-8')
    return df

# Сохранение ингредиентов
def save_ingredients(df):
    """Сохраняет обновленную базу ингредиентов"""
    df.to_csv('ingredients_v2.csv', index=False, encoding='utf-8')
    st.cache_data.clear()  # Очищаем кэш для перезагрузки данных

# Функция извлечения аллергенов из тега
def extract_allergens(tag):
    """Извлекает список аллергенов из тега согласно ТР ТС 022/2011"""
    if pd.isna(tag) or tag == '':
        return []
    
    allergens = []
    tag_lower = tag.lower()
    
    # Проверяем наличие маркера аллергена
    if '#аллерген' in tag_lower:
        # Извлекаем конкретные аллергены согласно ТР ТС 022/2011
        if 'лактоза' in tag_lower or 'молочн' in tag_lower:
            allergens.append('молоко и продукты его переработки (включая лактозу)')
        if 'глютен' in tag_lower or 'пшениц' in tag_lower:
            allergens.append('злаки, содержащие глютен (пшеница, рожь, ячмень, овес)')
        if 'яй' in tag_lower or 'яиц' in tag_lower:
            allergens.append('яйца и продукты их переработки')
        if 'орех' in tag_lower:
            allergens.append('орехи и продукты их переработки')
        if 'арахис' in tag_lower:
            allergens.append('арахис и продукты его переработки')
        if 'сое' in tag_lower or 'соев' in tag_lower or 'соя' in tag_lower:
            allergens.append('соя и продукты ее переработки')
    
    return allergens

# Функция сохранения рецепта
def save_recipe_to_file(recipe_name, recipe_data, calculations):
    """Сохраняет рецепт в JSON файл"""
    
    # Создаем папку для рецептов, если её нет
    os.makedirs('saved_recipes', exist_ok=True)
    
    # Формируем имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in recipe_name if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"saved_recipes/{safe_name}_{timestamp}.json"
    
    # Формируем данные для сохранения
    save_data = {
        'название_изделия': recipe_name,
        'дата_создания': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'рецепт': recipe_data,
        'расчеты': calculations
    }
    
    # Сохраняем в JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    return filename

# Инициализация данных
try:
    ingredients_db = load_ingredients()
    st.success(f"✅ Загружено {len(ingredients_db)} ингредиентов")
except FileNotFoundError:
    st.error("❌ Файл ingredients_v2.csv не найден. Загрузите файл с ингредиентами.")
    st.stop()

# Инициализация состояния сессии
if 'recipe' not in st.session_state:
    st.session_state.recipe = []
if 'show_new_ingredient_form' not in st.session_state:
    st.session_state.show_new_ingredient_form = False

# Боковая панель для управления
with st.sidebar:
    st.header("⚙️ Управление")
    
    if st.button("➕ Добавить новый ингредиент", use_container_width=True):
        st.session_state.show_new_ingredient_form = not st.session_state.show_new_ingredient_form
    
    st.divider()
    st.markdown(f"**Всего ингредиентов в базе:** {len(ingredients_db)}")
    st.markdown(f"**Ингредиентов в рецепте:** {len(st.session_state.recipe)}")

# ========== ФОРМА ДОБАВЛЕНИЯ НОВОГО ИНГРЕДИЕНТА ==========
if st.session_state.show_new_ingredient_form:
    st.header("➕ Добавление нового ингредиента")
    
    with st.form("new_ingredient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("* Название ингредиента", help="Обязательное поле")
            new_protein = st.number_input("* Белки (г на 100г)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, help="Обязательное поле")
            new_fat = st.number_input("* Жиры (г на 100г)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, help="Обязательное поле")
            new_carbs = st.number_input("* Углеводы (г на 100г)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, help="Обязательное поле")
            new_calories = st.number_input("* Калории (кКал на 100г)", min_value=0.0, max_value=900.0, value=0.0, step=1.0, help="Обязательное поле")
        
        with col2:
            new_fiber = st.number_input("* Клетчатка (г на 100г)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, help="Обязательное поле")
            new_lactose = st.number_input("* Лактоза (г на 100г)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, help="Обязательное поле")
            new_gluten = st.number_input("* Глютен (г на 100г)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, help="Обязательное поле")
            new_cost = st.number_input("* Стоимость (руб/кг)", min_value=0.0, value=0.0, step=1.0, help="Обязательное поле")
            new_tag = st.text_input("Тэг (необязательно)", help="Например: #аллерген, глютен")
        
        st.markdown("_* - обязательные поля_")
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submit_button = st.form_submit_button("💾 Сохранить ингредиент", type="primary", use_container_width=True)
        
        with col_cancel:
            cancel_button = st.form_submit_button("❌ Отмена", use_container_width=True)
        
        if cancel_button:
            st.session_state.show_new_ingredient_form = False
            st.rerun()
        
        if submit_button:
            # Валидация обязательных полей
            errors = []
            
            if not new_name or new_name.strip() == "":
                errors.append("Название ингредиента")
            
            # Проверяем, что хотя бы одно из значений БЖУ или калорий не равно нулю
            if new_protein == 0 and new_fat == 0 and new_carbs == 0 and new_calories == 0:
                errors.append("Хотя бы одно значение (Белки, Жиры, Углеводы или Калории) должно быть больше 0")
            
            if errors:
                st.error("❌ Ошибка! Не заполнены обязательные поля:")
                for error in errors:
                    st.markdown(f"- {error}")
            else:
                # Проверяем, нет ли уже такого ингредиента
                if new_name in ingredients_db['Ингредиент'].values:
                    st.warning(f"⚠️ Ингредиент '{new_name}' уже существует в базе!")
                else:
                    # Добавляем новый ингредиент
                    new_ingredient = pd.DataFrame([{
                        'Ингредиент': new_name.strip(),
                        'Белки, г': new_protein,
                        'Жиры, г': new_fat,
                        'Углеводы, г': new_carbs,
                        'Энергетическая ценность, кКал': new_calories,
                        'Клетчатка, г': new_fiber,
                        'Лактоза, г': new_lactose,
                        'Глютен, г': new_gluten,
                        'Стоимость, руб/кг': new_cost,
                        'Тэг': new_tag.strip()
                    }])
                    
                    # Добавляем в базу
                    ingredients_db_updated = pd.concat([ingredients_db, new_ingredient], ignore_index=True)
                    save_ingredients(ingredients_db_updated)
                    
                    st.success(f"✅ Ингредиент '{new_name}' успешно добавлен в базу!")
                    st.session_state.show_new_ingredient_form = False
                    st.rerun()
    
    st.divider()

# ========== ОСНОВНОЙ ИНТЕРФЕЙС ==========

# Название изделия
recipe_name = st.text_input("📝 Название изделия", placeholder="Например: Торт Наполеон", key="recipe_name_input")

# Разделение на две колонки
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Добавление ингредиентов")
    
    # Поиск ингредиента
    search_query = st.text_input(
        "Поиск ингредиента по названию:",
        placeholder="Введите название (например: мука, сахар, масло)"
    )
    
    # Фильтрация ингредиентов по поисковому запросу
    if search_query:
        filtered_ingredients = ingredients_db[
            ingredients_db['Ингредиент'].str.contains(search_query, case=False, na=False)
        ]
        
        if len(filtered_ingredients) > 0:
            st.write(f"Найдено ингредиентов: {len(filtered_ingredients)}")
            
            # Выбор ингредиента из найденных
            selected_ingredient = st.selectbox(
                "Выберите ингредиент:",
                options=filtered_ingredients['Ингредиент'].tolist(),
                key='ingredient_select'
            )
            
            # Ввод количества в граммах
            quantity = st.number_input(
                "Количество (в граммах):",
                min_value=0.0,
                value=100.0,
                step=10.0,
                key='quantity_input'
            )
            
            # Кнопка добавления
            if st.button("➕ Добавить в рецепт", type="primary"):
                # Проверка, не добавлен ли уже этот ингредиент
                existing = [item for item in st.session_state.recipe if item['name'] == selected_ingredient]
                
                if existing:
                    st.warning(f"⚠️ {selected_ingredient} уже добавлен в рецепт!")
                else:
                    # Получаем данные о выбранном ингредиенте
                    ingredient_data = ingredients_db[
                        ingredients_db['Ингредиент'] == selected_ingredient
                    ].iloc[0]
                    
                    # Добавляем в рецепт
                    st.session_state.recipe.append({
                        'name': selected_ingredient,
                        'quantity': quantity,
                        'protein': ingredient_data['Белки, г'],
                        'fat': ingredient_data['Жиры, г'],
                        'carbs': ingredient_data['Углеводы, г'],
                        'calories': ingredient_data['Энергетическая ценность, кКал'],
                        'cost': ingredient_data['Стоимость, руб/кг'],
                        'tag': ingredient_data['Тэг']
                    })
                    st.success(f"✅ Добавлено: {selected_ingredient} - {quantity}г")
                    st.rerun()
        else:
            st.info("🔍 Ничего не найдено. Попробуйте другой запрос.")
    else:
        st.info("👆 Начните вводить название ингредиента для поиска")

with col2:
    st.subheader("🍰 Текущий рецепт")
    
    if len(st.session_state.recipe) > 0:
        # Показываем список ингредиентов в рецепте
        for idx, item in enumerate(st.session_state.recipe):
            col_name, col_qty, col_delete = st.columns([3, 2, 1])
            
            with col_name:
                st.write(f"**{item['name']}**")
            
            with col_qty:
                st.write(f"{item['quantity']} г")
            
            with col_delete:
                if st.button("🗑️", key=f"delete_{idx}"):
                    st.session_state.recipe.pop(idx)
                    st.rerun()
        
        st.divider()
        
        # ========== РАСЧЕТЫ ==========
        
        # Общий вес рецепта
        total_weight = sum(item['quantity'] for item in st.session_state.recipe)
        
        # Расчет абсолютных значений БЖУ и калорий
        total_protein = sum(item['protein'] * item['quantity'] / 100 for item in st.session_state.recipe)
        total_fat = sum(item['fat'] * item['quantity'] / 100 for item in st.session_state.recipe)
        total_carbs = sum(item['carbs'] * item['quantity'] / 100 for item in st.session_state.recipe)
        total_calories = sum(item['calories'] * item['quantity'] / 100 for item in st.session_state.recipe)
        
        # Расчет стоимости
        total_cost = sum(item['cost'] * item['quantity'] / 1000 for item in st.session_state.recipe)
        cost_per_kg = (total_cost / total_weight) * 1000 if total_weight > 0 else 0
        
        # Пересчет на 100г готового продукта
        protein_per_100g = (total_protein / total_weight) * 100 if total_weight > 0 else 0
        fat_per_100g = (total_fat / total_weight) * 100 if total_weight > 0 else 0
        carbs_per_100g = (total_carbs / total_weight) * 100 if total_weight > 0 else 0
        calories_per_100g = (total_calories / total_weight) * 100 if total_weight > 0 else 0
        
        # ========== 1. ПИЩЕВАЯ ЦЕННОСТЬ И СТОИМОСТЬ ==========
        st.subheader("📊 Пищевая ценность и стоимость")
        
        st.markdown(f"**Общий вес рецепта:** {total_weight:.1f} г")
        st.markdown(f"**Стоимость рецепта:** {total_cost:.2f} руб")
        st.markdown(f"**💰 Стоимость на 1 кг:** {cost_per_kg:.2f} руб/кг")
        
        st.markdown("---")
        st.markdown("### На 100г готовой продукции:")
        
        # Метрики в красивом формате
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("Белки", f"{protein_per_100g:.2f} г")
        
        with metric_col2:
            st.metric("Жиры", f"{fat_per_100g:.2f} г")
        
        with metric_col3:
            st.metric("Углеводы", f"{carbs_per_100g:.2f} г")
        
        with metric_col4:
            st.metric("Калории", f"{calories_per_100g:.1f} кКал")
        
        st.divider()
        
        # ========== 2. СОСТАВ ПРОДУКТА (ТР ТС) ==========
        st.subheader("📋 Состав продукта (по ТР ТС 022/2011)")
        
        # Сортируем ингредиенты по количеству (по убыванию)
        sorted_recipe = sorted(st.session_state.recipe, key=lambda x: x['quantity'], reverse=True)
        
        # Формируем строку состава
        composition_list = []
        for item in sorted_recipe:
            # Рассчитываем процент от общего веса
            percentage = (item['quantity'] / total_weight) * 100
            composition_list.append(f"{item['name']} ({percentage:.1f}%)")
        
        composition_text = ", ".join(composition_list) + "."
        
        st.markdown("**Состав (в порядке убывания):**")
        st.info(composition_text)
        
        st.divider()
        
        # ========== 3. АЛЛЕРГЕНЫ ==========
        st.subheader("⚠️ Информация об аллергенах")
        
        # Собираем все уникальные аллергены
        all_allergens = set()
        for item in st.session_state.recipe:
            allergens = extract_allergens(item['tag'])
            all_allergens.update(allergens)
        
        allergens_text = ""
        if all_allergens:
            st.warning("**Содержит аллергены:**")
            for allergen in sorted(all_allergens):
                st.markdown(f"- {allergen}")
                allergens_text += f"- {allergen}\n"
        else:
            st.success("✅ Аллергены не обнаружены")
            allergens_text = "Аллергены не обнаружены"
        
        st.divider()
        
        # ========== КНОПКА СОХРАНЕНИЯ РЕЦЕПТА ==========
        col_save, col_clear = st.columns(2)
        
        with col_save:
            if st.button("💾 Сохранить рецепт", type="primary", use_container_width=True):
                if not recipe_name or recipe_name.strip() == "":
                    st.error("❌ Введите название изделия для сохранения!")
                else:
                    # Формируем данные рецепта
                    recipe_data = []
                    for item in sorted_recipe:
                        recipe_data.append({
                            'ингредиент': item['name'],
                            'количество_г': item['quantity']
                        })
                    
                    # Формируем расчеты
                    calculations = {
                        'общий_вес_г': total_weight,
                        'БЖУ_на_100г': {
                            'белки_г': round(protein_per_100g, 2),
                            'жиры_г': round(fat_per_100g, 2),
                            'углеводы_г': round(carbs_per_100g, 2),
                            'калории_кКал': round(calories_per_100g, 1)
                        },
                        'стоимость': {
                            'за_рецепт_руб': round(total_cost, 2),
                            'за_1кг_руб': round(cost_per_kg, 2)
                        },
                        'состав': composition_text,
                        'аллергены': allergens_text
                    }
                    
                    # Сохраняем
                    filename = save_recipe_to_file(recipe_name, recipe_data, calculations)
                    st.success(f"✅ Рецепт '{recipe_name}' успешно сохранен!")
                    st.info(f"📁 Файл: {filename}")
        
        with col_clear:
            if st.button("🗑️ Очистить рецепт", type="secondary", use_container_width=True):
                st.session_state.recipe = []
                st.rerun()
            
    else:
        st.info("📋 Рецепт пуст. Добавьте ингредиенты слева.")

# Футер
st.markdown("---")
st.markdown("*Кондитерская Прохорова - расчет пищевой ценности v3.0*")
st.markdown("*Новое: сохранение рецептов, добавление новых ингредиентов*")
