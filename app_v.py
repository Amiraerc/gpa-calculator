from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'gpa_history.json'

GRADE_SCALE = {
    'A': 4.0, 'A-': 3.67, 'B+': 3.33, 'B': 3.0, 'B-': 2.67,
    'C+': 2.33, 'C': 2.0, 'C-': 1.67, 'D+': 1.33, 'D': 1.0, 
    'FX': 0, 'F': 0
}

GRADE_INFO = {
    'A': '95-100% - Отлично',
    'A-': '90-94% - Очень хорошо',
    'B+': '85-89% - Хорошо+',
    'B': '80-84% - Хорошо',
    'B-': '75-79% - Хорошо-',
    'C+': '70-74% - Удовлетворительно+',
    'C': '65-69% - Удовлетворительно',
    'C-': '60-64% - Удовлетворительно-',
    'D+': '55-59% - Достаточно+',
    'D': '50-54% - Достаточно',
    'FX': '25-49% - Неудача (можно пересдать)',
    'F': '0-24% - Неудача (не сдано)'
}

def load_history():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

@app.route('/')
def home():
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPA Калькулятор</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #667eea; min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; }
        .header { background: #4361ee; color: white; padding: 30px; text-align: center; }
        .logo { font-size: 2em; margin-bottom: 10px; }
        .nav { display: flex; background: #f8f9fa; }
        .nav a { flex: 1; text-align: center; padding: 18px; text-decoration: none; color: #495057; font-weight: 500; }
        .nav a.active { background: white; color: #4361ee; border-bottom: 3px solid #4361ee; }
        .main { padding: 30px; display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        @media (max-width: 768px) { .main { grid-template-columns: 1fr; } }
        .card { background: #f8f9fa; padding: 25px; border-radius: 12px; border: 2px solid #dee2e6; }
        h2 { color: #1a1a2e; margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        .form-input { width: 100%; padding: 12px; border: 2px solid #dee2e6; border-radius: 8px; font-size: 1em; }
        .course-row { display: grid; grid-template-columns: 2fr 1fr 1.5fr auto; gap: 12px; margin-bottom: 12px; padding: 12px; background: white; border-radius: 8px; border: 1px solid #dee2e6; }
        .btn-remove { background: #f72585; color: white; border: none; width: 36px; height: 36px; border-radius: 6px; cursor: pointer; }
        .button-group { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 25px; }
        .btn { padding: 12px 24px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
        .btn-primary { background: #4361ee; color: white; }
        .btn-secondary { background: white; color: #4361ee; border: 2px solid #4361ee; }
        .btn-success { background: #4cc9f0; color: white; }
        .result-placeholder { text-align: center; padding: 30px; color: #6c757d; }
        .gpa-result { background: white; padding: 25px; border-radius: 12px; border: 3px solid; margin-bottom: 20px; text-align: center; }
        .gpa-value { font-size: 3em; font-weight: 700; margin: 10px 0; }
        .result-details { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6; }
        .grade-scale { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; margin-top: 12px; }
        .grade-item { background: white; padding: 10px; border-radius: 6px; border-left: 4px solid #4361ee; font-size: 0.9em; }
        .footer { text-align: center; padding: 20px; background: #1a1a2e; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">GPA Калькулятор</div>
            <p>Расчет среднего балла с сохранением истории</p>
        </div>
        
        <nav class="nav">
            <a href="/" class="active">Калькулятор</a>
            <a href="/history">История</a>
        </nav>
        
        <div class="main">
            <div class="card">
                <h2>Введите данные</h2>
                <div class="form-group">
                    <label>Название семестра:</label>
                    <input type="text" class="form-input" id="semester" placeholder="Например: Осень 2024" value="Мой семестр">
                </div>
                <div class="courses-container">
                    <h3>Курсы</h3>
                    <div id="courses-list">
                        <div class="course-row">
                            <input type="text" class="form-input" placeholder="Название" value="Математика">
                            <input type="number" class="form-input" placeholder="Кредиты" step="0.5" min="0.5" value="3">
                            <select class="form-input">'''
    
    for grade in GRADE_SCALE.keys():
        html += f'<option value="{grade}">{grade}</option>'
    
    html += '''                            </select>
                            <button class="btn-remove" onclick="removeCourse(this)">X</button>
                        </div>
                    </div>
                </div>
                <div class="button-group">
                    <button class="btn btn-primary" onclick="addCourse()">Добавить курс</button>
                    <button class="btn btn-success" onclick="calculateGPA()">Рассчитать GPA</button>
                    <button class="btn btn-secondary" onclick="resetForm()">Сбросить</button>
                </div>
            </div>
            
            <div class="card">
                <h2>Результаты</h2>
                <div id="results-container">
                    <div class="result-placeholder">
                        <p>Добавьте курсы и нажмите "Рассчитать GPA"</p>
                    </div>
                </div>
                <div style="margin-top: 25px;">
                    <h3>Система оценок</h3>
                    <div class="grade-scale">'''
    
    for grade, desc in GRADE_INFO.items():
        html += f'<div class="grade-item"><strong>{grade}</strong> ({GRADE_SCALE[grade]})<br><small>{desc}</small></div>'
    
    html += '''                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>GPA Calculator © 2024</p>
        </div>
    </div>
    
    <script>
        function addCourse() {
            const list = document.getElementById('courses-list');
            const div = document.createElement('div');
            div.className = 'course-row';
            div.innerHTML = `
                <input type="text" class="form-input" placeholder="Название" value="Новый курс">
                <input type="number" class="form-input" placeholder="Кредиты" step="0.5" min="0.5" value="3">
                <select class="form-input">'''
    
    for grade in GRADE_SCALE.keys():
        html += f'<option value="{grade}">{grade}</option>'
    
    html += '''                </select>
                <button class="btn-remove" onclick="removeCourse(this)">X</button>
            `;
            list.appendChild(div);
        }
        
        function removeCourse(btn) {
            const courses = document.querySelectorAll('.course-row');
            if (courses.length > 1) {
                btn.parentElement.remove();
            }
        }
        
        function resetForm() {
            if (confirm('Очистить все поля?')) {
                document.getElementById('courses-list').innerHTML = `
                    <div class="course-row">
                        <input type="text" class="form-input" placeholder="Название" value="Математика">
                        <input type="number" class="form-input" placeholder="Кредиты" step="0.5" min="0.5" value="3">
                        <select class="form-input">'''
    
    for grade in GRADE_SCALE.keys():
        html += f'<option value="{grade}">{grade}</option>'
    
    html += '''                        </select>
                        <button class="btn-remove" onclick="removeCourse(this)">X</button>
                    </div>
                `;
                document.getElementById('semester').value = 'Мой семестр';
                document.getElementById('results-container').innerHTML = `
                    <div class="result-placeholder">
                        <p>Добавьте курсы и нажмите "Рассчитать GPA"</p>
                    </div>
                `;
            }
        }
        
        async function calculateGPA() {
            const courses = [];
            const rows = document.querySelectorAll('.course-row');
            
            for (const row of rows) {
                const inputs = row.querySelectorAll('input, select');
                const name = inputs[0].value.trim();
                const credits = inputs[1].value;
                const grade = inputs[2].value;
                
                if (!name || !credits) {
                    alert('Заполните все поля');
                    return;
                }
                
                courses.push({
                    name: name,
                    credits: parseFloat(credits),
                    grade: grade
                });
            }
            
            if (courses.length === 0) {
                alert('Добавьте курсы');
                return;
            }
            
            const semester = document.getElementById('semester').value || 'Мой семестр';
            
            try {
                const response = await fetch('/calculate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({semester: semester, courses: courses})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const gpa = result.gpa;
                    let color = '#fbbf24';
                    if (gpa >= 3.5) color = '#4cc9f0';
                    else if (gpa >= 3.0) color = '#4ade80';
                    else if (gpa < 2.0) color = '#ef4444';
                    
                    document.getElementById('results-container').innerHTML = `
                        <div class="gpa-result" style="border-color: ${color}">
                            <h3>${semester}</h3>
                            <div class="gpa-value" style="color: ${color}">${gpa}</div>
                            <div class="result-details">
                                <div><small>Курсов:</small><br><strong>${courses.length}</strong></div>
                                <div><small>Кредиты:</small><br><strong>${result.total_credits}</strong></div>
                                <div><small>Баллы:</small><br><strong>${result.total_grade_points}</strong></div>
                                <div><small>Сохранено:</small><br>✓</div>
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 15px;">
                            <a href="/history" class="btn btn-primary" style="display: inline-block; padding: 10px 20px;">
                                Посмотреть историю
                            </a>
                        </div>
                    `;
                } else {
                    alert('Ошибка: ' + result.error);
                }
            } catch (error) {
                alert('Ошибка соединения');
            }
        }
    </script>
</body>
</html>'''
    return html

@app.route('/history')
def history():
    history_data = load_history()
    history_data.sort(key=lambda x: x['date'], reverse=True)
    
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>История GPA</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #667eea; min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; }
        .header { background: #4361ee; color: white; padding: 30px; text-align: center; }
        .logo { font-size: 2em; margin-bottom: 10px; }
        .nav { display: flex; background: #f8f9fa; }
        .nav a { flex: 1; text-align: center; padding: 18px; text-decoration: none; color: #495057; font-weight: 500; }
        .nav a.active { background: white; color: #4361ee; border-bottom: 3px solid #4361ee; }
        .main { padding: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin: 25px 0; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; border: 2px solid #dee2e6; text-align: center; }
        .stat-value { font-size: 1.8em; font-weight: 700; color: #4361ee; }
        .action-buttons { display: flex; gap: 15px; margin: 25px 0; }
        .btn { padding: 12px 24px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
        .btn-export { background: #10b981; color: white; }
        .btn-clear { background: #ef4444; color: white; }
        .history-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; margin-top: 25px; }
        .history-card { background: white; border: 2px solid #dee2e6; border-radius: 10px; overflow: hidden; }
        .card-header { background: #4361ee; color: white; padding: 15px; display: flex; justify-content: space-between; }
        .card-body { padding: 20px; }
        .gpa-display { text-align: center; margin-bottom: 15px; }
        .gpa-value { font-size: 2.2em; font-weight: 700; color: #4361ee; display: block; }
        .card-footer { padding: 15px; background: #f8f9fa; border-top: 1px solid #dee2e6; text-align: right; }
        .btn-delete { background: #ef4444; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 0.9em; }
        .empty { text-align: center; padding: 50px; color: #6c757d; }
        .footer { text-align: center; padding: 20px; background: #1a1a2e; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">История GPA</div>
            <p>Отслеживайте ваш прогресс</p>
        </div>
        
        <nav class="nav">
            <a href="/">Калькулятор</a>
            <a href="/history" class="active">История</a>
        </nav>
        
        <div class="main">'''
    
    if history_data:
        gpas = [entry['gpa'] for entry in history_data]
        credits = [entry['total_credits'] for entry in history_data]
        
        html += f'''
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{len(history_data)}</div>
                    <div>Всего расчетов</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{round(sum(gpas)/len(gpas), 2)}</div>
                    <div>Средний GPA</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{sum(credits)}</div>
                    <div>Всего кредитов</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{max(gpas) if gpas else 0}</div>
                    <div>Лучший GPA</div>
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-export" onclick="exportData()">Экспорт CSV</button>
                <button class="btn btn-clear" onclick="clearAll()">Очистить историю</button>
            </div>
            
            <div class="history-list">'''
        
        for entry in history_data:
            html += f'''
                <div class="history-card">
                    <div class="card-header">
                        <div>{entry["semester"]}</div>
                        <div>{entry["date"]}</div>
                    </div>
                    <div class="card-body">
                        <div class="gpa-display">
                            <span class="gpa-value">{entry["gpa"]}</span>
                            <span>GPA</span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                            <div><small>Кредиты:</small><br><strong>{entry["total_credits"]}</strong></div>
                            <div><small>Баллы:</small><br><strong>{entry["total_grade_points"]}</strong></div>
                        </div>
                        <div style="background: #f8f9fa; padding: 12px; border-radius: 8px;">
                            <strong>Курсы:</strong>
                            <ul style="margin-top: 8px; padding-left: 20px; font-size: 0.9em;">'''
            
            for course in entry['courses']:
                html += f'<li>{course["name"]}: {course["credits"]}кр. - {course["grade"]}</li>'
            
            html += f'''         </ul>
                        </div>
                    </div>
                    <div class="card-footer">
                        <a href="/delete/{entry['id']}" class="btn-delete" onclick="return confirm('Удалить?')">Удалить</a>
                    </div>
                </div>'''
        
        html += '''        </div>'''
    else:
        html += '''
            <div class="empty">
                <h2>История пуста</h2>
                <p>Сначала выполните расчет GPA</p>
                <a href="/" style="display: inline-block; margin-top: 20px; padding: 12px 30px; 
                   background: #4361ee; color: white; text-decoration: none; border-radius: 8px;">
                    Перейти к калькулятору
                </a>
            </div>'''
    
    html += '''
        </div>
        
        <div class="footer">
            <p>GPA Calculator © 2024</p>
        </div>
    </div>
    
    <script>
        async function exportData() {
            try {
                const response = await fetch('/export');
                const result = await response.json();
                
                const blob = new Blob([result.csv], {type: 'text/csv'});
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = result.filename;
                link.click();
                
            } catch (error) {
                alert('Ошибка экспорта');
            }
        }
        
        function clearAll() {
            if (confirm('Удалить всю историю?')) {
                window.location.href = '/clear';
            }
        }
    </script>
</body>
</html>'''
    return html

@app.route('/calculate', methods=['POST'])
def calculate_gpa():
    try:
        data = request.json
        courses = data.get('courses', [])
        semester = data.get('semester', 'Семестр 1')
        
        total_credits = 0
        total_grade_points = 0
        
        for course in courses:
            grade = course['grade']
            credits = float(course['credits'])
            
            if grade in GRADE_SCALE:
                grade_point = GRADE_SCALE[grade]
                total_credits += credits
                total_grade_points += grade_point * credits
        
        gpa = total_grade_points / total_credits if total_credits > 0 else 0
        
        history = load_history()
        
        history.append({
            'id': len(history) + 1,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'semester': semester,
            'courses': courses,
            'total_credits': total_credits,
            'total_grade_points': round(total_grade_points, 2),
            'gpa': round(gpa, 2)
        })
        
        save_history(history)
        
        return jsonify({
            'success': True,
            'gpa': round(gpa, 2),
            'total_credits': total_credits,
            'total_grade_points': round(total_grade_points, 2)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete/<int:entry_id>')
def delete_entry(entry_id):
    history = load_history()
    history = [entry for entry in history if entry['id'] != entry_id]
    
    for i, entry in enumerate(history, 1):
        entry['id'] = i
    
    save_history(history)
    return '<script>window.location.href = "/history";</script>'

@app.route('/export')
def export_history():
    history_data = load_history()
    
    csv_lines = ['Дата;Семестр;GPA;Кредиты;Баллы;Курсы']
    
    for entry in history_data:
        courses_str = ' | '.join([f"{c['name']}({c['credits']}кр.,{c['grade']})" for c in entry['courses']])
        csv_lines.append(f"{entry['date']};{entry['semester']};{entry['gpa']};{entry['total_credits']};{entry['total_grade_points']};{courses_str}")
    
    csv_content = '\n'.join(csv_lines)
    
    return jsonify({
        'csv': csv_content,
        'filename': f'gpa_history_{datetime.now().strftime("%Y%m%d")}.csv'
    })

@app.route('/clear')
def clear_history():
    save_history([])
    return '<script>window.location.href = "/history";</script>'

if __name__ == '__main__':
    app.run(debug=False, port=5000)
