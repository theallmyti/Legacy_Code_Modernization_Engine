from typing import Dict, Any, Tuple

# Categories as requested
ERROR_TYPES = [
    "SYNTAX_ERROR", 
    "WRONG_ROUNDING", 
    "WRONG_SCALE", 
    "MISSING_SETSCALE", 
    "CHAINED_CALCULATION",
    "MATH_MISMATCH",
    "VERIFICATION_TIMEOUT"
]

class ErrorAnalyzer:
    """
    Analyzes failures from the Z3 solver or the compiler/executor
    to categorize them and assist the AI agent in correcting code.
    """
    def __init__(self):
        pass

    def analyze_error(self, source_code: str, target_code: str, z3_status: str, counter_example: Dict[str, str] = None) -> str:
        """
        Categorize the failure.
        """
        if z3_status == "SYNTAX_ERROR":
            return "SYNTAX_ERROR"
            
        if z3_status == "VERIFICATION_TIMEOUT":
            return "VERIFICATION_TIMEOUT"
            
        if z3_status == "MATH_MISMATCH" and counter_example:
            # Try to be smart about what went wrong using heuristics on the code
            
            if 'round(' in target_code.lower() and not 'round(' in source_code.lower():
                # Extraneous rounding
                return "WRONG_ROUNDING"
                
            if '/' in source_code and '/' in target_code:
                # If they both have divisions but fail, it might be a float scale issue
                return "WRONG_SCALE"
                
            if 'decimal' in source_code.lower() and 'decimal' not in target_code.lower():
                 return "MISSING_SETSCALE"
                 
            # Default to mathematical mismatch or chained calculations grouping wrong
            return "CHAINED_CALCULATION"
            
        return "UNKNOWN_ERROR"
