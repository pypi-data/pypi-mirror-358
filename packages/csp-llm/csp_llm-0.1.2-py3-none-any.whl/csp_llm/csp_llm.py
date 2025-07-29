#!/usr/bin/env python3
"""
Version simplifiée du lanceur app
Usage basique sans arguments compliqués
"""

import subprocess
import sys
from pathlib import Path


def find_app_py(app_file_name: str) -> Path:
    """Trouve app.py automatiquement dans src/"""

    possible_locations = [
        # Même package que le CLI
        Path(__file__).parent / app_file_name,
        # Dans src/ depuis la racine du projet
        Path(__file__).parent.parent.parent / "src" / app_file_name,
        # Répertoire courant
        Path.cwd() / "src" / app_file_name,
        Path.cwd() / app_file_name,
    ]

    for location in possible_locations:
        if location.exists():
            return location.resolve()  # Chemin absolu

    raise FileNotFoundError("app.py introuvable")


def main():
    """Lance l'application csp_llm avec une configuration basique."""
    import argparse

    parser = argparse.ArgumentParser(description="Lance l'application")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8501)

    args = parser.parse_args()

    # Configuration par défaut
    APP_FILE = find_app_py("main.py")
    print(f"Chemin absolu de app: {APP_FILE}")

    HOST = args.host  # ou "0.0.0.0" pour l'accès réseau
    PORT = args.port  # default

    print("🚀 Lancement de l'application...")

    # Vérifier que le fichier existe
    app_path = Path(APP_FILE)
    if not app_path.exists():
        print(f"❌ Erreur: {APP_FILE} introuvable")

        return 1

    count = 0
    total = 5
    are_packages_ok: list[bool] = [True] * total
    install_messages: list[str] = []
    try:
        import anthropic

        install_messages.append(f"✅ anthropic {anthropic.__version__} trouvé")
    except ImportError:
        install_messages.append("❌ anthropic n'est pas installé")
        are_packages_ok[count] = False
        count += 1

    try:
        import openai

        install_messages.append(f"✅ openai {openai.__version__} trouvé")
    except ImportError:
        install_messages.append("❌ openai n'est pas installé")
        are_packages_ok[count] = False
        count += 1

    try:
        import streamlit

        install_messages.append(f"✅ streamlit {streamlit.__version__} trouvé")
    except ImportError:
        install_messages.append("❌ openai n'est pas installé")
        are_packages_ok[count] = False
        count += 1

    try:
        import dotenv

        install_messages.append(f"✅ {dotenv.__name__} trouvé")
    except ImportError:
        install_messages.append("❌ dotenv n'est pas installé")
        are_packages_ok[count] = False
        count += 1

    print("\n".join(install_messages))

    if not all(are_packages_ok):
        return 1

    # Construire la commande
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        APP_FILE,
        "--server.address",
        HOST,
        "--server.port",
        str(PORT),
        "--browser.gatherUsageStats",
        "false",
    ]

    # Afficher l'URL d'accès
    print(f"🌐 Application disponible sur: http://{HOST}:{PORT}")
    print("💡 Appuyez sur Ctrl+C pour arrêter")
    print("-" * 50)

    try:

        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n🛑 Application arrêtée")
        return 0

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
