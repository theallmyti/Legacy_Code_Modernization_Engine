import pytest
from lcm_engine.verification.symbolic_engine import SymbolicEngine
from lcm_engine.verification.z3_solver import Z3Solver

def test_symbolic_engine_ir():
    sym = SymbolicEngine()
    
    # Test COBOL
    cobol_code = """
    COMPUTE WS-NET-PAY = WS-GROSS - WS-TAX
    """
    ir_cobol = sym.translate_cobol_to_ir(cobol_code)
    assert len(ir_cobol) == 1
    assert ir_cobol[0]['var'] == 'ws_net_pay'
    assert 'ws_gross' in ir_cobol[0]['expr']
    
    # Test Python
    python_code = """
    ws_net_pay = ws_gross - ws_tax
    """
    ir_py = sym.translate_python_to_ir(python_code)
    assert len(ir_py) == 1
    assert ir_py[0]['var'] == 'ws_net_pay'

def test_z3_solver_equivalent():
    # Setup IRs that are mathematically equivalent
    solver = Z3Solver()
    
    source = [{'var': 'a', 'expr': 'x + y'}]
    
    # y + x is mathematically identical
    target1 = [{'var': 'a', 'expr': 'y + x'}]
    
    # Check
    variables = ['a', 'x', 'y']
    is_valid, cex, status = solver.verify_equivalence(source, target1, variables)
    
    assert is_valid is True
    assert status == "SUCCESS"

def test_z3_solver_not_equivalent():
    solver = Z3Solver()
    
    source = [{'var': 'a', 'expr': 'x + y'}]
    # Subtraction is not identical
    target2 = [{'var': 'a', 'expr': 'x - y'}]
    
    variables = ['a', 'x', 'y']
    is_valid, cex, status = solver.verify_equivalence(source, target2, variables)
    
    assert is_valid is False
    assert status == "MATH_MISMATCH"
    assert cex is not None
