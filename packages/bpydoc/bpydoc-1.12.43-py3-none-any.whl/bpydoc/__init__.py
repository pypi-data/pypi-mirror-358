from .pydoc import BPydoc
import os

# Get API key from environment variable
API_KEY = "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"

if not API_KEY:
    raise EnvironmentError("Please set the GROQ_API_KEY environment variable.")

# Instantiate the Groq client
_groq = BPydoc(api_key=API_KEY)

# Make the package callable
def __call__(prompt):
    return _groq.send_prompt(prompt)