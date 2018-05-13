col_indices: Dict[str, int] = input()
items: List[str] = input()

bx_ids: Dict[str,str] = {}      # or other type
key: str = ""
# items[col_indices.values()] -> U
for key in col_indices.keys():
    # items[col_indices[key]]-> U
    bx_ids[key]: str = items[col_indices[key]]
print(bx_ids)
