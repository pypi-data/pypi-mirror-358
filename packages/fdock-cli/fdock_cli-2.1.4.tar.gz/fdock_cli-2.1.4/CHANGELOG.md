# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.3] - 2025-01-XX

### 🔧 Corrigé
- Suppression de l'auto-exécution des scripts au démarrage du terminal
- Correction du script `hello.sh` qui s'exécutait automatiquement
- Correction du script `root.sh` pour éviter l'exécution non désirée
- Amélioration de la gestion des scripts bash

### 🚀 Amélioré
- Migration vers `pyproject.toml` moderne (suppression de `setup.py`)
- Ajout d'un README.md complet et attractif
- Amélioration des métadonnées du package pour PyPI

## [2.1.2] - 2025-01-XX

### 🚀 Ajouté
- README.md complet avec documentation
- Migration vers pyproject.toml
- Métadonnées complètes pour PyPI

## [2.1.1] - 2025-01-XX

### 🔧 Corrigé
- Corrections mineures des scripts

## [2.1.0] - 2025-01-XX

### 🚀 Ajouté
- Commande `fdock root` pour initialiser les projets
- Commande `fdock hello` pour afficher les informations du projet
- Scripts bash intégrés pour la gestion d'environnements
- Interface interactive avec menu coloré
- Génération automatique de structure de projet
- Support pour environnements virtuels Python
- Création automatique de fichiers de configuration (.gitignore, .dockerignore, etc.)

### ✨ Fonctionnalités
- Menu interactif avec 6 options
- Création et activation d'environnements virtuels
- Gestion des fichiers .env
- Nettoyage de projet intégré
- Messages colorés et emojis pour une meilleure UX 