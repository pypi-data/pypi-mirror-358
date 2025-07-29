#!/usr/bin/env python3
"""
Fonctions pour détecter Java et sa version
Compatible Windows, Linux, macOS
"""

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict, NamedTuple, Optional


@dataclass
class JavaInfo:
    """Informations sur l'installation Java"""

    version: str
    major_version: int
    vendor: str
    runtime: str
    path: str
    is_openjdk: bool = False


def check_java_installed() -> Optional[JavaInfo]:
    """
    Vérifie si Java est installé et retourne les informations de version.

    Returns:
        JavaInfo: Informations Java si installé, None sinon
    """

    # Commandes Java à tester
    java_commands = ["java", "java.exe"]

    for java_cmd in java_commands:
        # Vérifier si la commande existe
        java_path = shutil.which(java_cmd)
        if not java_path:
            continue

        try:
            # Exécuter java -version
            result = subprocess.run(
                [java_cmd, "-version"],
                capture_output=True,
                text=True,
                timeout=10,  # Timeout de 10 secondes
            )

            # Java écrit sa version sur stderr (pas stdout)
            version_output = result.stderr

            if result.returncode == 0 and version_output:
                return parse_java_version(version_output, java_path)

        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            continue

    return None


def parse_java_version(version_output: str, java_path: str) -> Optional[JavaInfo]:
    """
    Parse la sortie de 'java -version' pour extraire les informations.

    Args:
        version_output: Sortie de la commande java -version
        java_path: Chemin vers l'exécutable Java

    Returns:
        JavaInfo: Informations parsées ou None si parsing échoue
    """

    try:
        lines = version_output.strip().split("\n")

        # Première ligne contient généralement la version
        version_line = lines[0] if lines else ""

        # Extraire la version avec regex
        # Formats possibles:
        # java version "1.8.0_291"
        # openjdk version "11.0.11" 2021-04-20
        # java version "17.0.1" 2021-10-19 LTS

        version_match = re.search(r'version\s+"([^"]+)"', version_line)
        if not version_match:
            return None

        version_string = version_match.group(1)

        # Déterminer la version majeure
        major_version = extract_major_version(version_string)

        # Déterminer le vendor/runtime
        vendor = "Unknown"
        runtime = "Unknown"
        is_openjdk = False

        if "openjdk" in version_line.lower():
            vendor = "OpenJDK"
            is_openjdk = True
        elif "oracle" in version_line.lower():
            vendor = "Oracle"
        elif "ibm" in version_line.lower():
            vendor = "IBM"
        elif "amazon" in version_line.lower():
            vendor = "Amazon Corretto"
        elif "zulu" in version_line.lower():
            vendor = "Azul Zulu"

        # Extraire le runtime de la deuxième ligne si disponible
        if len(lines) > 1:
            runtime_line = lines[1]
            if "Runtime Environment" in runtime_line:
                runtime = runtime_line.strip()
            elif "OpenJDK Runtime Environment" in runtime_line:
                runtime = "OpenJDK Runtime Environment"
                is_openjdk = True

        return JavaInfo(
            version=version_string,
            major_version=major_version,
            vendor=vendor,
            runtime=runtime,
            path=java_path,
            is_openjdk=is_openjdk,
        )

    except Exception as e:
        print(f"Erreur lors du parsing de la version Java: {e}")
        return None


def extract_major_version(version_string: str) -> int:
    """
    Extrait la version majeure Java depuis la string de version.

    Args:
        version_string: Version string (ex: "1.8.0_291", "11.0.11", "17.0.1")

    Returns:
        int: Version majeure (8, 11, 17, etc.)
    """

    try:
        # Supprimer les suffixes comme "+9" ou "-ea"
        clean_version = re.sub(r"[+-].*$", "", version_string)

        parts = clean_version.split(".")

        if len(parts) >= 2 and parts[0] == "1":
            # Format ancien: 1.8.0_291 -> version 8
            return int(parts[1])
        elif len(parts) >= 1:
            # Format nouveau: 11.0.11 -> version 11
            return int(parts[0])
        else:
            return 0

    except (ValueError, IndexError):
        return 0


def get_java_version_simple() -> Optional[str]:
    """
    Version simplifiée qui retourne juste la version string.

    Returns:
        str: Version Java (ex: "11.0.11") ou None si non installé
    """
    java_info = check_java_installed()
    return java_info.version if java_info else None


def is_java_version_compatible(required_major: int) -> bool:
    """
    Vérifie si la version Java installée est compatible.

    Args:
        required_major: Version majeure requise (ex: 8, 11, 17)

    Returns:
        bool: True si compatible, False sinon
    """
    java_info = check_java_installed()
    if not java_info:
        return False

    return java_info.major_version >= required_major


def get_detailed_java_info() -> Dict[str, str]:
    """
    Retourne des informations détaillées sur Java sous forme de dictionnaire.

    Returns:
        Dict: Informations Java ou dictionnaire vide si non installé
    """
    java_info = check_java_installed()

    if not java_info:
        return {}

    return {
        "version": java_info.version,
        "major_version": str(java_info.major_version),
        "vendor": java_info.vendor,
        "runtime": java_info.runtime,
        "path": java_info.path,
        "is_openjdk": str(java_info.is_openjdk),
        "is_installed": "true",
    }


def check_java_environment() -> Dict[str, str]:
    """
    Vérifie l'environnement Java complet (JAVA_HOME, PATH, etc.).

    Returns:
        Dict: Informations sur l'environnement Java
    """
    env_info = {}

    # Java installé
    java_info = check_java_installed()
    if java_info:
        env_info.update(
            {
                "java_installed": "true",
                "java_version": java_info.version,
                "java_major": str(java_info.major_version),
                "java_vendor": java_info.vendor,
                "java_path": java_info.path,
            }
        )
    else:
        env_info["java_installed"] = "false"

    # JAVA_HOME
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        env_info["java_home"] = java_home
        env_info["java_home_exists"] = str(os.path.exists(java_home))
    else:
        env_info["java_home"] = "not_set"

    # PATH
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    java_in_path = any("java" in dir_path.lower() for dir_path in path_dirs)
    env_info["java_in_path"] = str(java_in_path)

    return env_info


# ========================================
# FONCTIONS DE COMMODITÉ
# ========================================


def print_java_info() -> None:
    """Affiche les informations Java de manière formatée."""
    java_info = check_java_installed()

    if not java_info:
        print("❌ Java n'est pas installé ou introuvable")
        print("💡 Installez Java depuis: https://adoptium.net/")
        return

    print("☕ Informations Java:")
    print(f"   Version: {java_info.version}")
    print(f"   Version majeure: {java_info.major_version}")
    print(f"   Vendor: {java_info.vendor}")
    print(f"   Runtime: {java_info.runtime}")
    print(f"   Chemin: {java_info.path}")
    print(f"   OpenJDK: {'Oui' if java_info.is_openjdk else 'Non'}")

    # Vérifier des versions communes
    if java_info.major_version >= 17:
        print("✅ Version moderne (17+)")
    elif java_info.major_version >= 11:
        print("✅ Version LTS supportée (11+)")
    elif java_info.major_version >= 8:
        print("⚠️  Version ancienne mais supportée (8+)")
    else:
        print("❌ Version très ancienne (< 8)")


def require_java(min_version: int = 8) -> bool:
    """
    Vérifie qu'une version minimale de Java est disponible.

    Args:
        min_version: Version majeure minimale requise

    Returns:
        bool: True si disponible, False sinon (avec message d'erreur)
    """
    java_info = check_java_installed()

    if not java_info:
        print(f"❌ Java {min_version}+ requis mais non installé")
        print("💡 Installez Java depuis: https://adoptium.net/")
        return False

    if java_info.major_version < min_version:
        print(f"❌ Java {min_version}+ requis")
        print(
            f"   Version installée: {java_info.version} (majeure: {java_info.major_version})"
        )
        print("💡 Mettez à jour Java vers une version plus récente")
        return False

    print(f"✅ Java {java_info.version} détecté (>= {min_version})")
    return True
