import os
import sys
import subprocess
from pathlib import Path

def get_script_path(script_name):
    """Retourne le chemin du script dans le package."""
    # Utiliser Path pour gérer les chemins de manière cross-platform
    script_path = Path(__file__).parent / "scripts" / f"{script_name}.sh"
    return str(script_path.resolve())

def list_commands():
    """Liste les commandes disponibles."""
    scripts_dir = Path(__file__).parent / "scripts"
    commands = []
    if scripts_dir.exists():
        for file in scripts_dir.glob("*.sh"):
            commands.append(file.stem)  # Enlève le .sh
    return sorted(commands)

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
        print(f"🔍 Recherché dans : {script_path}")
        print("💡 Utilisez 'fdock --help' pour voir les commandes disponibles")
        return 1

    try:
        # Vérifier que le script existe et est lisible
        if not os.access(script_path, os.R_OK):
            print(f"❌ Le script {script_path} n'est pas accessible en lecture")
            return 1

        # Afficher le chemin pour le debug
        print(f"📜 Exécution du script : {script_path}")
        
        # Exécute le script bash avec tous les arguments passés
        # Utiliser shell=True pour Windows
        if os.name == 'nt':  # Windows
            result = subprocess.run(
                f"bash {script_path} {' '.join(sys.argv[2:])}",
                shell=True,
                check=True
            )
        else:  # Unix
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