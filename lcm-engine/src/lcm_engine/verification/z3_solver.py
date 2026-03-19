import z3
from typing import List, Dict, Any, Tuple
from .error_analyzer import ERROR_TYPES

class Z3Solver:
    """
    Uses Microsoft's Z3 SMT Solver to prove mathematical equivalence between
    legacy (source) constraints and modern (target) constraints.
    """
    def __init__(self):
        self.solver = z3.Solver()

    def _safe_eval(self, expr_str: str, var_map: Dict[str, z3.Real]) -> Any:
        """
        Evaluate string expression safely into a Z3 compatible object.
        Replaces standard arithmetic with Z3 ones.
        """
        # A tiny evaluator or using eval with strict locals
        # Replace exponentiation
        expr_str = expr_str.replace('^', '**')
        
        # Prepare execution environment with only Z3 variables
        safe_env = {k: v for k, v in var_map.items()}
        # Add basic Z3 mathematical constants or functions if needed
        # safe_env['z3'] = z3 
        
        try:
            return eval(expr_str, {"__builtins__": {}}, safe_env)
        except Exception as e:
            # If evaluation fails, it's typically SYNTAX or UNKNOWN_FUNC
            raise ValueError(f"Could not convert expression '{expr_str}' to Z3: {e}")

    def verify_equivalence(self, source_ir: List[Dict], target_ir: List[Dict], variables: List[str]) -> Tuple[bool, Dict, str]:
        """
        Verifies that source assignments mathematically equal target assignments.
        Returns (is_equivalent, counter_example_dict, error_status).
        """
        self.solver.reset()
        
        # Declare all variables as Z3 Reals (suitable for financial code precision testing)
        z3_vars = {v: z3.Real(v) for v in variables}
        
        # Track final states of variables
        source_state = {}
        target_state = {}
        
        try:
            # Build constraints for Source
            for stmt in source_ir:
                var = stmt['var']
                expr = stmt['expr']
                source_state[var] = self._safe_eval(expr, z3_vars)
                # Assign to our tracker vars map so later expressions can use the simplified expression
                z3_vars[var] = source_state[var] 
                
            # Reset vars to symbolic base for target
            z3_vars = {v: z3.Real(v) for v in variables}
            
            # Build constraints for Target
            for stmt in target_ir:
                var = stmt['var']
                expr = stmt['expr']
                target_state[var] = self._safe_eval(expr, z3_vars)
                z3_vars[var] = target_state[var]
        except ValueError as e:
            return False, {"error": str(e)}, "SYNTAX_ERROR"
            
        # Optimization: We only care about variables that were modified in both or either
        vars_to_check = set(list(source_state.keys()) + list(target_state.keys()))
        
        # If no variables modified, they are trivially equivalent
        if not vars_to_check:
            return True, None, "SUCCESS"
            
        # Create the equality assertion: Not(And(s_var1 == t_var1, s_var2 == t_var2, ...))
        # If the negation is UN-satisfiable, the expressions are ALWAYs equal.
        equivalences = []
        for var in vars_to_check:
            s_val = source_state.get(var, z3.Real(var))
            t_val = target_state.get(var, z3.Real(var))
            
            # Use Z3 simplify to check if they are identical trivially before asking the solver
            if str(z3.simplify(s_val == t_val)) == "True":
                continue
                
            equivalences.append(s_val == t_val)
            
        if not equivalences:
             return True, None, "SUCCESS"
             
        # Add solver constraint: "What if they are NOT equivalent?"
        self.solver.add(z3.Not(z3.And(*equivalences)))
        
        result = self.solver.check()
        
        if result == z3.unsat:
            # They are always equivalent! (Proof)
            return True, None, "SUCCESS"
        elif result == z3.sat:
            # We found a counter-example where source != target
            model = self.solver.model()
            counter_example = {}
            for d in model.decls():
                counter_example[d.name()] = str(model[d])
            return False, counter_example, "MATH_MISMATCH"
        else:
            # z3.unknown
            return False, None, "VERIFICATION_TIMEOUT"
