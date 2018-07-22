
# INITIAL: bonus -> Dead, english -> Dead, math -> Dead, passing -> Dead, science -> Dead
english: bool = bool(input())
math: bool = bool(input())
science: bool = bool(input())
bonus: bool = bool(input())
# STATE: bonus -> Live, english -> Live, math -> Live, passing -> Dead, science -> Dead
passing: bool = True
# STATE: bonus -> Live, english -> Live, math -> Live, passing -> Live, science -> Dead
if not english:
    # STATE:  bonus -> Live, english -> Dead, math -> Live, passing -> Live, science -> Dead
    english: bool = False         # error: *english* should be *passing*
# STATE:  bonus -> Live, english -> Dead, math -> Live, passing -> Live, science -> Dead
if not math:
    # STATE:  bonus -> Live, english -> Dead, math -> Live, passing -> Dead, science -> Dead
    passing: bool = False or bonus
# STATE:  bonus -> Live, english -> Dead, math -> Live, passing -> Live, science -> Dead
if not math:
    # STATE: bonus -> Live, english -> Dead, math -> Dead, passing -> Dead, science -> Dead
    passing: bool = False or bonus   # error: *math* should be *science*
# STATE: bonus -> Dead, english -> Dead, math -> Dead, passing -> Live, science -> Dead
print(passing)
# FINAL: bonus -> Dead, english -> Dead, math -> Dead, passing -> Dead, science -> Dead
