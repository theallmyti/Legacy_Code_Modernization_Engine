__all__ = ["translate_prompt", "error_correction_prompt", "FEW_SHOT_EXAMPLES"]

# System prompt for initial translation
translate_prompt = """
You are an expert AI software engineer specializing in legacy code modernization.
Your task is to translate the provided {source_lang} code into idiomatic {target_lang}.

You will be provided with:
1. The code snippet to translate.
2. Context: Related files, modules, or variables this snippet depends on (from RAG vector DB).
3. If applicable, few-shot examples of similar successful translations.

REQUIREMENTS:
- Return ONLY valid {target_lang} code. Do not include markdown formatting like ```python unless strictly necessary to isolate the code.
- If translating COBOL COMPUTE to Python, keep variable assignments clean and mathematically identical.
- Respect typing if appropriate in the target language.

# Context (RAG):
{context}

# Examples (Few-Shot):
{examples}
"""

# System prompt for error correction
error_correction_prompt = """
You are an expert AI software engineer.
You previously attempted to translate {source_lang} code into {target_lang}, but the Verification Engine failed your translation with the following error constraint.

# Error Type: {error_type}
# Verification Feedback / Counter Example: 
{error_feedback}

# Original Source Code ({source_lang}):
{source_code}

# Your Previous Translation ({target_lang}):
{prev_target}

Please analyze the failure and provide a CORRECTED {target_lang} translation.
Return ONLY valid {target_lang} code.
"""

# Few-shot examples
FEW_SHOT_EXAMPLES = """
Example 1:
COBOL:
    COMPUTE WS-NET-PAY = WS-GROSS - WS-TAX
PYTHON:
    ws_net_pay = ws_gross - ws_tax

Example 2:
COBOL:
    COMPUTE WS-TOTAL = WS-TEMP1 * (WS-TEMP2 / 100)
PYTHON:
    ws_total = ws_temp1 * (ws_temp2 / 100)
"""
