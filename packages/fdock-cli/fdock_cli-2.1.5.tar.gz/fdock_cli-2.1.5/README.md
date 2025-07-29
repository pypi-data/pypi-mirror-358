# 🚀 fdock_cli

Un outil CLI puissant pour initialiser et gérer vos projets Python avec style ! 

## 🎯 Fonctionnalités

- **Initialisation rapide** de projets Python avec structure complète
- **Gestion d'environnements virtuels** simplifiée
- **Interface interactive** avec menu coloré
- **Scripts bash intégrés** pour automatiser vos tâches

## 📦 Installation

```bash
pip install fdock_cli
```

## 🚀 Utilisation

Après installation, lancez l'installation des scripts :

```bash
python -m fdock_cli.install
```

Puis redémarrez votre terminal et utilisez :

```bash
# Initialiser un nouveau projet
fdock root

# Afficher les informations du projet
fdock hello
```

## 🎨 Fonctionnalités du menu

1. **Créer un environnement virtuel** (.venv) et l'activer
2. **Créer un fichier .env** pour vos variables d'environnement  
3. **Les deux !** (environnement + .env avec activation)
4. **Activer uniquement** le .venv existant
5. **🧹 Nettoyer le projet** (supprimer les fichiers générés)
6. **Je suis juste de passage** 🚶

## 📁 Structure générée

```
votre-projet/
├── src/
│   └── __init__.py
├── .gitignore
├── .dockerignore  
├── .dockerfile
├── .docker-compose.yml
├── pyproject.toml
├── README.md
└── .env
```

## 🎯 Pourquoi fdock_cli ?

- **Rapide** : Initialisez un projet en quelques secondes
- **Complet** : Tous les fichiers essentiels générés automatiquement
- **Interactif** : Menu coloré et intuitif
- **Flexible** : Choisissez exactement ce dont vous avez besoin

## 🛠️ Développement

```bash
git clone https://github.com/votre-repo/fdock_cli
cd fdock_cli
pip install -e .
```

## 📄 Licence

MIT License - Utilisez librement !

---

**Créé avec ❤️ pour simplifier la vie des développeurs Python !** 