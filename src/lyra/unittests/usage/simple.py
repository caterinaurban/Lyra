
# INITIAL: bonus -> W; english -> N; math -> W; passing -> W; science -> N
english: bool = bool(input())
math: bool = bool(input())
science: bool = bool(input())
bonus: bool = bool(input())
# STATE: bonus -> U; english -> N; math -> U; passing -> W; science -> N
passing: bool = True
# STATE: bonus -> U; english -> N; math -> U; passing -> U; science -> N
if not english:
    english: bool = False         # error: *english* should be *passing*
if not math:
    passing: bool = False or bonus
if not math:
    passing: bool = False or bonus   # error: *math* should be *science*
print(passing)
# FINAL: bonus -> N; english -> N; math -> N; passing -> N; science -> N
