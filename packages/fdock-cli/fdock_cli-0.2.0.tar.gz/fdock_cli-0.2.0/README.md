# 🚀 fdock-cli

Un ensemble d'outils en ligne de commande pour initialiser et gérer vos projets Python.

## ✨ Fonctionnalités

- 📁 Initialisation rapide de projets Python
- 🔧 Gestion automatisée des environnements virtuels
- 🎯 Création de structure de projet standardisée
- 🐳 Support Docker intégré

## 📥 Installation

```bash
pip install fdock-cli
```

C'est tout ! Pas besoin de configuration supplémentaire.

## 🎮 Utilisation

### Commande `fdock root`

Initialise un nouveau projet :
```bash
fdock root
```

Options disponibles :
1. Créer un environnement virtuel (.venv) et l'activer
2. Créer un fichier .env
3. Les deux ! (avec activation du .venv)
4. Activer uniquement le .venv existant
5. Nettoyer le projet
6. Quitter

### Commande `fdock hello`

Un exemple de commande simple :
```bash
fdock hello
```

### Aide

Pour voir toutes les commandes disponibles :
```bash
fdock --help
```

## 🔧 Structure créée par `fdock root`

```
projet/
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

## 🗑️ Désinstallation

Simple comme bonjour :
```bash
pip uninstall fdock-cli
```

## 📝 License

MIT License 