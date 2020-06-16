import os

print(os.getcwd())

print (os.path.dirname(os.path.realpath(__file__)) )


test = os.getcwd()

test2 = test.split('/')[-1]

print(test2)
