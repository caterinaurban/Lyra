# import numpy as np
#
# def solve():
#     n = int(raw_input())
#     a = [raw_input() for __ in xrange(n)]
#     a.sort()
#     b = [len(set(x.replace(' ', ''))) for x in a]
#     print a[np.argmax(b)]
#
# if __name__ == '__main__':
#     T = int(raw_input())
#     for t in xrange(T):
#         print 'Case #{0}:'.format(t + 1),
#         solve()

T: int = int(input())
for t in range(T):
    n: int = int(input())
    a: List[str] = []
    # a.sort() -> assume a is sorted
    for i in range(len(a)):
        x: str = input()
        x: str = x.replace(' ', '')
        a.append(x)
    # find position of max element
    idx: int = 0
    max: int = a[0]
    for i in range(len(a)):
        if a[i] > max:
            max = a[i]
    print(max)