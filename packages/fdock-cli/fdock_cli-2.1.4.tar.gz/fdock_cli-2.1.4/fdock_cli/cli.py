import os
import sys
from .install import install_scripts

def show_help():
    """Affiche l'aide."""
    print("🚀 fdock - Gestionnaire de projets Python")
    print("\nUtilisation:")
    print("  fdock <commande>")
    print("\nCommandes disponibles:")
    print("  • root    # Initialise un nouveau projet")
    print("  • hello   # Affiche les informations du projet")
    print("\nExemple:")
    print("  fdock root    # Initialise un nouveau projet")

def execute_script(script_name):
    """Exécute un script bash."""
    home = os.path.expanduser('~')
    fdock_dir = os.path.join(home, '.fdock')
    script_path = os.path.join(fdock_dir, f"{script_name}.sh")
    
    if not os.path.exists(script_path):
        print(f"❌ Script {script_name}.sh non trouvé dans {fdock_dir}")
        return 1
    
    # Exécuter le script bash directement
    os.system(f'bash "{script_path}"')
    return 0

def main():
    """Point d'entrée principal."""
    # Première exécution - installer les scripts
    home = os.path.expanduser('~')
    fdock_dir = os.path.join(home, '.fdock')
    
    if not os.path.exists(fdock_dir):
        print("🔧 Première exécution détectée - Installation des scripts...")
        try:
            install_scripts()
            print("🎉 Installation terminée ! Redémarrez votre terminal.")
            return 0
        except Exception as e:
            print(f"❌ Erreur lors de l'installation : {e}")
            return 1
    
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        show_help()
        return 0
    
    command = sys.argv[1]
    if command in ['root', 'hello']:
        return execute_script(command)
    else:
        print(f"❌ Commande inconnue : {command}")
        show_help()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 