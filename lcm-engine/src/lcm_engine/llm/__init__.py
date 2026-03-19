__all__ = ["translate_prompt", "error_correction_prompt", "FEW_SHOT_EXAMPLES", "LLMController"]
from .prompts import translate_prompt, error_correction_prompt, FEW_SHOT_EXAMPLES
from .controller import LLMController
