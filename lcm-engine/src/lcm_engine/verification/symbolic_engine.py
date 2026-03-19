from typing import Dict, Any, List
import re

class SymbolicEngine:
    """
    Parses simple target/source code statements to a basic Intermediate Representation (IR)
    specifically designed for tracking arithmetic operations in financial codes.
    """
    def __init__(self):
        # We look for equations: Var = Expr
        self.equation_pattern = re.compile(r"([A-Za-z0-9_\-]+)\s*=\s*(.*)")
        
        # Mapping COBOL variables to Python variables for normalization
        self.normalize_pattern = re.compile(r"[-_]([A-Za-z0-9])")
        
    def _normalize_var(self, var_name: str) -> str:
        """WS-VAR-NAME -> ws_var_name"""
        return var_name.replace('-', '_').lower()

    def translate_cobol_to_ir(self, source_code: str) -> List[Dict[str, str]]:
        """
        Convert COBOL COMPUTE statements into a list of variable equations.
        e.g. COMPUTE WS-NET = WS-GROSS - WS-TAX -> {'var': 'ws_net', 'expr': 'ws_gross - ws_tax'}
        """
        ir = []
        for line in source_code.split('\n'):
            line = line.strip()
            if line.upper().startswith("COMPUTE "):
                statement = line[7:].strip()
                match = self.equation_pattern.match(statement)
                if match:
                    var = self._normalize_var(match.group(1).strip())
                    expr = match.group(2).strip()
                    # Basic normalizations
                    expr = expr.replace('**', '^') # Z3 uses ** but we might want to normalize
                    # Replace variables inside expression
                    def _replace_var(m):
                        w = m.group(0)
                        if not w.isnumeric() and not w.replace('.', '').isnumeric():
                            return self._normalize_var(w)
                        return w
                        
                    expr = re.sub(r'[A-Za-z0-9_-]+', _replace_var, expr)
                    ir.append({'var': var, 'expr': expr})
                    
        return ir

    def translate_python_to_ir(self, target_code: str) -> List[Dict[str, str]]:
        """
        Extract basic assignments from target Python code.
        """
        ir = []
        for line in target_code.split('\n'):
            line = line.strip()
            # Ignore defs, comments, etc for simple arithmetic mapping
            if '=' in line and not line.startswith(('def', 'class', 'import', '#', 'return')):
                match = self.equation_pattern.match(line)
                if match:
                    var = match.group(1).strip()
                    expr = match.group(2).strip()
                    # Python usually uses lowercase, but lets normalize anyway
                    var = self._normalize_var(var)
                    def _replace_var(m):
                        w = m.group(0)
                        if not w.isnumeric() and not w.replace('.', '').isnumeric():
                            return self._normalize_var(w)
                        return w
                    expr = re.sub(r'[A-Za-z0-9_-]+', _replace_var, expr)
                    ir.append({'var': var, 'expr': expr})
        return ir

    def get_variables(self, ir_list: List[Dict[str, str]]) -> List[str]:
        """Extract all unique variables used in an IR list."""
        vars_set = set()
        for stmt in ir_list:
            vars_set.add(stmt['var'])
            words = re.split(r'\W+', stmt['expr'])
            for w in words:
                if w and not w.isnumeric() and not w.replace('.', '').isnumeric():
                    vars_set.add(w)
        return list(vars_set)
