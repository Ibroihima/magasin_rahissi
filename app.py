from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import init_db, get_db
import os
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'rahissi-secret-key-2025-mbeni'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'rahissi2025'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

@app.context_processor
def cart_count():
    panier = session.get('panier', {})
    count = sum(item['quantite'] for item in panier.values())
    return {'panier_count': count}

# ──────────────────────────────────────────
# FRONT-OFFICE
# ──────────────────────────────────────────

@app.route('/')
def index():
    db = get_db()
    produits = db.execute(
        'SELECT p.*, c.nom as cat_nom FROM produits p LEFT JOIN categories c ON p.categorie_id = c.id WHERE p.actif=1 ORDER BY p.id DESC LIMIT 8'
    ).fetchall()
    categories = db.execute('SELECT * FROM categories').fetchall()
    return render_template('index.html', produits=produits, categories=categories)

@app.route('/produits')
def produits():
    db = get_db()
    categorie_id = request.args.get('categorie')
    recherche = request.args.get('q', '').strip()
    categories = db.execute('SELECT * FROM categories').fetchall()
    
    query = 'SELECT p.*, c.nom as cat_nom FROM produits p LEFT JOIN categories c ON p.categorie_id = c.id WHERE p.actif=1'
    params = []
    if categorie_id:
        query += ' AND p.categorie_id = ?'
        params.append(categorie_id)
    if recherche:
        query += ' AND p.nom LIKE ?'
        params.append(f'%{recherche}%')
    query += ' ORDER BY p.id DESC'
    
    produits = db.execute(query, params).fetchall()
    cat_active = db.execute('SELECT * FROM categories WHERE id=?', [categorie_id]).fetchone() if categorie_id else None
    return render_template('produits.html', produits=produits, categories=categories, cat_active=cat_active, recherche=recherche)

@app.route('/produit/<int:id>')
def produit_detail(id):
    db = get_db()
    produit = db.execute('SELECT p.*, c.nom as cat_nom FROM produits p LEFT JOIN categories c ON p.categorie_id = c.id WHERE p.id=?', [id]).fetchone()
    if not produit:
        flash('Produit introuvable.', 'error')
        return redirect(url_for('produits'))
    similaires = db.execute('SELECT * FROM produits WHERE categorie_id=? AND id!=? AND actif=1 LIMIT 4', [produit['categorie_id'], id]).fetchall()
    return render_template('produit.html', produit=produit, similaires=similaires)

@app.route('/ajouter-panier', methods=['POST'])
def ajouter_panier():
    produit_id = str(request.form.get('produit_id'))
    quantite = int(request.form.get('quantite', 1))
    taille = request.form.get('taille', '')
    
    db = get_db()
    produit = db.execute('SELECT * FROM produits WHERE id=? AND actif=1', [produit_id]).fetchone()
    if not produit:
        flash('Produit introuvable.', 'error')
        return redirect(url_for('index'))
    
    panier = session.get('panier', {})
    key = f"{produit_id}_{taille}"
    if key in panier:
        panier[key]['quantite'] += quantite
    else:
        panier[key] = {
            'id': produit_id,
            'nom': produit['nom'],
            'prix': produit['prix'],
            'image': produit['image'],
            'taille': taille,
            'quantite': quantite
        }
    session['panier'] = panier
    flash(f'"{produit["nom"]}" ajouté au panier !', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/panier')
def voir_panier():
    panier = session.get('panier', {})
    total = sum(item['prix'] * item['quantite'] for item in panier.values())
    return render_template('panier.html', panier=panier, total=total)

@app.route('/modifier-panier', methods=['POST'])
def modifier_panier():
    key = request.form.get('key')
    action = request.form.get('action')
    panier = session.get('panier', {})
    if key in panier:
        if action == 'supprimer':
            del panier[key]
        elif action == 'augmenter':
            panier[key]['quantite'] += 1
        elif action == 'diminuer':
            panier[key]['quantite'] = max(1, panier[key]['quantite'] - 1)
    session['panier'] = panier
    return redirect(url_for('voir_panier'))

@app.route('/commander', methods=['GET', 'POST'])
def commander():
    panier = session.get('panier', {})
    if not panier:
        flash('Votre panier est vide.', 'error')
        return redirect(url_for('voir_panier'))
    
    total = sum(item['prix'] * item['quantite'] for item in panier.values())
    
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        telephone = request.form.get('telephone', '').strip()
        ville = request.form.get('ville', '').strip()
        adresse = request.form.get('adresse', '').strip()
        note = request.form.get('note', '').strip()
        
        if not all([nom, prenom, telephone, ville]):
            flash('Veuillez remplir tous les champs obligatoires.', 'error')
            return render_template('commander.html', panier=panier, total=total)
        
        db = get_db()
        import json
        details = json.dumps([{
            'nom': v['nom'], 'prix': v['prix'],
            'quantite': v['quantite'], 'taille': v['taille']
        } for v in panier.values()], ensure_ascii=False)
        
        db.execute(
            'INSERT INTO commandes (nom, prenom, telephone, ville, adresse, note, total, details, statut) VALUES (?,?,?,?,?,?,?,?,?)',
            [nom, prenom, telephone, ville, adresse, note, total, details, 'En attente']
        )
        db.commit()
        session.pop('panier', None)
        flash('✅ Commande envoyée ! Nous vous contacterons très prochainement.', 'success')
        return redirect(url_for('index'))
    
    return render_template('commander.html', panier=panier, total=total)

# ──────────────────────────────────────────
# ADMIN
# ──────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Identifiants incorrects.', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    commandes = db.execute('SELECT * FROM commandes ORDER BY date DESC LIMIT 10').fetchall()
    stats = {
        'total_commandes': db.execute('SELECT COUNT(*) FROM commandes').fetchone()[0],
        'ca': db.execute("SELECT IFNULL(SUM(total),0) FROM commandes WHERE statut != 'Annulée'").fetchone()[0],
        'en_attente': db.execute("SELECT COUNT(*) FROM commandes WHERE statut='En attente'").fetchone()[0],
        'total_produits': db.execute('SELECT COUNT(*) FROM produits').fetchone()[0],
    }
    return render_template('admin/dashboard.html', commandes=commandes, stats=stats)

@app.route('/admin/commandes')
@admin_required
def admin_commandes():
    db = get_db()
    statut = request.args.get('statut', '')
    if statut:
        commandes = db.execute('SELECT * FROM commandes WHERE statut=? ORDER BY date DESC', [statut]).fetchall()
    else:
        commandes = db.execute('SELECT * FROM commandes ORDER BY date DESC').fetchall()
    return render_template('admin/commandes.html', commandes=commandes, statut_filtre=statut)

@app.route('/admin/commande/<int:id>/statut', methods=['POST'])
@admin_required
def changer_statut(id):
    nouveau_statut = request.form.get('statut')
    db = get_db()
    db.execute('UPDATE commandes SET statut=? WHERE id=?', [nouveau_statut, id])
    db.commit()
    flash('Statut mis à jour.', 'success')
    return redirect(url_for('admin_commandes'))

@app.route('/admin/commande/<int:id>/supprimer', methods=['POST'])
@admin_required
def admin_supprimer_commande(id):
    db = get_db()
    commande = db.execute('SELECT * FROM commandes WHERE id=?', [id]).fetchone()
    if not commande:
        flash('Commande introuvable.', 'error')
        return redirect(url_for('admin_commandes'))
    if commande['statut'] != 'Annulée':
        flash('Seules les commandes annulées peuvent être supprimées.', 'error')
        return redirect(url_for('admin_commandes'))
    db.execute('DELETE FROM commandes WHERE id=?', [id])
    db.commit()
    flash(f'Commande #{ id } supprimée définitivement.', 'success')
    return redirect(url_for('admin_commandes'))

@app.route('/admin/produits')
@admin_required
def admin_produits():
    db = get_db()
    produits = db.execute('SELECT p.*, c.nom as cat_nom FROM produits p LEFT JOIN categories c ON p.categorie_id = c.id ORDER BY p.id DESC').fetchall()
    categories = db.execute('SELECT * FROM categories').fetchall()
    return render_template('admin/produits.html', produits=produits, categories=categories)

@app.route('/admin/produit/ajouter', methods=['POST'])
@admin_required
def admin_ajouter_produit():
    nom = request.form.get('nom')
    prix = float(request.form.get('prix', 0))
    prix_ancien = request.form.get('prix_ancien') or None
    description = request.form.get('description', '')
    categorie_id = request.form.get('categorie_id')
    stock = int(request.form.get('stock', 0))
    badge = request.form.get('badge', '')
    
    image = 'default.jpg'
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = filename
    
    db = get_db()
    db.execute(
        'INSERT INTO produits (nom, prix, prix_ancien, description, categorie_id, stock, image, badge) VALUES (?,?,?,?,?,?,?,?)',
        [nom, prix, prix_ancien, description, categorie_id, stock, image, badge]
    )
    db.commit()
    flash(f'Produit "{nom}" ajouté avec succès.', 'success')
    return redirect(url_for('admin_produits'))

@app.route('/admin/produit/<int:id>/modifier', methods=['POST'])
@admin_required
def admin_modifier_produit(id):
    nom = request.form.get('nom')
    prix = float(request.form.get('prix', 0))
    prix_ancien = request.form.get('prix_ancien') or None
    description = request.form.get('description', '')
    categorie_id = request.form.get('categorie_id')
    stock = int(request.form.get('stock', 0))
    badge = request.form.get('badge', '')
    actif = 1 if request.form.get('actif') else 0
    
    db = get_db()
    produit = db.execute('SELECT * FROM produits WHERE id=?', [id]).fetchone()
    
    image = produit['image']
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = filename
    
    db.execute(
        'UPDATE produits SET nom=?, prix=?, prix_ancien=?, description=?, categorie_id=?, stock=?, image=?, badge=?, actif=? WHERE id=?',
        [nom, prix, prix_ancien, description, categorie_id, stock, image, badge, actif, id]
    )
    db.commit()
    flash(f'Produit modifié avec succès.', 'success')
    return redirect(url_for('admin_produits'))

@app.route('/admin/produit/<int:id>/supprimer', methods=['POST'])
@admin_required
def admin_supprimer_produit(id):
    db = get_db()
    db.execute('DELETE FROM produits WHERE id=?', [id])
    db.commit()
    flash('Produit supprimé.', 'success')
    return redirect(url_for('admin_produits'))

@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def admin_categories():
    db = get_db()
    if request.method == 'POST':
        nom = request.form.get('nom')
        emoji = request.form.get('emoji', '🛍️')
        db.execute('INSERT INTO categories (nom, emoji) VALUES (?,?)', [nom, emoji])
        db.commit()
        flash('Catégorie ajoutée.', 'success')
    categories = db.execute('SELECT c.*, COUNT(p.id) as nb_produits FROM categories c LEFT JOIN produits p ON c.id=p.categorie_id GROUP BY c.id').fetchall()
    return render_template('admin/categories.html', categories=categories)

import json

@app.template_filter('from_json')
def from_json_filter(value):
    try:
        return json.loads(value) if value else []
    except Exception:
        return []

@app.template_filter('urlencode')
def urlencode_filter(value):
    from urllib.parse import quote
    return quote(str(value))

@app.teardown_appcontext
def close_db_ctx(e=None):
    from database import close_db as _close
    _close(e)

if __name__ == '__main__':
    init_db()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)

#fin
