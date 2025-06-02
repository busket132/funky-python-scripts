import cv2
import numpy as np
from EZTkinter import *
import pyautogui
import os
import time

def start_search():
    global max_matches
    try:
        threshold = float(threshold_entry.get())
        max_matches = max_matches_entry.get()
        
        if threshold < 0 or threshold > 1:
            results_text.config(state='normal')
            results_text.delete(0, 'end')
            results_text.insert(0, "Порог должен быть от 0 до 1")
            results_text.config(state='readonly')
            return
            
        matches, screenshot = find_templates_on_screen(
            threshold=threshold, 
            max_matches_per_template=max_matches,
            template_filter=filter_entry.get().strip() if filter_entry.get().strip() else None,
            exclude_filter=exclude_entry.get().strip() if exclude_entry.get().strip() else None
        )
        
        if matches and save_template_var.var.get():
            # Создаем папку для новых шаблонов
            new_templates_dir = 'new_templates'
            if not os.path.exists(new_templates_dir):
                os.makedirs(new_templates_dir)
            
            # Сохраняем найденные изображения как новые шаблоны
            for i, match in enumerate(matches):
                pt = match['position']
                w, h = match['size']
                template_name = match['template']
                
                # Вырезаем найденное изображение
                crop = screenshot[pt[1]:pt[1]+h, pt[0]:pt[0]+w]
                new_template_name = f"new_template_{int(time.time())}_{i}.png"
                template_path = os.path.join(new_templates_dir, new_template_name)
                cv2.imwrite(template_path, crop)
        
        if matches:
            # Рисуем прямоугольники и сохраняем результат
            output_path = draw_rectangles(matches, screenshot)
            
            # Создаем статистику по шаблонам
            template_stats = {}
            for match in matches:
                template = match['template']
                template_stats[template] = template_stats.get(template, 0) + 1
            
            # Формируем строку результата
            stats_str = ", ".join([f"{template}: {count}" for template, count in template_stats.items()])
            result_str = f"Найдено совпадений: {len(matches)} ({stats_str})"
            
            results_text.config(state='normal')
            results_text.delete(0, 'end')
            results_text.insert(0, result_str)
            results_text.config(state='readonly')
        else:
            results_text.config(state='normal')
            results_text.delete(0, 'end')
            results_text.insert(0, "Совпадений не найдено")
            results_text.config(state='readonly')
            
    except Exception as e:
        results_text.config(state='normal')
        results_text.delete(0, 'end')
        results_text.insert(0, f"Ошибка: {str(e)}")
        results_text.config(state='readonly')

def find_templates_on_screen(templates_dir='templates', threshold=0.8, max_matches_per_template=10, template_filter=None, exclude_filter=None):
    try:
        # Делаем скриншот экрана
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Преобрзуем max_matches в обычное число, если это IntVar
        if hasattr(max_matches_per_template, 'get'):
            max_matches_per_template = int(max_matches_per_template.get())
        
        matches = []
        
        # Проверяем существование папки с шаблонами
        if not os.path.exists(templates_dir):
            raise FileNotFoundError(f"Папка {templates_dir} не найдена")
        
        # Получаем списки фильтров
        include_filters = [f.strip().lower() for f in template_filter.split(',')] if template_filter else []
        exclude_filters = [f.strip().lower() for f in exclude_filter.split(',')] if exclude_filter else []
        
        template_files = os.listdir(templates_dir)
        
        # Применяем фильтры
        filtered_templates = []
        for template_file in template_files:
            template_lower = template_file.lower()
            
            # Пропускаем файл если он содержит исключаемые слова
            if any(ex_filter in template_lower for ex_filter in exclude_filters):
                continue
                
            # Проверяем включающие фильтры
            if include_filters:
                if any(in_filter in template_lower for in_filter in include_filters):
                    filtered_templates.append(template_file)
            else:
                filtered_templates.append(template_file)
        
        # Используем отфильтрованный список
        for template_file in filtered_templates:
            if template_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    template_path = os.path.join(templates_dir, template_file)
                    template = cv2.imread(template_path)
                    
                    if template is None:
                        continue
                    
                    # Получаем размеры и преобразуем их в обычные числа, если это IntVar
                    h = template.shape[0] #if hasattr(template.shape[0], 'get') else template.shape[0]
                    w = template.shape[1] #if hasattr(template.shape[1], 'get') else template.shape[1]
                    screen_h = screenshot.shape[0] #if hasattr(screenshot.shape[0], 'get') else screenshot.shape[0]
                    screen_w = screenshot.shape[1] #if hasattr(screenshot.shape[1], 'get') else screenshot.shape[1]
                    
                    print(h, w, screen_h, screen_w)

                    if h > screen_h or w > screen_w:
                        continue
                    
                    # Ищем совпадения
                    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                    
                    print(max_matches_per_template)

                    # Находим локальные максимумы
                    template_matches = []
                    while len(template_matches) < int(max_matches_per_template):
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                        if max_val >= threshold:
                            # Проверяем, нет ли уже похожих совпадений рядом
                            is_duplicate = False
                            for existing_match in template_matches:
                                ex_x, ex_y = existing_match['position']
                                new_x, new_y = max_loc
                                # Если расстояние между точками меньше половины размера шаблона
                                if (abs(ex_x - new_x) < w//2 and abs(ex_y - new_y) < h//2):
                                    is_duplicate = True
                                    break
                            
                            if not is_duplicate:
                                template_matches.append({
                                    'template': template_file,
                                    'position': max_loc,
                                    'similarity': float(max_val),
                                    'size': (w, h)
                                })
                            
                            # Маскируем область вокруг найденного совпадения
                            x, y = max_loc
                            result[max(0, y-h//2):min(result.shape[0], y+h//2+h),
                                  max(0, x-w//2):min(result.shape[1], x+w//2+w)] = -1
                        else:
                            break
                    
                    matches.extend(template_matches)
                    
                except Exception as e:
                    print(f"Ошибка при обработке шаблона {template_file}: {str(e)}")
                    continue
        
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches, screenshot
    except Exception as e:
        raise Exception(f"Ошибка при поиске шаблонов: {str(e)}")

def draw_rectangles(matches, screenshot):
    try:
        # Создаем папки для результатов
        output_dir = 'results'
        crops_dir = os.path.join(output_dir, 'crops')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if not os.path.exists(crops_dir):
            os.makedirs(crops_dir)
        
        # Копируем скриншот для рисования
        marked_image = screenshot.copy()
        
        # Словарь для хранения цветов шаблонов
        template_colors = {}
        
        timestamp = int(time.time())
        
        # Рисуем прямоугольники для каждого совпадения
        for i, match in enumerate(matches):
            try:
                pt = match['position']
                w, h = match['size']
                template_name = match['template']
                
                # Генерируем или получаем цвет для шаблона
                if template_name not in template_colors:
                    template_colors[template_name] = (
                        np.random.randint(0, 255),
                        np.random.randint(0, 255),
                        np.random.randint(0, 255)
                    )
                
                color = template_colors[template_name]
                
                # Проверяем координаты перед рисованием
                if (pt[0] >= 0 and pt[1] >= 0 and 
                    pt[0] + w <= marked_image.shape[1] and 
                    pt[1] + h <= marked_image.shape[0]):
                    
                    # Рисуем прямоугольник
                    cv2.rectangle(marked_image, pt, (pt[0] + w, pt[1] + h), color, 2)
                    
                    # Добавляем текст
                    text = f"{template_name}: {match['similarity']:.2%}"
                    text_pt = (pt[0], max(pt[1] - 10, 20))
                    cv2.putText(marked_image, text, text_pt,
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
                    # Вырезаем и сохраняем найденный объект
                    crop = screenshot[pt[1]:pt[1]+h, pt[0]:pt[0]+w]
                    crop_filename = f"match_{timestamp}_{i}_{template_name}_{match['similarity']:.2f}.png"
                    crop_path = os.path.join(crops_dir, crop_filename)
                    cv2.imwrite(crop_path, crop)
                    
            except Exception as e:
                print(f"Ошибка при отрисовке совпадения: {str(e)}")
                continue
        
        # Сохраняем общий результат
        output_path = os.path.join(output_dir, f"screen_match_{timestamp}.png")
        cv2.imwrite(output_path, marked_image)
        return output_path
    except Exception as e:
        raise Exception(f"Ошибка при отрисовке результатов: {str(e)}")

# Создаем элементы интерфейса
title_label = Add_Label("Поиск нескольких шаблонов на экране", 1)

threshold_label = Add_Label("Порог сходства (0.0 - 1.0):", 2)
threshold_entry = Add_Entry_DV("", "0.8", 1)

max_matches = int
max_matches_label = Add_Label("Максимум совпадений на шаблон:", 3)
max_matches_entry = Add_Entry_DV("", "5", 1)

save_template_var = Add_CheckButton("Сохранять новые шаблоны", 4)

result_label = Add_Label("Результаты поиска:", 5)
results_text = Add_Entry_DV("", "", 2)
results_text.config(state='readonly', width=50)

Add_Attributes("-topmost")

# Добавляем поля в интерфейс
filter_label = Add_Label("Фильтр шаблонов (через запятую):", 6)
filter_entry = Add_Entry_DV("", "", 3)

exclude_label = Add_Label("Исключить шаблоны (через запятую):", 7)
exclude_entry = Add_Entry_DV("", "", 4)

search_button = Add_Button("Начать поиск", 1)
search_button.config(command=start_search)

# Настройка окна
Resize_Enabler("true")
CreateWindow(600, 300, "Поиск шаблонов на экране")
