import streamlit as st
import pandas as pd

# Настройка страницы
st.set_page_config(
    page_title="Калькулятор БЖУ v2.0",
    page_icon="🧁",
    layout="wide"
)

# Заголовок
st.title("🧁 Калькулятор пищевой ценности v2.0")
st.markdown("### Расчет БЖУ, калорийности, стоимости и состава")

# Загрузка данных об ингредиентах
@st.cache_data
def load_ingredients():
    """Загружает базу данных ингредиентов из CSV файла"""
    df = pd.read_csv('ingredients_v2.csv', encoding='utf-8')
    return df

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

# Инициализация данных
try:
    ingredients_db = load_ingredients()
    st.success(f"✅ Загружено {len(ingredients_db)} ингредиентов")
except FileNotFoundError:
    st.error("❌ Файл ingredients_v2.csv не найден. Загрузите файл с ингредиентами.")
    st.stop()

# Инициализация состояния сессии для рецепта
if 'recipe' not in st.session_state:
    st.session_state.recipe = []

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
            composition_list.append(f"{item['name']}")
        
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
        
        if all_allergens:
            st.warning("**Содержит аллергены:**")
            for allergen in sorted(all_allergens):
                st.markdown(f"- {allergen}")
        else:
            st.success("✅ Аллергены не обнаружены")
        
        st.divider()
        
        # Кнопка очистки рецепта
        if st.button("🗑️ Очистить весь рецепт", type="secondary"):
            st.session_state.recipe = []
            st.rerun()
            
    else:
        st.info("📋 Рецепт пуст. Добавьте ингредиенты слева.")

# Футер
st.markdown("---")
st.markdown("*Расчет пищевой ценности v2.0*")
st.markdown("*Новое: расчет стоимости, состав по ТР ТС, маркировка аллергенов*")
