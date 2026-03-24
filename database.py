import sqlite3
import os
from flask import g

DATABASE = os.path.join('instance', 'magasin.db')

def get_db():
    from flask import current_app
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    os.makedirs('instance', exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            emoji TEXT DEFAULT '🛍️'
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prix REAL NOT NULL,
            prix_ancien REAL,
            description TEXT,
            categorie_id INTEGER REFERENCES categories(id),
            stock INTEGER DEFAULT 0,
            image TEXT DEFAULT 'default.jpg',
            badge TEXT DEFAULT '',
            actif INTEGER DEFAULT 1
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS commandes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            telephone TEXT NOT NULL,
            ville TEXT NOT NULL,
            adresse TEXT,
            note TEXT,
            total REAL NOT NULL,
            details TEXT,
            statut TEXT DEFAULT 'En attente',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed initial data
    existing = c.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
    if existing == 0:
        cats = [
            ('Vêtements Femme', '👗'),
            ('Vêtements Fille', '🎀'),
            ('Chaussures', '👠'),
            ('Cosmétiques', '💄'),
            ('Accessoires', '👜'),
        ]
        c.executemany('INSERT INTO categories (nom, emoji) VALUES (?,?)', cats)
        conn.commit()

        produits = [
            ('Robe Traditionnelle Comorienne', 4500, 5500, 'Belle robe traditionnelle en tissu léger, parfaite pour les cérémonies.', 1, 15, 'default.jpg', 'Nouveau'),
            ('Hijab Soie Premium', 1800, None, 'Hijab en soie douce, disponible en plusieurs couleurs.', 1, 30, 'default.jpg', ''),
            ('Jean Slim Femme', 2500, 3200, 'Jean slim confortable et tendance pour femme.', 1, 20, 'default.jpg', ''),
            ('Robe Fille Brodée', 2200, None, 'Adorable robe brodée pour fille, tailles 4-14 ans.', 2, 12, 'default.jpg', 'Nouveau'),
            ('Sandales Dorées', 3500, 4200, 'Sandales dorées élégantes pour toutes occasions.', 3, 8, 'default.jpg', 'Promo'),
            ('Baskets Fille Colorées', 2800, None, 'Baskets légères et colorées pour fille active.', 3, 10, 'default.jpg', ''),
            ('Crème Karité Naturelle', 1200, None, 'Crème karité 100% naturelle, hydratante et nourrissante.', 4, 25, 'default.jpg', ''),
            ('Parfum Oriental Oud', 5500, 6000, 'Parfum oriental à base d\'oud, longue tenue.', 4, 6, 'default.jpg', 'Promo'),
            ('Sac à Main Tressé', 3200, None, 'Sac à main tressé artisanal, fabriqué aux Comores.', 5, 9, 'default.jpg', 'Nouveau'),
            ('Collier Doré Fleuri', 1500, None, 'Collier doré avec motifs floraux, léger et élégant.', 5, 20, 'default.jpg', ''),
        ]
        c.executemany(
            'INSERT INTO produits (nom, prix, prix_ancien, description, categorie_id, stock, image, badge) VALUES (?,?,?,?,?,?,?,?)',
            produits
        )
        conn.commit()

    conn.close()

from flask import Flask
def register_db(app: Flask):
    app.teardown_appcontext(close_db)
