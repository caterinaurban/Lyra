
important: Set[str] = {"Albert Einstein" , "Alan Turing"}
texts: Dict[str, str] = input() # {"<author >" : "<t e x t >"}

freqdict: Dict[str, int] = {}     # defaultdict(int)  err: int recognized as varId  #initialized to 0
a: str = ""     #necessary?
b: str = ""
for a, b in texts.items():
    if a in important:     #texts of important authors weighted twice
        weight: int = 2
    else:
        weight: int = 1
        words: List[str] = a.split()      #Bug A: Should be `b' (values)
        for word in words:     #and Bug B: Wrong indentation
            word: str = word.lower()
            freqdict[word]: int = freqdict[word] + weight
print(freqdict)         #outputs <word>:<count>, ...