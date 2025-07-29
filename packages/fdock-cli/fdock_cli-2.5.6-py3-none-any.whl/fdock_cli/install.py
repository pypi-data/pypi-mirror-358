import os
import shutil
from pathlib import Path

def convert_to_git_bash_path(windows_path):
    """Convertit un chemin Windows en chemin Git Bash."""
    # Enlève le C: et remplace les \ par /
    path = str(windows_path).replace('\\', '/')
    if ':' in path:
        drive, rest = path.split(':', 1)
        return f"/{drive.lower()}{rest}"
    return path

def install_scripts():
    """Installation des scripts dans le répertoire utilisateur."""
    # Création du répertoire .fdock dans le home
    home = str(Path.home())
    fdock_dir = os.path.join(home, '.fdock')
    os.makedirs(fdock_dir, exist_ok=True)

    # Copie des scripts
    scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    for script in os.listdir(scripts_dir):
        if script.endswith('.sh'):
            src = os.path.join(scripts_dir, script)
            dst = os.path.join(fdock_dir, script)
            shutil.copy2(src, dst)
            # Rendre le script exécutable
            os.chmod(dst, 0o755)

    # Ajout au .bashrc
    bashrc_path = os.path.join(home, '.bashrc')
    bash_profile_path = os.path.join(home, '.bash_profile')
    
    # Contenu à ajouter (avec chemin Git Bash) - SANS auto-exécution
    fdock_content = f"""
# fdock configuration
export FDOCK_HOME="{convert_to_git_bash_path(fdock_dir)}"
export PATH="$FDOCK_HOME:$PATH"
"""
    
    # Ajouter au .bashrc s'il existe
    if os.path.exists(bashrc_path):
        with open(bashrc_path, 'a') as f:
            f.write(fdock_content)
    
    # Ajouter au .bash_profile s'il existe
    if os.path.exists(bash_profile_path):
        with open(bash_profile_path, 'a') as f:
            f.write(fdock_content)
    
    print(f"✨ Scripts installés dans {fdock_dir}")
    print("🔄 Redémarrez votre terminal pour utiliser les commandes (fdock root, fdock hello, etc.)") 
