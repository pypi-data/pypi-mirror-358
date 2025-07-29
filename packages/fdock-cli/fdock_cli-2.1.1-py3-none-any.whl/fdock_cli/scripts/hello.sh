#!/bin/bash

# 🎨 Une fonction d'exemple
function hello() {
    local PROJECT_NAME=$(basename $(pwd))
    local PROJECT_PATH=$(pwd)
    
    echo "👋 Bonjour depuis le projet ${PROJECT_NAME} !"
    echo "📂 Chemin complet : ${PROJECT_PATH}"
    
    if [ -f ".rootsignal" ]; then
        echo "🎯 Ce projet est initialisé avec root-cli !"
    else
        echo "⚠️  Ce projet n'est pas encore initialisé avec root-cli"
        echo "💡 Tapez 'fdock root' pour l'initialiser"
    fi
}

# On exporte la fonction pour qu'elle soit disponible après le source
export -f hello

# On appelle aussi la fonction directement
hello 