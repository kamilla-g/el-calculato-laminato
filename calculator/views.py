from django.shortcuts import render
import math
import json

def home(request):
    # Начальные значения
    initial_data = {
        'room_length': 5.4,
        'room_width': 4.0,
        'laminate_length': 1285,
        'laminate_width': 192,
        'laminate_price': 400,
        'panels_per_pack': 8,
        'direction': 'length',
        'wall_indent': 10,
        'row_shift': 300,
        'min_panel_length': 300,
        'min_row_width': 50,
    }
    
    if request.method == 'POST':
        return calculate_laminate(request)
    
    context = {**initial_data, 'calculation_done': False}
    return render(request, 'calculator/index.html', context)

def calculate_laminate(request):
    try:
        # Получаем данные из формы
        room_length = float(request.POST.get('room_length', 5.4))
        room_width = float(request.POST.get('room_width', 4.0))
        laminate_length = int(request.POST.get('laminate_length', 1285))
        laminate_width = int(request.POST.get('laminate_width', 192))
        laminate_price = float(request.POST.get('laminate_price', 400))
        panels_per_pack = int(request.POST.get('panels_per_pack', 8))
        direction = request.POST.get('direction', 'length')
        wall_indent = int(request.POST.get('wall_indent', 10))
        min_panel_length = int(request.POST.get('min_panel_length', 300))
        row_shift = int(request.POST.get('row_shift', 300))
        min_row_width = int(request.POST.get('min_row_width', 50))
        
        # Вызываем функцию расчета
        result = calculate_laminate_python(
            room_length, room_width, laminate_length, laminate_width,
            laminate_price, panels_per_pack, direction, wall_indent,
            min_panel_length, row_shift, min_row_width
        )
        
        context = {
            'calculation_done': True,
            'room_length': room_length,
            'room_width': room_width,
            'laminate_length': laminate_length,
            'laminate_width': laminate_width,
            'laminate_price': laminate_price,
            'panels_per_pack': panels_per_pack,
            'direction': direction,
            'wall_indent': wall_indent,
            'row_shift': row_shift,
            'min_panel_length': min_panel_length,
            'min_row_width': min_row_width,
            **result
        }
        return render(request, 'calculator/index.html', context)
        
    except Exception as e:
        error_context = {
            'calculation_done': False,
            'error': f"Calculation error: {str(e)}",
            'room_length': request.POST.get('room_length', 5.4),
            'room_width': request.POST.get('room_width', 4.0),
            'laminate_length': request.POST.get('laminate_length', 1285),
            'laminate_width': request.POST.get('laminate_width', 192),
            'laminate_price': request.POST.get('laminate_price', 400),
            'panels_per_pack': request.POST.get('panels_per_pack', 8),
            'direction': request.POST.get('direction', 'length'),
            'wall_indent': request.POST.get('wall_indent', 10),
            'row_shift': request.POST.get('row_shift', 300),
            'min_panel_length': request.POST.get('min_panel_length', 300),
            'min_row_width': request.POST.get('min_row_width', 50),
        }
        return render(request, 'calculator/index.html', error_context)

def calculate_laminate_python(room_length, room_width, laminate_length, laminate_width,
                            laminate_price, panels_per_pack, direction, wall_indent,
                            min_panel_length, row_shift, min_row_width):
    """
    Основная функция расчета
    """
    # Рассчитываем площадь комнаты
    room_area = room_length * room_width
    
    # Рассчитываем площадь одной панели
    panel_area = (laminate_length * laminate_width) / 1000000
    
    # Генерируем схему укладки и получаем реальное количество панелей
    layout_data = generate_layout_scheme_python(
        room_length, room_width, laminate_length, laminate_width, 
        wall_indent, min_panel_length, row_shift, direction, min_row_width
    )
    
    total_panels_used = layout_data['total_panels']
    cut_panels_count = layout_data['cut_panels']
    
    # Рассчитываем упаковки на основе реально использованных панелей
    total_packs = math.ceil(total_panels_used / panels_per_pack)
    
    # Рассчитываем стоимость
    total_cost = total_packs * (laminate_price * panel_area * panels_per_pack)
    
    # Рассчитываем отходы
    used_area = total_panels_used * panel_area
    waste_area = used_area - room_area
    waste_percentage = (waste_area / room_area * 100) if room_area > 0 else 0
    
    return {
        'total_area': round(room_area, 1),
        'total_packs': total_packs,
        'total_cost': round(total_cost, 2),
        'waste_percentage': round(waste_percentage, 1),
        'total_panels': total_panels_used,
        'total_segments': cut_panels_count,
        'layout_data_json': json.dumps(layout_data['layout']),
        'coverage_length': layout_data['coverage_length'],
        'coverage_width': layout_data['coverage_width'],
        'scale': layout_data['scale'],
    }

def generate_layout_scheme_python(room_length, room_width, laminate_length, laminate_width, 
                                wall_indent, min_panel_length, row_shift, direction, min_row_width):
    """
    Генерация схемы укладки
    """
    # Определяем ориентацию комнаты в зависимости от направления укладки
    if direction == 'length':
        room_length_mm = room_length * 1000
        room_width_mm = room_width * 1000
    else:
        # При укладке по ширине комната "переворачивается"
        room_length_mm = room_width * 1000
        room_width_mm = room_length * 1000
    
    # Вычитаем отступы от стен
    available_length = room_length_mm - 2 * wall_indent
    available_width = room_width_mm - 2 * wall_indent
    
    # УВЕЛИЧИВАЕМ МАСШТАБ ДЛЯ БОЛЬШЕЙ СХЕМЫ
    max_display_width = 700  # УВЕЛИЧИЛИ С 600 ДО 700
    max_display_height = 500  # УВЕЛИЧИЛИ С 400 ДО 500
    
    scale_x = max_display_width / room_length_mm
    scale_y = max_display_height / room_width_mm
    scale = min(scale_x, scale_y) * 0.9  # УВЕЛИЧИЛИ КОЭФФИЦИЕНТ С 0.8 ДО 0.9
    
    layout = []
    panel_counter = 1
    cut_panels_count = 0
    total_panels = 0
    
    # Рассчитываем количество рядов
    rows = math.ceil(available_width / laminate_width)
    
    # Укладка по длине комнаты
    for row in range(rows):
        row_panels = []
        
        # Определяем ширину ряда
        if row == rows - 1:
            # Последний ряд - используем оставшуюся ширину
            row_width = available_width - (rows - 1) * laminate_width
        else:
            row_width = laminate_width
        
        # Пропускаем ряд если его ширина меньше минимальной
        if row_width < min_row_width:
            continue
        
        # Определяем смещение для нечетных рядов
        start_offset = min(row_shift, laminate_length * 0.4) if (row > 0 and row % 2 == 1) else 0
        
        current_position = 0
        
        # Первая панель в ряду (со смещением если нужно)
        if start_offset > 0:
            panel_length = min(start_offset, available_length)
            if panel_length >= min_panel_length:
                row_panels.append({
                    'type': 'cut-length-panel',
                    'length': panel_length,
                    'width': row_width,
                    'number': panel_counter
                })
                panel_counter += 1
                total_panels += 1
                cut_panels_count += 1
                current_position += panel_length
        
        # Укладка полных панелей
        while current_position + laminate_length <= available_length:
            panel_type = 'cut-width-panel' if row_width != laminate_width else 'full-panel'
            row_panels.append({
                'type': panel_type,
                'length': laminate_length,
                'width': row_width,
                'number': panel_counter
            })
            panel_counter += 1
            total_panels += 1
            if panel_type != 'full-panel':
                cut_panels_count += 1
            current_position += laminate_length
        
        # Последняя панель в ряду
        remaining_length = available_length - current_position
        if remaining_length > 0:
            panel_length = min(remaining_length, laminate_length)
            panel_type = 'cut-width-panel' if row_width != laminate_width else 'cut-length-panel'
            row_panels.append({
                'type': panel_type,
                'length': panel_length,
                'width': row_width,
                'number': panel_counter
            })
            panel_counter += 1
            total_panels += 1
            cut_panels_count += 1
        
        layout.append(row_panels)
    
    return {
        'layout': layout,
        'total_panels': total_panels,
        'cut_panels': cut_panels_count,
        'coverage_length': room_length_mm,
        'coverage_width': room_width_mm,
        'scale': scale
    }