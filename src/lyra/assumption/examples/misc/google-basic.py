def fix_start(s):
  # +++your code here+++
  # LAB(begin solution)
  front = s[0]
  back = s[1:]
  fixed_back = back.replace(front, '*')
  return front + fixed_back
  # LAB(replace solution)
  # return
  # LAB(end solution)