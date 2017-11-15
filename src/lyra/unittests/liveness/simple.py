
# INITIAL: english -> Dead, math -> Dead, science -> Dead, bonus -> Dead, passing -> Dead
english: bool = input()
math: bool = input()
science: bool = input()
bonus: bool = input()
# STATE: english -> Live, math -> Live, science -> Dead, bonus -> Live, passing -> Dead
passing: bool = True
# STATE: english -> Live, math -> Live, science -> Dead, bonus -> Live, passing -> Live
if not english:
    # STATE:  english -> Dead, math -> Live, science -> Dead, bonus -> Live, passing -> Live
    english: bool = False         # error: *english* should be *passing*
# STATE:  english -> Dead, math -> Live, science -> Dead, bonus -> Live, passing -> Live
if not math:
    # STATE:  english -> Dead, math -> Live, science -> Dead, bonus -> Live, passing -> Dead
    passing: bool = False or bonus
# STATE:  english -> Dead, math -> Live, science -> Dead, bonus -> Live, passing -> Live
if not math:
    # STATE: english -> Dead, math -> Dead, science -> Dead, bonus -> Live, passing -> Dead
    passing: bool = False or bonus   # error: *math* should be *science*
# STATE: english -> Dead, math -> Dead, science -> Dead, bonus -> Dead, passing -> Live
print(passing)
# FINAL: english -> Dead, math -> Dead, science -> Dead, bonus -> Dead, passing -> Dead
