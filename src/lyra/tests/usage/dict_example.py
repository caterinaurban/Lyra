
i: int = int(input())
v: int = 8

dict_in: Dict[int,int] = {}
dict_out: Dict[int,int] = {}
dict_own: Dict[int,int] = {3:6}

for key in range(v+1):
    value: int = int(input())
    if -3 <= value <= 3:
        dict_in[key]: int = value

dict_own[v]: int = -1
if 2 <= i <= 5:
    dict_own[i]: int = 0

for k in dict_own.keys():
    dict_out[k]: int = dict_in[k] + dict_own[k]

for k, v in dict_out.items():
    if k >= 3:
        print(v)
