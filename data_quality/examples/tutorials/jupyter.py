# http://nbviewer.jupyter.org/gist/manujeevanprakash/138c66c44533391a5af1

import numpy as np
import matplotlib.pyplot as plt

ghj = [5, 10 ,15, 20, 25]
it = [1, 2, 3, 4, 5]
# MAD: len(ghj) == len(it)
plt.bar(ghj, it)
plt.show()

# ----------------------

new_list = [[5., 25., 50., 20.], [4., 23., 51., 17.], [6., 22., 52., 19.]]
x = np.arange(4)
# MAD: len(new_list) > 0
# MAD: len(x) == len(new_list[0])
plt.bar(x + 0.00, new_list[0], color ='b', width =0.25)