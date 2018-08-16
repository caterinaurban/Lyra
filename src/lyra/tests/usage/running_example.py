scores: Dict[int, int] = input()     #dictinput()   # id -> score

score_occurences: Dict[int,int] = {}        # defaultdict(int)    # initialized to 0
for a,b in scores.items():
    a = a
    if a < 100:     # 'early adopter'
        weight: int = 3
    else:
        weight: int = 1
        if a not in score_occurences.keys():        # workaround for defaultdict
            score_occurences[a] = 0
        score_occurences[a] += weight   # BUG A: should be indexed by b & BUG B: wrong indentation

scores_gt_10: int = 0
for k in score_occurences.keys():
    if k > 10:
        scores_gt_10 += score_occurences[k]

print(scores_gt_10)
