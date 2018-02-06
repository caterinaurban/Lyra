# INITIAL [11 x [2:(Any, [-inf, inf])] with delimiter '', 5:(Int, [-inf, inf]), 0 x [6:((Any, [-inf, inf]), [.ID=5 - len(.ID=6) + 1 <= 0])] with delimiter ',', 0 x [9:(Any, [-inf, inf])] with delimiter ';', 10:((Int, [-inf, inf]), [.ID=10 - len(.ID=9) + 1 <= 0]), 0 x [13:((Any, [-inf, inf]), [.VAR0 - len(.ID=13) + 21 <= 0])] with delimiter ' ']
list1: List[str] = input().split()
print(list1[10])

n: int = int(input())
list2: List[str] = input().split(",")
print(list2[n])

list3: List[str] = input().split(";")
p: int = int(input())
print(list3[p])

list4: List[str] = input().split(" ")
M: int = 20
print(list4[M])
