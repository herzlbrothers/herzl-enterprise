from flask import Flask, render_template, request, redirect, url_for, session
from flask import Flask, render_template, request, redirect, url_for, session
import json, os
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key ="herzlblogsupersecret123"

# 🔧 Kommentarhandling
def handle_comments(page_key, user_input=None, user_name=None):
    file_path = 'data/comments.json'
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({}, f)

    with open(file_path, 'r') as f:
        data = json.load(f)

    if user_input and user_name:
        comment = {
            "user": user_name,
            "text": user_input,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        data.setdefault(page_key, []).append(comment)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    return data.get(page_key, [])


# 🔹 ALLE BLOGEINTRÄGE
@app.route('/blog', methods=['GET', 'POST'])
def blog():
    with open('data/blog.json') as f:
        blogs = json.load(f)

    kategorien = ["KI", "Politik", "Business", "Lifestyle", "Strategie"]
    ausgewählt = request.args.get("kategorie", "")

    # Kommentare speichern
    if request.method == 'POST' and 'user' in session:
        beitrag_id = request.form['beitrag_id']
        text = request.form['comment']
        user = session['user']
        handle_comments(beitrag_id, text, user)

    return render_template("blog_all.html",
        blogs=blogs,
        kategorien=kategorien,
        ausgewählt=ausgewählt,
        get_comments=handle_comments
    )



# 🔹 EINZELNER BLOGEINTRAG + KOMMENTARE
@app.route('/blog/eintrag/<eintrag_id>', methods=['GET', 'POST'])
def blog_eintrag(eintrag_id):
    with open('data/blog.json') as f:
        blogs = json.load(f)

    beitrag = None
    for autor in blogs.values():
        for post in autor:
            if post['id'] == eintrag_id:
                beitrag = post
                break

    if not beitrag:
        return "Beitrag nicht gefunden", 404

    if request.method == 'POST' and 'user' in session:
        comment = request.form['comment']
        user = session['user']
        handle_comments(eintrag_id, comment, user)
        return redirect(url_for('blog_eintrag', eintrag_id=eintrag_id))

    comments = handle_comments(eintrag_id)
    return render_template('blog_eintrag.html', beitrag=beitrag, comments=comments)

# 🔹 NEUEN BEITRAG SPEICHERN
@app.route('/neuer_blog', methods=['GET', 'POST'])
def neuer_blog():
    if session.get('user') not in ['simon', 'christoph']:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        kategorie = request.form['kategorie']
        author = session['user']
        new_entry = {
            "id": f"{author}_{int(datetime.now().timestamp())}",
            "title": title,
            "content": content,
            "kategorie": kategorie
        }

        with open('data/blog.json') as f:
            blogs = json.load(f)

        blogs.setdefault(author, []).append(new_entry)

        with open('data/blog.json', 'w') as f:
            json.dump(blogs, f, indent=2)

        return redirect(url_for('blog'))

    return render_template('neuer_blog.html')

@app.route('/neuer_artikel', methods=['GET', 'POST'])
def neuer_artikel():
    if session.get('user') not in ['simon', 'christoph']:
        return redirect(url_for('login'))

    kategorien = ["KI", "Politik", "Business", "Lifestyle", "Strategie"]

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        kategorie = request.form['kategorie']
        draft = request.form.get('draft') == 'on'
        author = session['user']

        new_entry = {
            "id": f"{author}_{int(datetime.now().timestamp())}",
            "title": title,
            "content": content,
            "kategorie": kategorie,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "draft": draft
        }

        try:
            with open('data/artikel.json') as f:
                artikel_daten = json.load(f)
        except:
            artikel_daten = {}

        artikel_daten.setdefault(author, []).insert(0, new_entry)

        with open('data/artikel.json', 'w') as f:
            json.dump(artikel_daten, f, indent=2)

        return redirect(url_for('artikel'))

    return render_template('neuer_artikel.html', kategorien=kategorien)




# 🔹 ARTIKEL mit KOMMENTAREN
@app.route('/artikel_kommentar', methods=['GET', 'POST'])
def artikel_kommentar():
    page_key = "artikel_news"
    comments = []

    if request.method == 'POST' and 'user' in session:
        user_input = request.form['comment']
        user_name = session['user']
        handle_comments(page_key, user_input, user_name)
        return redirect(url_for('artikel'))

    comments = handle_comments(page_key)
    return render_template('article.html', comments=comments)

# 🔹 CHATBOT
@app.route('/chat')
def chat():
    return render_template('chatbot.html')

# 🔹 LOGIN / LOGOUT / ADMIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if (user == 'simon' and pw == 'geheim') or (user == 'christoph' and pw == 'geheim'):
            session['user'] = user
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/admin')
def admin():
    if 'user' in session:
        return render_template('admin.html', user=session['user'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/')
def home():
    # Artikel laden
    with open('data/artikel.json') as f:
        artikel_data = json.load(f)

    # Blog laden
    with open('data/blog.json') as f:
        blog_data = json.load(f)

    # Timeline laden
    with open('data/timeline.json') as f:
        timeline_data = json.load(f)

    # Daten rausholen
    simon_timeline = timeline_data.get("simon", [])
    christoph_timeline = timeline_data.get("christoph", [])

    simon_blogs = blog_data.get("simon", [])
    christoph_blogs = blog_data.get("christoph", [])

    simon_artikel = artikel_data.get("simon", [])
    christoph_artikel = artikel_data.get("christoph", [])

    blog_teaser = simon_blogs[-1] if simon_blogs else None
    artikel_teaser = simon_artikel[-1] if simon_artikel else None

    return render_template('home.html',
                           simon_timeline=simon_timeline,
                           christoph_timeline=christoph_timeline,
                           blog_teaser=blog_teaser,
                           artikel_teaser=artikel_teaser)


@app.route('/newsletter', methods=['POST'])
def newsletter():
    name = request.form.get('name') or "Kein Name angegeben"
    email = request.form.get('email')

    # Basis-Validierung (E-Mail muss "@" enthalten)
    if not email or '@' not in email:
        session['newsletter_status'] = 'error'
        return redirect(url_for('home'))

    file_path = 'data/newsletter.json'

    try:
        with open(file_path, 'r') as f:
            daten = json.load(f)
            if not isinstance(daten, list):
                daten = []
    except:
        daten = []

    if not any(entry.get("email") == email for entry in daten):
        daten.append({"name": name, "email": email})
        with open(file_path, 'w') as f:
            json.dump(daten, f, indent=2)

    session['newsletter_status'] = 'success'
    return redirect(url_for('home'))


@app.route('/artikel', methods=['GET', 'POST'])
def artikel():
    with open('data/artikel.json') as f:
        artikel_roh = json.load(f)

    highlight_id = request.args.get("highlight", None)
    highlight_artikel = None
    artikel_liste = []

    for autor in artikel_roh:
        for beitrag in artikel_roh[autor]:
            if not beitrag.get("draft", False):
                if beitrag["id"] == highlight_id:
                    highlight_artikel = beitrag
                else:
                    artikel_liste.append(beitrag)

    artikel_liste = sorted(artikel_liste, key=lambda x: x['timestamp'], reverse=True)

    kategorien = ["KI", "Politik", "Business", "Lifestyle", "Strategie"]
    ausgewählt = request.args.get("kategorie", "")

    if request.method == 'POST' and 'user' in session:
        beitrag_id = request.form['beitrag_id']
        text = request.form['comment']
        user = session['user']
        handle_comments(beitrag_id, text, user)

    return render_template("article_list.html",
        artikel_liste=artikel_liste,
        highlight_artikel=highlight_artikel,
        kategorien=kategorien,
        ausgewählt=ausgewählt,
        get_comments=handle_comments
    )



@app.route('/artikel/<artikel_id>', methods=['GET', 'POST'])
def artikel_eintrag(artikel_id):
    with open('data/artikel.json') as f:
        artikel_daten = json.load(f)

    # Artikel suchen – durch alle Autoren iterieren
    artikel = None
    for autor in artikel_daten:
        for beitrag in artikel_daten[autor]:
            if beitrag["id"] == artikel_id:
                artikel = beitrag
                break
        if artikel:
            break

    if not artikel:
        return "Artikel nicht gefunden", 404

    # Kommentar hinzufügen
    if request.method == 'POST' and 'user' in session:
        comment = request.form['comment']
        user = session['user']
        handle_comments(artikel_id, comment, user)
        return redirect(url_for('artikel_eintrag', artikel_id=artikel_id))

    comments = handle_comments(artikel_id)
    return render_template('artikel_eintrag.html', artikel=artikel, comments=comments)



@app.route('/timeline')
def timeline():
    with open('data/timeline.json') as f:
        events = json.load(f)
    # Events nach Datum sortieren (neueste oben)
    events = sorted(events, key=lambda x: x['date'], reverse=True)
    return render_template('timeline.html', events=events)

@app.route('/antwort', methods=['POST'])
def antwort():
    if 'user' not in session:
        return redirect(url_for('login'))

    beitrag_id = request.form['beitrag_id']
    kommentar_index = int(request.form['kommentar_index'])
    antwort_text = request.form['antwort']
    antwort_user = session['user']

    with open('data/comments.json') as f:
        data = json.load(f)

    antwort = {
        "user": antwort_user,
        "text": antwort_text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    if beitrag_id in data:
        try:
            data[beitrag_id][kommentar_index].setdefault("replies", []).append(antwort)
        except IndexError:
            pass

    with open('data/comments.json', 'w') as f:
        json.dump(data, f, indent=2)

    return redirect(request.referrer)


if __name__ == '__main__':
    app.run(debug=True)
