from functools import reduce
x=reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])
print(x)