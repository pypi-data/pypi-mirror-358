#!/usr/bin/env python3
"""
Version simplifiée du lanceur Streamlit
Usage basique sans arguments compliqués
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Lance l'application csp_llm avec une configuration basique."""

    # Configuration par défaut
    APP_FILE = "src/csp_llm/main.py"  # Nom de votre app Streamlit
    HOST = "localhost"  # ou "0.0.0.0" pour l'accès réseau
    PORT = 8501  # Port par défaut de Streamlit

    print("🚀 Lancement de l'application Streamlit...")

    # Vérifier que le fichier existe
    app_path = Path(APP_FILE)
    if not app_path.exists():
        print(f"❌ Erreur: {APP_FILE} introuvable")
        print("💡 Assurez-vous que votre fichier Streamlit existe")
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
        import pycsp3

        install_messages.append(f"✅ pycsp3 {pycsp3.__pycsp3_version__} trouvé")
    except ImportError:
        install_messages.append("❌ pycsp3 n'est pas installé")
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
        # Lancer Streamlit
        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n🛑 Application arrêtée")
        return 0

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
