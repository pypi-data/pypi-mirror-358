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
python -m fdock_cli.install
source ~/.bashrc  # ou redémarrez votre terminal
```

## 🎮 Utilisation

### Commande `root`

Initialise un nouveau projet :
```bash
root
```

Options disponibles :
1. Créer un environnement virtuel (.venv) et l'activer
2. Créer un fichier .env
3. Les deux ! (avec activation du .venv)
4. Activer uniquement le .venv existant
5. Nettoyer le projet
6. Quitter

### Commande `hello`

Un exemple de commande simple :
```bash
hello
```

## 🔧 Structure créée

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

## 📝 License

MIT License 