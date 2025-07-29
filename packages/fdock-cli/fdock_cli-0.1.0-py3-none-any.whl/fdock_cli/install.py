import os
import shutil
from pathlib import Path

def get_bashrc_path():
    """Retourne le chemin du .bashrc de l'utilisateur."""
    home = str(Path.home())
    return os.path.join(home, ".bashrc")

def get_scripts_dir():
    """Retourne le chemin du dossier des scripts dans le package."""
    return os.path.join(os.path.dirname(__file__), "scripts")

def install_scripts():
    """Installe les scripts dans ~/.fdock et configure le .bashrc."""
    # Créer le dossier .fdock dans home
    home = str(Path.home())
    fdock_dir = os.path.join(home, ".fdock")
    os.makedirs(fdock_dir, exist_ok=True)
    
    # Copier les scripts
    scripts_dir = get_scripts_dir()
    for script in os.listdir(scripts_dir):
        if script.endswith('.sh'):
            src = os.path.join(scripts_dir, script)
            dst = os.path.join(fdock_dir, script)
            shutil.copy2(src, dst)
            # Rendre le script exécutable
            os.chmod(dst, 0o755)
    
    # Configurer le .bashrc
    bashrc_path = get_bashrc_path()
    fdock_source = f"\n# fdock-cli configuration\nfor script in ~/.fdock/*.sh; do\n    source \"$script\"\ndone\n"
    
    # Vérifier si la configuration existe déjà
    if os.path.exists(bashrc_path):
        with open(bashrc_path, 'r') as f:
            content = f.read()
        if "fdock-cli configuration" not in content:
            with open(bashrc_path, 'a') as f:
                f.write(fdock_source)
    else:
        with open(bashrc_path, 'w') as f:
            f.write(fdock_source)

def main():
    """Point d'entrée principal."""
    try:
        install_scripts()
        print("✨ Installation réussie ! Pour activer fdock-cli :")
        print("1. Redémarrez votre terminal, ou")
        print("2. Exécutez : source ~/.bashrc")
    except Exception as e:
        print(f"❌ Erreur lors de l'installation : {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    main() 