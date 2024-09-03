import pickle
import sys

ff=sys.argv[1]

cpu=pickle.load(open(ff,'rb'))
print(cpu)