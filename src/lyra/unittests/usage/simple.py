
# INITIAL: english -> N, math -> W, science -> N, bonus -> W, passing -> W
english: bool = bool(input())
math: bool = bool(input())
science: bool = bool(input())
bonus: bool = bool(input())
# STATE: english -> N, math -> U, science -> N, bonus -> U, passing -> W
passing: bool = True
# STATE: english -> N, math -> U, science -> N, bonus -> U, passing -> U
if not english:
    english: bool = False         # error: *english* should be *passing*
if not math:
    passing: bool = False or bonus
if not math:
    passing: bool = False or bonus   # error: *math* should be *science*
print(passing)
# FINAL: english -> N, math -> N, science -> N, bonus -> N, passing -> N
