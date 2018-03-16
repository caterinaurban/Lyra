# Analysis finds [6:Any with delimiter ',', 3 x [8:Any with delimiter "," and [len(.ID=8) - len(.ID=6) + 0 <= 0, -len(.ID=8) + len(.ID=6) + 0 <= 0]]]
# Manually +: len(headers) > 3 and len(line) > 3

from typing import List
from data_quality.examples.homeworks.cis192.tadas412 import InvalidFormatException

headers: List[str] = input().split(",")
for i in range(3):  # instad of with open(infile, 'r')
    line: List[str] = input().split(",")
    if len(line) < len(headers):  # != as < and >
        raise InvalidFormatException  # different error
    if len(line) > len(headers):
        raise InvalidFormatException  # different error
    print(headers[i])  # instead of gathering all results and print after loop
    print(line[i])
