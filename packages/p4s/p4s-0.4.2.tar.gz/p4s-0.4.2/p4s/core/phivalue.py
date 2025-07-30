"""phosphorus.core.phivalue
---------------------------------
Light‑weight wrapper around a Python AST that stores an optional
semantic type and guard/presupposition and beta‑reduces the AST
at construction time.

All heavy work (pretty HTML, richer type inference) lives elsewhere.
"""

import ast
import copy
from collections import ChainMap
from typing import Any, Optional

from p4s.simplify           import simplify          # local functional API
from p4s.simplify.utils     import capture_env       # caller env snapshot
from p4s.core.display       import render_phi_html   # rich HTML helper
from p4s.core.infer         import infer_and_strip   # type checker / DSL stripper
from p4s.core.stypes        import Type              # semantic type system
from p4s.core.constants     import UNDEF             # sentinel for undefined values

# ---------------------------------------------------------------------------
#  PhiValue
# ---------------------------------------------------------------------------

class PhiValue:
  """An AST + optional semantic type and guard with Jupyter‑friendly HTML."""

  __slots__ = ("expr", "stype", "guard", "_env")

  # ---------------------------------------------------------------------
  #  construction
  # ---------------------------------------------------------------------

  def __init__(self,
               expr: ast.AST | str, *,
               stype: Optional[Type] = None,
               guard: Optional[ast.AST] = None) -> None:
    # 0: parse or accept AST
    if isinstance(expr, str):
      expr = ast.parse(expr, mode="eval").body

    # 1. capture *caller* environment (skip this frame)
    env = capture_env(skip=1)          # ChainMap

    # 2. *Infer* type while DSL cues are still present (also strips DSL cues)
    expr = infer_and_strip(expr, env)
    inferred_type = getattr(expr, "stype", None)
    inferred_guard = getattr(expr, "guard", None)

    # 3. beta‑reduce / macro‑expand (pure)
    simplified = simplify(expr, env=env)
    simplified_guard = inferred_guard and simplify(guard or inferred_guard, env=env)

    # 4. store
    self.expr  = simplified
    self._env  = ChainMap({}, env)     # make a shallow, isolated view
    self.stype = stype or inferred_type or getattr(simplified, "stype", None)
    self.guard = simplified_guard

  # ---------------------------------------------------------------------
  #  functional behaviour
  # ---------------------------------------------------------------------

  def __call__(self, *args: "PhiValue", **kwargs) -> "PhiValue":
    call_ast = ast.Call(
      func=copy.deepcopy(self.expr),
      args=[copy.deepcopy(a.expr) for a in args],
      keywords=[ast.keyword(arg=k, value=copy.deepcopy(kwargs[k].expr)) for k in kwargs]
    )
    phi = PhiValue(call_ast)
    try:
      return phi.eval()
    except:
      return phi

  # ---------------------------------------------------------------------
  #  evaluation helpers
  # ---------------------------------------------------------------------

  def eval(self) -> Any:
    """Evaluate the stored expression in its captured environment."""
    # Python's eval requires a real dict for globals
    env_dict = dict(self._env)
    code = compile(ast.Expression(self.expr), filename="<phivalue>", mode="eval")
    return eval(code, env_dict)

  # ---------------------------------------------------------------------
  #  dunder utilities
  # ---------------------------------------------------------------------

  def __bool__(self):
    return bool(self.eval())

  def __hash__(self):
    return hash((ast.dump(self.expr, annotate_fields=False), self.stype, 
                 ast.dump(self.guard, annotate_fields=False)))

  def __eq__(self, other):
    if isinstance(other, PhiValue):
      if (ast.dump(self.expr, annotate_fields=False) !=
          ast.dump(other.expr, annotate_fields=False)):
        return False

      if self.stype != other.stype:
        return False

      if self.guard == other.guard == None:
        return True

      if self.guard is None or other.guard is None:
        return False

      return (ast.dump(self.guard, annotate_fields=False) ==
                 ast.dump(other.guard, annotate_fields=False))
    
    try:
      return self.eval() == other
    except:
      return NotImplemented

  def __mod__(self, guard):
    if not guard:
      return UNDEF
    return self

  def __repr__(self):
    return ast.unparse(self.expr)

  # Jupyter rich repr
  def _repr_html_(self):
    #return f"<code>{ast.unparse(self.expr)}</code>  <small>{self.stype}</small>"
    return render_phi_html(self.expr, stype=self.stype)

# ---------------------------------------------------------------------------
#  rudimentary tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
  id_ast = ast.parse("lambda x=t: x[t]", mode="eval").body
  id_pv = PhiValue(id_ast)
  two_pv = PhiValue(ast.parse("2", mode="eval").body)

  assert id_pv(two_pv).eval() == 2
  assert id_pv == id_pv
  assert isinstance(hash(id_pv), int)
  print("✅ PhiValue sanity tests passed.")
