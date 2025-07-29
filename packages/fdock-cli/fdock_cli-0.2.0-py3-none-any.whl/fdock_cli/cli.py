import os
import sys
import subprocess
from pathlib import Path

def get_script_path(script_name):
    """Retourne le chemin du script dans le package."""
    return os.path.join(os.path.dirname(__file__), "scripts", f"{script_name}.sh")

def list_commands():
    """Liste les commandes disponibles."""
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    commands = []
    for file in os.listdir(scripts_dir):
        if file.endswith('.sh'):
            commands.append(file[:-3])  # Enlève le .sh
    return commands

def show_help():
    """Affiche l'aide."""
    commands = list_commands()
    print("🚀 fdock - Gestionnaire de projets Python")
    print("\nUtilisation:")
    print("  fdock <commande>")
    print("\nCommandes disponibles:")
    for cmd in commands:
        print(f"  • {cmd}")
    print("\nExemple:")
    print("  fdock root    # Initialise un nouveau projet")
    print("  fdock hello   # Affiche les informations du projet")

def main():
    """Point d'entrée principal."""
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        show_help()
        return 0

    command = sys.argv[1]
    script_path = get_script_path(command)
    
    if not os.path.exists(script_path):
        print(f"❌ Commande '{command}' introuvable")
        print("💡 Utilisez 'fdock --help' pour voir les commandes disponibles")
        return 1

    try:
        # Exécute le script bash avec tous les arguments passés
        result = subprocess.run(
            ["bash", script_path] + sys.argv[2:],
            check=True
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de la commande : {e}")
        return e.returncode
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 