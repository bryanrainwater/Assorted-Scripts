#### MIE generator ####
# Creates "mie.c" file with 65536 entries, corresponding to the lookup values

# Python table creation
# use "python3 table_creation.py > mie.c"
import numpy as np

print('#include "sqrttbl.h"')
print('unsigned int SQRTTBL[4194304] = {')
#print('#include "mie.h"')
#print('unsigned int MIE[65536] = {')

# Diam = n*c*sqrt(((200*V/Vmax) - a)*f)
# V = V_max * bit / bit_scale
# When bit > 16*bit_scale/200 a = 5.7, otherwise a = 0.8

n = 1.3
c = 84.0
f = 10.0 #LPM
Vmax = 2.0/2.0
bit_scale = 65536.0/2.0

'''
for i in range(65536):
    if i < 16.0*bit_scale/200.0:
        d = n*c*np.sqrt(((200.0*float(i)/bit_scale) + 1.0 - 0.8 )*f)
        d = int(np.round(d))
        print(d, ",")
    elif i == 65535:
        d = n*c*np.sqrt(((200.0*float(i)/bit_scale) + 1.0 - 5.7 )*f)
        d = int(np.round(d))
        print(d) #No trailing comma on last element
    else:
        d = n*c*np.sqrt(((200.0*float(i)/bit_scale) + 1.0 - 5.7 )*f)
        d = int(np.round(d))
        print(d, ",")
print('};')
''' 

#for i in range(65536):
for i in range(4194304):
    if i<4194303: #65535
        #print(int(np.round(np.sqrt(i))),",")
        print(int(np.round(np.sqrt(i))),",")
    else:
        print(int(np.round(np.sqrt(i))))    
print('};')

