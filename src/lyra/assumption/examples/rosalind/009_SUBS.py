# source: http://rosalind.info/problems/subs/
# Find all positions in which t exists as a substring in s

s: str = input()
t: str = input()

if len(t) > len(s):
    raise ValueError

for i in range(len(s)):
    if s[i: i + len(t)] == t:
        print(i + 1)


