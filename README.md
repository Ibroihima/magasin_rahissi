# 🛍️ Rahissi Shop – Boutique en ligne

Boutique e-commerce Flask pour **Magasin Rahissi**, Grand Marché de Mbeni, Grande Comore.

## 🚀 Lancement rapide

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Lancer le serveur
```bash
python app.py
```

Le site sera accessible sur : **http://localhost:5000**

### 3. Accès Admin
- URL : http://localhost:5000/admin/login
- Identifiant : `admin`
- Mot de passe : `rahissi2025`

> ⚠️ Changez le mot de passe dans `app.py` ligne `ADMIN_PASSWORD` avant la mise en production !

---

## 📁 Structure du projet

```
magasin_rahissi/
├── app.py                  # Application Flask principale
├── database.py             # Gestion SQLite
├── requirements.txt
├── templates/
│   ├── base.html           # Template de base (nav, footer)
│   ├── index.html          # Page d'accueil
│   ├── produits.html       # Catalogue produits
│   ├── produit.html        # Fiche produit détaillée
│   ├── panier.html         # Panier
│   ├── commander.html      # Formulaire de commande
│   └── admin/
│       ├── login.html      # Connexion admin
│       ├── base_admin.html # Layout admin
│       ├── dashboard.html  # Tableau de bord
│       ├── commandes.html  # Gestion commandes
│       ├── produits.html   # Gestion produits
│       └── categories.html # Gestion catégories
├── static/
│   ├── css/
│   │   ├── style.css       # Styles boutique
│   │   └── admin.css       # Styles admin
│   └── uploads/            # Photos produits (uploadées)
└── instance/
    └── magasin.db          # Base de données SQLite (créée auto)
```

---

## 🎨 Design
- Palette : **Teal profond + Or chaud + Crème**
- Police : Playfair Display + DM Sans
- Mobile-first, responsive
- Bouton WhatsApp flottant sur toutes les pages

## ⚙️ Fonctionnalités
- ✅ Catalogue produits avec catégories
- ✅ Fiche produit avec ajout au panier
- ✅ Panier géré en session (sans compte)
- ✅ Checkout (Nom, Prénom, Tél, Ville)
- ✅ Paiement à la livraison
- ✅ Bouton WhatsApp (+2693447012)
- ✅ Dashboard admin (stats, commandes, produits)
- ✅ Upload d'images produits
- ✅ Gestion des statuts de commande

## 📦 Hébergement
- **PythonAnywhere** (gratuit pour débuter)
- **VPS Ubuntu** avec gunicorn + nginx

### PythonAnywhere (recommandé)
1. Créer un compte sur pythonanywhere.com
2. Uploader le dossier via "Files"
3. Créer une web app Flask en pointant vers `app.py`
4. Configurer le dossier static

---

WhatsApp : +269 344 7012
Grand Marché de Mbeni, Grande Comore 🇰🇲
