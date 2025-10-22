from flask import Flask, render_template_string, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('flashcards.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS flashcards
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  question TEXT NOT NULL,
                  answer TEXT NOT NULL,
                  category TEXT)''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('flashcards.db')
    conn.row_factory = sqlite3.Row
    return conn

# HTML Templates
#BASE_TEMPLATE = '''
#'''

#HOME_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
#''')

#ADD_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
#''')

#MANAGE_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
#''')

#EDIT_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
#''')

# Routes
@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    
    # Get total cards and categories
    c.execute('SELECT COUNT(*) FROM flashcards')
    total = c.fetchone()[0]
    
    c.execute('SELECT COUNT(DISTINCT category) FROM flashcards WHERE category IS NOT NULL AND category != ""')
    categories = c.fetchone()[0]
    
    flashcard = None
    prev_id = None
    next_id = None
    
    if total > 0:
        card_id = request.args.get('id', type=int)
        random = request.args.get('random', type=int)
        
        if random:
            c.execute('SELECT * FROM flashcards ORDER BY RANDOM() LIMIT 1')
        elif card_id:
            c.execute('SELECT * FROM flashcards WHERE id = ?', (card_id,))
        else:
            c.execute('SELECT * FROM flashcards ORDER BY id LIMIT 1')
        
        flashcard = c.fetchone()
        
        if flashcard:
            # Get previous and next IDs
            c.execute('SELECT id FROM flashcards WHERE id < ? ORDER BY id DESC LIMIT 1', (flashcard['id'],))
            prev = c.fetchone()
            prev_id = prev['id'] if prev else flashcard['id']
            
            c.execute('SELECT id FROM flashcards WHERE id > ? ORDER BY id LIMIT 1', (flashcard['id'],))
            nxt = c.fetchone()
            next_id = nxt['id'] if nxt else flashcard['id']
    
    conn.close()
    
    return render_template("index.html", 
                                 flashcard=flashcard, 
                                 total=total,
                                 categories=categories,
                                 prev_id=prev_id,
                                 next_id=next_id)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        category = request.form.get('category', '').strip()
        
        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO flashcards (question, answer, category) VALUES (?, ?, ?)',
                 (question, answer, category if category else None))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    return render_template("add.html")

@app.route('/manage')
def manage():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM flashcards ORDER BY id DESC')
    flashcards = c.fetchall()
    conn.close()
    
    return render_template("manage.html", flashcards=flashcards)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    c = conn.cursor()
    
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        category = request.form.get('category', '').strip()
        
        c.execute('UPDATE flashcards SET question = ?, answer = ?, category = ? WHERE id = ?',
                 (question, answer, category if category else None, id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('manage'))
    
    c.execute('SELECT * FROM flashcards WHERE id = ?', (id,))
    flashcard = c.fetchone()
    conn.close()
    
    if not flashcard:
        return redirect(url_for('manage'))
    
    return render_template("edit.html", flashcard=flashcard)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM flashcards WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('manage'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)