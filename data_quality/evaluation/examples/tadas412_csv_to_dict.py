from typing import List

result: List[str] = ["", "", ""]  # instead of [] with later append
headers: List[str] = input().split(",")
for i in range(3):  # instad of with open(infile, 'r')
    line: List[str] = input().split(",")
    if len(line) < len(headers):  # != as < and >
        raise ValueError  # different error
    if len(line) > len(headers):
        raise ValueError  # different error
    result[i]: str = line  # instead of (headers, line)
print(result)  # print instead of return
