
# INITIAL: i -> [-inf, inf]; len(x) -> [0, inf]; len(y) -> [0, inf]; x -> [-inf, inf]; y -> [-inf, inf]
x: List[str] = input().split()
y: List[int] = list()
# STATE: i -> [-inf, inf]; len(x) -> [0, inf]; len(y) -> [0, 0]; x -> [-inf, inf]; y -> ⊥
for i in range(len(x)):     # LOOP: i -> [-inf, inf]; len(x) -> [0, inf]; len(y) -> [0, inf]; x -> [-inf, inf]; y -> [-inf, inf]
    y.append(int(x[i]))
# FINAL: i -> [-inf, inf]; len(x) -> [0, inf]; len(y) -> [0, inf]; x -> [-inf, inf]; y -> [-inf, inf]
