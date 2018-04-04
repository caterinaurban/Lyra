
english: bool = bool(input())
math: bool = bool(input())
science: bool = bool(input())
bonus: bool = bool(input())
passing: bool = True
if not english:
    english: bool = False         # error: *english* should be *passing*
if not math:
    passing: bool = False or bonus
if not math:
    passing: bool = False or bonus   # error: *math* should be *science*
print(passing)
