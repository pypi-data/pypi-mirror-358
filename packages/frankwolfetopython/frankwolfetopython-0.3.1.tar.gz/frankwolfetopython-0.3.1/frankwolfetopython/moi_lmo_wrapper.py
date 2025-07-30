from ._julia_env import jl
from typing import Callable, Union, Dict, Any, Tuple, List
import numpy as np

def wrap_moi(constraints: List[Tuple[np.ndarray, np.ndarray, str]]):
    global jl
    """
    Allows user to set custom linear constraints for solver using the MathOptInterface (MOI) in Julia

    Params:
        - A: Matrix representing constraints
        - b: RHS

    Returns: 
        - MOI model with the given linear constraints.
    """
    script = "optimizer = GLPK.Optimizer()\n"

    for idx, (A, b, sense) in enumerate(constraints):
            if not isinstance(A, np.ndarray) or not isinstance(b, np.ndarray):
                raise ValueError("A and b must be numpy arrays.")
            if A.ndim != 2 or b.ndim != 1:
                raise ValueError("A must be 2D, b must be 1D.")
            if A.shape[0] != b.shape[0]:
                raise ValueError("Rows of A must match length of b.")
            
            n_vars = A.shape[1]
            n_cons = A.shape[0]
            A = A.astype(float)
            b = b.astype(float)
            A_jl = "[" + "; ".join(" ".join(str(A[i, j]) for j in range(n_vars)) for i in range(n_cons)) + "]"
            b_jl = "[" + "; ".join(str(bi) for bi in b) + "]"

            if sense == "leq":
                constr_type = "MOI.LessThan"
            elif sense == "eq":
                constr_type = "MOI.EqualTo"
            elif sense == "geq":
                constr_type = "MOI.GreaterThan"
            else:
                raise ValueError("sense must be 'leq', 'eq', or 'geq'")
            
            # Add variables only once
            if idx == 0:
                script += f"x = MOI.add_variables(optimizer, {n_vars})\n"
            script += f"A = {A_jl}\n"
            script += f"b = {b_jl}\n"
            script += f"for i in 1:{n_cons}\n"
            script += f"    MOI.add_constraint(optimizer, MOI.ScalarAffineFunction(MOI.ScalarAffineTerm.(A[i, :], x), 0.0), {constr_type}(b[i]))\n"
            script += "end\n"

    jl.seval(script)
    lmo = jl.FrankWolfe.MathOptLMO(jl.optimizer)
    return lmo