
from typing import IO, List

class TestCase():

    def __init__(self: 'TestCase', Hd: None, Ad: None, Hk: None, Ak: None, B: None, D: None) -> None:
        self.Hd: None = Hd
        self.Ad: float = Ad
        self.Hk: float = Hk
        self.Ak: int = Ak
        self.B: int = B
        self.D: int = D
        self.buffRounds: float = 0
        self.debuffRounds: float = 0

    def computeOffRounds(self: 'TestCase') -> float:
        tmp: float = (self.Hk // (self.Ad + (self.buffRounds * self.B)))
        if ((self.Hk % (self.Ad + (self.buffRounds * self.B))) != 0):
            tmp += 1
        return (tmp + self.buffRounds)

    def computeOptBuffRounds(self: 'TestCase') -> None:
        if (self.B == 0):
            self.buffRounds: float = 0
        best: float = self.computeOffRounds()
        self.buffRounds += 1
        while (self.computeOffRounds() <= best):
            best: float = self.computeOffRounds()
            self.buffRounds += 1
        self.buffRounds -= 1

    def computeDefRounds(self: 'TestCase') -> int:
        tmp: int = 0
        rounds: complex = (self.totalOffRounds - 1)
        i: int = 0
        life: int = self.Hd
        damage: int = self.Ak
        lastTimeHeal: object = False
        while (rounds != 0):
            if (life <= damage):
                if ((life > (damage - self.D)) and (i < self.debuffRounds)):
                    lastTimeHeal: object = False
                    i += 1
                    damage -= self.D
                    if (damage < 0):
                        damage: int = 0
                    tmp += 1
                else:
                    if lastTimeHeal:
                        return 10000
                    lastTimeHeal: object = True
                    tmp += 1
                    life: int = self.Hd
            else:
                lastTimeHeal: object = False
                if (i < self.debuffRounds):
                    i += 1
                    damage -= self.D
                    if (damage < 0):
                        damage: int = 0
                    tmp += 1
                else:
                    rounds -= 1
            life -= damage
        return tmp

    def computeOptDebuffRounds(self: 'TestCase') -> None:
        best: int = self.computeDefRounds()
        bestrounds: float = 0
        if ((self.D == 0) or (self.Ak == 0)):
            self.debuffRounds: float = 0
            return
        self.debuffRounds: float = 0
        for i in range((((self.Ak // self.D) + 2) + 1)):
            if (self.computeDefRounds() < best):
                best: int = self.computeDefRounds()
                bestrounds: float = self.debuffRounds
            self.debuffRounds += 1
        self.debuffRounds: float = bestrounds

    def solve(self: 'TestCase') -> str:
        print('Start solving...')
        self.computeOptBuffRounds()
        self.totalOffRounds: complex = self.computeOffRounds()
        print(('Off solved: ' + str(self.totalOffRounds)))
        self.computeOptDebuffRounds()
        self.totalDefRounds: float = self.computeDefRounds()
        print(('Def solved: ' + str(self.totalDefRounds)))
        print(self.debuffRounds)
        if (self.totalDefRounds >= 10000):
            return 'IMPOSSIBLE'
        return str((self.totalOffRounds + self.totalDefRounds))

def loadTestCases(path: str) -> List[TestCase]:
    out: List[TestCase] = []
    input_file: IO = open(path)
    for i in range(int(input_file.readline())):
        (Hd, Ad, Hk, Ak, B, D) = [int(i) for i in input_file.readline().split()]
        print((Hd, Ad, Hk, Ak, B, D))
        out.append(TestCase(Hd, Ad, Hk, Ak, B, D))
    input_file.close()
    return out

def solve(path: str) -> None:
    tcs: List[TestCase] = loadTestCases(path)
    output_file: IO = open((path[:(- 3)] + '.out'), 'w')
    count: int = 1
    for t in tcs:
        output_file.write((((('Case #' + str(count)) + ': ') + str(t.solve())) + '\n'))
        count += 1
    output_file.close()
solve('C-large.in')
