ANTHROPIC_PREFIX = "anthropic"
CHATGPT_PREFIX = "openai"
CRIL_PREFIX = "cril"
GOOGLE_PREFIX = "google"

BASE_CRIL_URL = "http://172.17.141.34/api"
BASE_GOOGLE_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


MODELS = [
    f"{ANTHROPIC_PREFIX} [claude-sonnet-4-20250514]",
    f"{CRIL_PREFIX} [qwen3:14b]",
    f"{CRIL_PREFIX}  [llama3.2:latest]",
    f"{CHATGPT_PREFIX}  [gpt-3.5]",
    f"{CHATGPT_PREFIX}  [gpt-4.1]",
    f"{GOOGLE_PREFIX}  [gemini-2.0-flash]",
]


# Example problems
EXAMPLE_PROBLEMS = {
    "N-Queens": "Solve the 8-Queens problem: place 8 queens on a chessboard so no two queens attack each other",
    "Sudoku": "Create a 4x4 Sudoku solver with variables for each cell and constraints for rows, columns, and blocks",
    "Graph Coloring": "Color a graph with 4 nodes and edges [(0,1), (1,2), (2,3), (3,0)] using minimum colors",
    "Knapsack": "Knapsack problem with items having weights [2,3,4,5] and values [3,4,5,6], capacity 5",
    "Custom": "Enter your own problem description",
}
