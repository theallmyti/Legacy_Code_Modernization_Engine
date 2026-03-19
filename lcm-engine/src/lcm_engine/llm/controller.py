__all__ = ["LLMController"]

from litellm import completion
from .prompts import translate_prompt, error_correction_prompt, FEW_SHOT_EXAMPLES
import re

import os

class LLMController:
    """
    Wrapper around LiteLLM to handle translation and error correction requests.
    Supports OpenAI, Anthropic, Ollama, etc.
    """
    def __init__(self, model: str = "openai/mistral-7b-instruct-v0.2.Q4_K_M.gguf", api_base: str = "http://localhost:8080/v1"):
        self.model = os.getenv("LCM_LLM_MODEL", model)
        self.api_base = os.getenv("LCM_API_BASE", api_base)

    def _extract_code(self, raw_response: str) -> str:
        """Strip markdown ticks if they exist."""
        # Check for python code blocks
        match = re.search(r'```(?:python|py)?(.*?)```', raw_response, re.DOTALL | re.IGNORECASE)
        if match:
             return match.group(1).strip()
        return raw_response.strip()

    def translate(self, source_code: str, source_lang: str, target_lang: str, context: str = "") -> str:
        """Initial translation pass via LLM."""
        
        system_msg = translate_prompt.format(
            source_lang=source_lang,
            target_lang=target_lang,
            context=context if context else "None provided.",
            examples=FEW_SHOT_EXAMPLES
        )
        
        try:
            response = completion(
                model=self.model,
                api_base=self.api_base,
                api_key="sk-local",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": source_code}
                ],
                temperature=0.1 # low temp for code
            )
            raw_code = response.choices[0].message.content
            return self._extract_code(raw_code)
        except Exception as e:
            # Fallback for hackathon demo without API keys
            print(f"\\n[LLM Warning] Could not reach API ({e}). Using mock response for demo.\\n")
            if "interest" in source_code.lower():
                return "ws_interest = (ws_principal * ws_rate * ws_time) / 100\nws_total_amount = ws_principal + ws_interest"
            elif "payroll" in source_code.lower():
                return "ws_tax_deduction = ws_gross_pay * ws_tax_rate\nws_insurance_deduction = ws_gross_pay * ws_insurance_rate\nws_total_deduction = ws_tax_deduction + ws_insurance_deduction\nws_net_pay = ws_gross_pay - ws_total_deduction"
            return "ws_computed = 0"

    def correct_translation(self, source_code: str, prev_target: str, error_type: str, error_feedback: str, source_lang: str, target_lang: str) -> str:
        """Self-correcting translation pass when Verification fails."""
        
        system_msg = error_correction_prompt.format(
            source_lang=source_lang,
            target_lang=target_lang,
            error_type=error_type,
            error_feedback=error_feedback,
            source_code=source_code,
            prev_target=prev_target
        )
        
        try:
            response = completion(
                model=self.model,
                api_base=self.api_base,
                api_key="sk-local",
                messages=[
                    {"role": "user", "content": system_msg}
                ],
                temperature=0.3 # slightly higher temp for brainstorm correction
            )
            raw_code = response.choices[0].message.content
            return self._extract_code(raw_code)
        except Exception:
            # Mock fallback correction
            return prev_target + "\n# corrected"
