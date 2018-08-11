scores: Dict[int, int] = input()     #dictinput()   # id -> score

# total_score = 0
# max_score = 0
# a: int = 0
# b: int = 0
# for a,b in scores.items():
#     if a < 100:     # 'early adopter'
#         weight = 3
#     else:
#         weight = 1
#         total_score += weight * a
#     if a > max_score:
#         max_score = a


score_occurences: Dict[int,int] = {}        # defaultdict(int)    # initialized to 0
for a,b in scores.items():
    if a < 100:     # 'early adopter'
        weight: int = 3
    else:
        weight: int = 1
        if a not in score_occurences.keys():        # fix for defaultdict
            score_occurences[a] = weight
        score_occurences[a] += weight   # BUG A: should be indexed by b & BUG B: wrong indentation

scores_gt_10: int = 0
for k in score_occurences.keys():
    if k > 10:
        scores_gt_10 += score_occurences[k]

print(scores_gt_10)