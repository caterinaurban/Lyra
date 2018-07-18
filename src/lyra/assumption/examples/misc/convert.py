def convertToKilograms(weight_str):
  result = weight_str.split()
  if(len(result)) != 2:
    return 0
  try:
    number = float(result[0])
  except ValueError:
    return 0
    
  if(result[1] == 'pounds' or result[1] == 'lb' or result[1] == 'lbs'):
    return number * 453.592 * 1e-3
  elif(result[1] == 'ounces' or result[1] == 'oz' or result[1] == 'oz.'):
    return number * 28.35 * 1e-3
  elif(result[1] == 'grams' or result[1] == 'gms' or result[1] == 'g'):
    return number * 1e-3
  elif(result[1] == 'kilograms' or result[1] == 'kilo' or result[1] == 'kg'):
    return number
  else:
    raise ValueError

a = ['pounds', 'lb', 'lbs', 'ounces', 'oz', 'oz.', 'grams', 'gms', 'g', 'kilograms', 'kilo', 'kg']
u = set()
for s in a: 
  u = u.union(set(s))
print(u)
