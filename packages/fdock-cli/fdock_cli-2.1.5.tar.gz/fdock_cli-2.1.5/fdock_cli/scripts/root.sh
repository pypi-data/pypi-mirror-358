#!/bin/bash

# 🎨 Quelques couleurs pour égayer notre terminal
VERT='\033[0;32m'
BLEU='\033[0;34m'
JAUNE='\033[1;33m'
ROUGE='\033[0;31m'
NC='\033[0m' # No Color

# 🧹 Fonction de nettoyage
function clean_root() {
    local PROJECT_NAME=$(basename $(pwd))
    echo -e "${JAUNE}🧹 Nettoyage du projet ${PROJECT_NAME} en cours...${NC}"
    
    # Liste des fichiers à supprimer
    files_to_remove=(
        ".rootsignal"
        ".gitignore"
        ".dockerignore"
        ".dockerfile"
        ".docker-compose.yml"
        "pyproject.toml"
        "README.md"
        ".env"
    )
    
    # Suppression des fichiers
    for file in "${files_to_remove[@]}"; do
        if [ -f "$file" ]; then
            rm "$file"
            echo -e "${ROUGE}   🗑️  Suppression de $file${NC}"
        fi
    done
    
    # Suppression des dossiers
    if [ -d "src" ]; then
        rm -rf src
        echo -e "${ROUGE}   🗑️  Suppression du dossier src/${NC}"
    fi
    
    if [ -d ".venv" ]; then
        echo -e "${JAUNE}⚠️  Le dossier .venv existe. Voulez-vous le supprimer aussi ? (o/n)${NC}"
        read -n 1 -r
        echo
        if [[ $REPLY =~ ^[Oo]$ ]]; then
            rm -rf .venv
            echo -e "${ROUGE}   🗑️  Suppression du dossier .venv/${NC}"
        fi
    fi
    
    echo -e "${VERT}✨ Nettoyage terminé !${NC}"
}

# 🎯 Notre super fonction root
function root() {
    local PROJECT_NAME=$(basename $(pwd))
    local PROJECT_PATH=$(pwd)
    local choix=$1  # Prendre le premier argument
    
    # Message d'accueil stylé
    echo -e "${VERT}
    🌈 Bienvenue dans le projet: ${JAUNE}${PROJECT_NAME}${VERT} !
    📂 Chemin: ${JAUNE}${PROJECT_PATH}${VERT}
    ===============================================${NC}"
    
    # Si pas d'argument, afficher le menu
    if [ -z "$choix" ]; then
        echo -e "${BLEU}Que souhaitez-vous faire ?${NC}
        
        1) Créer un environnement virtuel (.venv) et l'activer
        2) Créer un fichier .env
        3) Les deux ! (avec activation du .venv)
        4) Activer uniquement le .venv existant
        5) 🧹 Nettoyer le projet (supprimer les fichiers générés)
        6) Je suis juste de passage 🚶
        
        Votre choix (1-6) : "
        read -n 1 choix
        echo
    fi
    
    case $choix in
        1)
            python -m venv .venv
            source .venv/Scripts/activate
            echo -e "${VERT}✨ Environnement virtuel créé et activé !${NC}"
            ;;
        2)
            touch .env
            echo -e "${VERT}📝 Fichier .env créé !${NC}"
            ;;
        3)
            python -m venv .venv
            touch .env
            source .venv/Scripts/activate
            echo -e "${VERT}🎉 Environnement complet créé et .venv activé !${NC}"
            ;;
        4)
            if [ -d ".venv" ]; then
                source .venv/Scripts/activate
                echo -e "${VERT}🔌 Environnement virtuel activé !${NC}"
            else
                echo -e "${JAUNE}⚠️ Pas de .venv trouvé ! Voulez-vous le créer ? (o/n)${NC}"
                read -n 1 -r
                echo
                if [[ $REPLY =~ ^[Oo]$ ]]; then
                    python -m venv .venv
                    source .venv/Scripts/activate
                    echo -e "${VERT}✨ Environnement virtuel créé et activé !${NC}"
                fi
            fi
            ;;
        5)
            echo -e "${ROUGE}⚠️  Attention ! Cette action va supprimer tous les fichiers générés !${NC}"
            echo -e "${ROUGE}    Êtes-vous sûr de vouloir continuer ? (o/n)${NC}"
            read -n 1 -r
            echo
            if [[ $REPLY =~ ^[Oo]$ ]]; then
                clean_root
            else
                echo -e "${VERT}✨ Opération annulée !${NC}"
            fi
            return
            ;;
        6)
            echo -e "${JAUNE}🌟 À bientôt !${NC}"
            return
            ;;
        *)
            if [ -n "$choix" ]; then
                echo -e "${JAUNE}⚠️ Choix non valide : $choix${NC}"
            else
                echo -e "${JAUNE}⚠️ Aucun choix fait${NC}"
            fi
            return 1
            ;;
    esac

    # Création du marqueur magique et de la structure
    echo "🌟 ROOT_MARKER: ${PROJECT_NAME}" > .rootsignal
    mkdir -p src
    touch src/__init__.py
    
    # Création du README.md avec le nom du projet
    cat << EOF > README.md
# 🚀 ${PROJECT_NAME}

Projet créé avec root-cli.

## 📁 Structure du projet

\`\`\`
${PROJECT_NAME}/
├── src/
│   └── __init__.py
├── .gitignore
├── .dockerignore
├── .dockerfile
├── .docker-compose.yml
├── pyproject.toml
└── .env
\`\`\`
EOF

    touch pyproject.toml
    touch .dockerfile
    touch .docker-compose.yml
    touch .env

    # Création du .gitignore avec contenu par défaut
    cat << 'EOF' > .gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environnements virtuels
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Logs et bases de données
*.log
*.sqlite
*.db

# Dossiers de build
node_modules/
dist/
build/
EOF

    # Création du .dockerignore avec contenu par défaut
    cat << 'EOF' > .dockerignore
# Git
.git
.gitignore
.gitattributes

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/

# Environnements virtuels
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Docker
Dockerfile
docker-compose.yml
.docker

# Logs et données temporaires
*.log
.coverage
coverage.xml
htmlcov/
EOF

    echo -e "${VERT}📁 Structure du projet ${PROJECT_NAME} créée :${NC}"
    echo -e "${BLEU}   ├── src/${NC}"
    echo -e "${BLEU}   │   └── __init__.py${NC}"
    echo -e "${BLEU}   ├── .gitignore${NC}"
    echo -e "${BLEU}   ├── .dockerignore${NC}"
    echo -e "${BLEU}   ├── .dockerfile${NC}"
    echo -e "${BLEU}   ├── .docker-compose.yml${NC}"
    echo -e "${BLEU}   ├── pyproject.toml${NC}"
    echo -e "${BLEU}   ├── README.md${NC}"
    echo -e "${BLEU}   └── .env${NC}"
    
    # Petit message de fin
    if [ -f .rootsignal ]; then
        echo -e "${VERT}🎯 Marqueur root créé avec succès pour ${PROJECT_NAME} !${NC}"
    fi
}

# Script principal - seulement si exécuté directement
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    root "$@"
fi 