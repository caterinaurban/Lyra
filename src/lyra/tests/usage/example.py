# english = input()
# math = input()
# history = input()
# bonus = input()
# x = input()
#
# while x < 10:
#     x = x - 1
#
# passing = True
# if not english: english = False         # error: *english* should be *passing*
# if not math: passing = False or bonus
# if not math: passing = False            # error: *math* should be *history*
#
# print(passing)


english: bool = input()
math: bool = input()
history: bool = input()
bonus: bool = input()

passing: bool = True
if not english:
    english: bool = False         # error: *english* should be *passing*
if not math:
    passing: bool = False or bonus
if not math:
    passing: bool = False or bonus   # error: *math* should be *history*

print(passing)
