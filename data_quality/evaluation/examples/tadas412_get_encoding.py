# analysis finds 3 x [2 x any with delimiter ","]
# manually: 3 x [2 x [int with 1 digit, any with 1 char] with delimiter ","] and data[0] < len(encoding)

from typing import List
from data_quality.examples.homeworks.cis192.tadas412 import InvalidFormatException

encoding: List[str] = ["", "", ""]  # list instead of dict
# without try except
for i in range(3):  # input() instead of open()
    data: List[str] = input().split(",")
    if len(data) != 2:  # single ifs instead of .. or ..
        raise InvalidFormatException

    data0: str = data[0]
    if len(data0) != 1:
        raise InvalidFormatException

    data1: str = data[1]
    if len(data1) != 1:
        raise InvalidFormatException

    if data[0] in encoding:
        raise InvalidFormatException

    data[0]: int = int(data[0])
    data0_int: int = data[0]
    encoding[data0_int]: str = data[1]
print(encoding)  # print instead of return
