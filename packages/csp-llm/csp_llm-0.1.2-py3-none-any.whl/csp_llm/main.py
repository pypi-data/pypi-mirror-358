import gui
import streamlit as st
from check_java import require_java
from csp_tools import CSPExtractor, CSPGenerator, MCPCSPRunner

# MCP and Local Model imports
try:
    import anthropic
    import dotenv

    # import mcp
    import openai
except ImportError as e:
    st.error(
        f"Missing required packages. Install with: pip install openai anthropic pycsp3 streamlit dotenv"
    )
    st.stop()

try:
    from pycsp3 import __pycsp3_version__

    print(f"✅ pycsp3 {__pycsp3_version__}")
except ImportError:
    print("❌ pycsp3 n'est pas installé")

    st.stop()


if not require_java(8):  # pycsp3 nécessite Java 8+
    print("❌ Java 8+ requis pour utiliser pycsp3")
    st.stop()

if __name__ == "__main__":
    gui.main()
