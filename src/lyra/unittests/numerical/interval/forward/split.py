temp: List[str] = input()
index: int = 0
for i in range(10):
    x: int = int(temp[index].rstrip().split()[0])
    print(x)