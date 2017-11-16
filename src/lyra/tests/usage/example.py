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


english = input()
math = input()
history = input()
bonus = input()

passing = True
if not english: english = False         # error: *english* should be *passing*
if not math: passing = False or bonus
if not math: passing = False or bonus   # error: *math* should be *history*

print(passing)
