# INITIAL [2:(Int, [-inf, inf]), 0 x [3:((Any, [-inf, inf]), {-.ID=2 + len(.ID=3) + 0 <= 0})] with delimiter '', 0 x [8:(Any, [-inf, inf])] with delimiter '', 9:((Int, [-inf, inf]), {-.ID=9 + len(.ID=8) + 0 <= 0}), 13:(Int, [-inf, inf]), 0 x [14:((Any, [-inf, inf]), {-.ID=13 + len(.ID=14) + 0 <= 0})] with delimiter '']
a: int = int(input())
list1: List[str] = input().split()
list2: List[str] = list1
if a < len(list2):
    raise ValueError

list3: List[str] = input().split()
b: int = int(input())
if b < len(list3):
    raise ValueError

a: int = int(input())
list4: List[str] = input().split()
y: int = len(list4)
if a < y:
    raise ValueError
