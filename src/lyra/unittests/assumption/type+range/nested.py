
# INITIAL:  3:(String, [-inf, inf]), 10 * [6:(String, [-inf, inf]), 20 * 8:(String, [-inf, inf])]
a: str = input()
# STATE:  10 * [6:(String, [-inf, inf]), 20 * 8:(String, [-inf, inf])]
for i in range(10):
    b: str = input()
    for j in range(20):
        c: str = input()
