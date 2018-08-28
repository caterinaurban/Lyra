scores: Dict[int, int] = input()     #dictinput()   # id -> score
# previous_ge_10: int = int(input())  # previous results

score_occurrences: Dict[int, int] = {}        # defaultdict(int)    # initialized to 0
for a, b in scores.items():
    if a < 100:     # 'early adopter'
        weight: int = 3
    else:
        weight: int = 1
    if a not in score_occurrences.keys():        # workaround for defaultdict
        score_occurrences[a] = 0
    score_occurrences[a] += weight   # BUG A: should be indexed by b & BUG B: wrong indentation

# scores_gt_10: int = 0
# if previous_ge_10 > 0:
#     scores_ge_10: int = previous_ge_10  # BUG C: scores_ge_10 instead of scores_gt_10

scores_gt_10: int = 0
for k in score_occurrences.keys():
    if k > 10:
        scores_gt_10 += score_occurrences[k]

print(scores_gt_10)
