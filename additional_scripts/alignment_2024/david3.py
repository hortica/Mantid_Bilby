# import mantid algorithms, numpy and matplotlib
from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np

def linspace(start, stop, num):
    r = [0.0] * num
    
    nom = stop - start
    den = num - 1
    for i in range(num): # in 2016 it used to be x-range
        r[i] = start + (i * nom) / den
    return r

def sample(x0, y0, x1):
        import numpy as np        
        
        if len(x0) != len(y0):
            raise Exception("len(x0) != len(y0)")

        x0_min = np.min(x0)
        x0_max = np.max(x0)

        if isinstance(x1, list):
            x1_min = np.min(x1)
            x1_max = np.max(x1)
        else:
            x1_min = x1
            x1_max = x1

        if len(x0) < 2:
            raise Exception("len(x0) < 2")
        if x0_max < x0_min:
            raise Exception("x0_max < x0_min")
        if x1_min < x0_min:
            raise Exception("x1_min < x0_min")
        if x0_max < x1_max:
            raise Exception("x0_max < x1_max")

        i0 = 0
        i1 = 1
        x0i0 = x0[i0]
        y0i0 = y0[i0]
        x0i1 = x0[i1]
        y0i1 = y0[i1]
        
        try:
            _ = iter(x1)
        except TypeError:
            # not iterable
            while x0i1 < x1:
                x0i0 = x0i1
                y0i0 = y0i1

                i1 += 1
                
                x0i1 = x0[i1]
                y0i1 = y0[i1]

            return y0i0 + (x1 - x0i0) * (y0i1 - y0i0) / (x0i1 - x0i0)
            
        else:
            # iterable
            y1 = [0.0] * len(x1)
            for j in range(len(x1)): # x
                x1j = x1[j]
                while x0i1 < x1j:
                    x0i0 = x0i1
                    y0i0 = y0i1

                    i1 += 1
                    
                    x0i1 = x0[i1]
                    y0i1 = y0[i1]

                y1[j] = y0i0 + (x1j - x0i0) * (y0i1 - y0i0) / (x0i1 - x0i0)

            return y1

def normxcorr(s, k):
              
        sLen = len(s)
        kLen = len(k)
        cLen = sLen + kLen - 1

        c = [0.0] * cLen
        
        for i in range(cLen): #x
            j0 = i - (kLen - 1) if i >= kLen - 1 else 0
            jN = i + 1 if i < sLen - 1 else sLen

            s1Sum = 0.0
            s2Sum = 0.0

            k1Sum = 0.0
            k2Sum = 0.0

            skSum = 0.0

            n = jN - j0
            
            for j in range(j0, jN): #x
                sVal = s[j    ]
                kVal = k[i - j]

                s1Sum += sVal
                s2Sum += sVal * sVal
                
                k1Sum += kVal
                k2Sum += kVal * kVal

                skSum += sVal * kVal

            nom  = skSum - s1Sum * k1Sum / n
            denS = s2Sum - s1Sum * s1Sum / n
            denk = k2Sum - k1Sum * k1Sum / n
            den  = np.sqrt(denS * denk)

            if den > 1e-5 * np.abs(nom):
                c[i] = nom / den

        return c

def localmaxima(x, y):
        if len(x) != len(y):
            raise Exception("len(x) != len(y)")
        if len(x) < 3:
            raise Exception("len(x) < 3")
        
        # return list of tuples (x, y, i)
        result = []

        y1 = y[0]
        y2 = y[1]
        for i2 in range(2, len(y)): #x
            y0 = y1
            y1 = y2
            y2 = y[i2]

            if (y0 < y1) and (y1 > y2):
                result.append((x[i2 - 1], y1, i2 - 1))
            
        return result
    
def maximumX(x, y, i):
                
        x0 = x[i - 1]
        x1 = x[i    ]
        x2 = x[i + 1]
        
        y0 = y[i - 1]
        y1 = y[i    ]
        y2 = y[i + 1]
        
        y10 = y1 - y0
        y20 = y2 - y0
        
        return -0.5 * ((x2*x2 - x0*x0)*y10 - (x1*x1 - x0*x0)*y20) / ((x1 - x0)*y20 - (x2 - x0)*y10)