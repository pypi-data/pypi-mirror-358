import gui
import streamlit as st
from csp_tools import CSPExtractor, CSPGenerator, MCPCSPRunner

# MCP and Local Model imports
try:
    import anthropic
    import dotenv

    # import mcp
    import openai
    import pycsp3
except ImportError as e:
    st.error(
        f"Missing required packages. Install with: pip install openai anthropic pycsp3 streamlit dotenv"
    )
    st.stop()

if __name__ == "__main__":
    gui.main()
