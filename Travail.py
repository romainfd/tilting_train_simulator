def alphaMax(trace, pkd, pkf, pas, reel, a = 1, b = 0, k_raid = 3.6e5):   # en degrés
    nbL = len(reel)
    V = vit(reel, a = a, b = b)
#    reel = fusion(acc, dev, pkd, pkf, pas)
#    nbL = len(fusion(acc, dev, pkd, pkf, pas))
    th = []
    dbt, fin = bornes(trace, pkd, pkf, m=1)
    pk = pkd
    max, PKmax = 0, 0 # angle max de pendulation et PK où atteint
    tps = 0
# déterminer cbn de fois on répète chaque truc
    k = dbt
    for i in range(nbL):
        R = trace[k][4]
        devr = - trace[k][3] * trace[k][6] / 1000000   # sens * dev
        v = V[i][1]                    ## EN M/S  !!!!!!!!!!!
        tps += pas*1000/v
        if R != 0:
            pend = dev_p(v, trace[k][6] / 1000000, h=1.1, R = R, M = 50000, d = 1, k = k_raid) 
            if abs(trace[k][6]/1000000 + pend) > max:
                max, PKmax =  abs(trace[k][6]/1000000 + pend), trace[k][0]/1000
            ATB = trace[k][3] * (- g * (trace[k][6]/1000000) + v*v/R)
            AVB = trace[k][3] * (- (v*v/R) * trace[k][6] / 1000000)  # prend pas le poids
            ATC = trace[k][3] * (- g * (trace[k][6]/1000000 + pend) + v*v/R)
            AVC = trace[k][3] * (- g - v*v/R * devr) + g  
        else:
            pend = 0
            ATB = 0
            AVB = 0
            ATC = 0
            AVC = 0
        while trace[k+1][0]/1000 <= pk:
            k += 1
        pk += pas
    return max/(np.pi)*180, PKmax    # retourne l'angle de pendulation en degré