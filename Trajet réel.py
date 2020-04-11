## APPELS DE FONCTIONS
# avoir la plage de données du virage (moyennée sur une longueur = pas) :
# PK moyen, vitesse, temps, ATB, AVB, ATC, AVC, devers (radians):
# fusion(acc, dev, pkd, pkf, pas)
# reel = fusion(acc, dev, 406, 455, 0.05)

# theo = th(trace, pkd, pkf, pas, reel)
# theo = th(trace, 406, 455, 0.05, reel, k_raid = 201000)


# afficher les 2 dévers:
# aff(theo, reel, 0, 7, 7)

# afficher l'angle de pendulation
# aff1(theo, 0, 8, 50)

## COMPARAISON DES DEVERS
# reel = fusion(acc, dev, 406, 455, 0.05)
# theo = th(trace, 406, 455, 0.05, reel)
# aff(theo, reel, 0, 7, 7, "Validation du modèle : dévers", "Point Kilométrique (km)", "Angle de dévers (rad)", "Devers du tracé théorique", "Dévers mesuré")


import scipy.io as sio
import matplotlib.pyplot as plt
import numpy as np
from numpy import cos, sin
g = 9.81

import matplotlib.pyplot as plt
import numpy as np
from numpy import cos, sin
g = 9.81

LT = [i for i in range(10)]     #liste test

## OPERATEURS SUR LES LISTES, terme à terme

def somme(l1, l2):
    return [l1[i] + l2[i] for i in range(len(l1))]
    
def prod(l1, x):
    return [x*l1[i] for i in range(len(l1))]
    

## ouverture du fichier Excel 
## convertir un fichier excel
def excel(fichier):
    f = open(fichier)
    lignes = f.readlines()
    f.close()
    tab = []
    for l in lignes:
        l=l.split(';')
        del l[-1]
        tab.append(l)
    del(tab[0])
    tab.sort()
    return tab
  
def num(l, c):  #  int la colonne c de la liste l
    for i in range(len(l)):
        l[i][c] = int(l[i][c])
        
def flt(l,c):
    for i in range(len(l)-1):
        l[i][c] = float(l[i][c])
  
lTest = [[i, i+1] for i in range(10)]

# DEVERS SNCF
dev = excel('devers - RP.csv')
for c in '12':
    flt(dev, int(c)-1)      # -1 à case du décalage des indices python
    
# ACCELERATION SNCF
acc = excel('acceleration - RP.csv')
for c in '1234567':
    flt(acc, int(c)-1)      # -1 à case du décalage des indices python


## AFFICHAGE DES VALEURS BRUTES SNCF
def aff_dev_prat(dev):
    X = []
    Y = []
    for k in range(len(dev)):
        X.append(dev[k][0])
        Y.append(dev[k][1])
    plt.plot(X, Y)
           
def aff_acc_prat(acc):
    X = []
    Acc = []
    V = []
    for k in range(len(acc)):
        X.append(acc[k][0])
        Acc.append(acc[k][3])
        V.append(acc[k][1])      # en km/h !!  
    plt.plot(X, Acc, label = 'Accélération latérale mesurée') 
    plt.figure()  
    plt.plot(X, V, label='vitesse')
    plt.legend()
    
## AFFICHER LES VALEURS BRUTES SNCF :
# aff_dev_prat(dev)
# aff_dev_prat(acc)    # affiche l'accélération et la vitesse
    
## EXTRACTION DES INTERVALLES INTERESSANTS
def dichotomie_c(l, val, c):   # encadre par rapport à la colonne c (qui doit être triée
    a = 0
    b = len(l) - 1
    while b - a > 1:
        m = (a + b) // 2
        if l[m][c] > val :
            b = m
        else:
            a = m
    return a, b
    
def bornes(trace, pkd, pkf, m = 0):     # m = 1 si dans trace les pk sont en metres
    dbt = dichotomie_c(trace, pkd*(1+999*m), 0)[0]
    fin = dichotomie_c(trace, pkf*(1+999*m), 0)[1]
    return dbt, fin
    
def extrait(l, pkd, pkf):
    dbt, fin = bornes(l, pkd, pkf)
    return l[dbt: fin]   
        
    
## MOYENNAGE DES DONNEES POUR LIMITER LE NB DE LIGNES    
    
def lissage(l, pas):
    liss = []
    c = 0
    pk0 = l[0][0]
    moy = [0]*len(l[0])
    for ligne in l:
        if ligne[0] - pk0 < pas:
            moy = somme(moy, ligne)
            c += 1
        else:
            moy = prod(moy, 1/(c+1))   
            liss.append(moy)
            pk0 += pas
            c = 0
            moy = ligne
    return liss
        

## FUSION DES DEUX TABLEAUX
    
def fusion(acc, dev, pkd, pkf, pas):    #  dévers ajouté en radians
    acc_v = extrait(acc, pkd, pkf)
    dev_v = extrait(dev, pkd, pkf)
    acc_v_l = lissage(acc_v, pas)
    dev_v_l = lissage(dev_v, pas)
    n = min(len(acc_v_l), len(dev_v_l))
    fus = []
    t0 = acc_v_l[1][2]
    for i in range(n):
        fus.append(acc_v_l[i] + [dev_v_l[i][1] / 1435])    # on reprend pas le pk, et on ajoute le devers en radians
# départ à zéro de l'échelle des temps qui à été retourné par le sort() sur la première ligne, d'où le moins:
        fus[i][2] = t0 - fus[i][2]
    return fus
    

## CREATION DU MEME TABLEAU THEORIQUE
# EN K/H !!! dans reel
def vit(reel, a = 1, b = 0):   # vitesse réelle transformée affine : en m/s
    vit = [] 
    for ligne in reel:
        vit.append([ligne[0], (a * ligne[1] + b)/3.6])   # on a joute le pk et la vitesse correspondant (en m/s)
    return vit

## Crée un tableau avec les valeurs théoriques mais basées sur la vitesse réelle
def th(trace, pkd, pkf, pas, reel, a = 1, b = 0, k_raid = 3.6e5):  
    nbL = len(reel)
    V = vit(reel, a = a, b = b)  # en m/s
#    reel = fusion(acc, dev, pkd, pkf, pas)
#    nbL = len(fusion(acc, dev, pkd, pkf, pas))
    th = []
    dbt, fin = bornes(trace, pkd, pkf, m=1)
    pk = pkd
    tps = 0
# déterminer cbn de fois on répète chaque truc
    k = dbt
    for i in range(nbL):
        R = trace[k][4]
        devr = - trace[k][3] * trace[k][6] / 1000000   # sens * dev
        v = V[i][1]                    ## EN M/S  !!!!!!!!!!!
        tps += pas*1000/v
        if R != 0:
            pend = -trace[k][3]*dev_p(v, trace[k][6] / 1000000, h=1.1, R = R, M = 50000, d = 1, k = k_raid) 
            ATB = trace[k][3] * (- g * (trace[k][6]/1000000) + v*v/R)
            AVB = trace[k][3] * (- (v*v/R) * trace[k][6] / 1000000)  # prend pas le poids
            ATC = trace[k][3] * (- g * (trace[k][6]/1000000 + abs(pend)) + v*v/R)
            AVC = trace[k][3] * (- g - v*v/R * devr) + g  
        else:
            pend = 0
            ATB = 0
            AVB = 0
            ATC = 0
            AVC = 0
        th.append([pk, v*3.6, tps, ATB, AVB, ATC, AVC, devr, pend])   #avec pend en rad
        while trace[k+1][0]/1000 <= pk:
            k += 1
        pk += pas
    return th
    
## AFFICHAGE DES COLONNES DE CERTAINES TABLES
def aff(l1, l2, abs, ord1, ord2, titre, labelX, labelY, label1, label2):
    X =[]
    Y1 = []
    Y2 = []
    for ligne in l1:
        X.append(ligne[abs])
        Y1.append(ligne[ord1])
    for ligne in l2:
        Y2.append(ligne[ord2])
    plt.plot(X, Y1, label = label1)
    plt.plot(X, Y2, label = label2)
    plt.title(titre, fontsize=20)
    plt.xlabel(labelX, fontsize=16)
    plt.ylabel(labelY, fontsize=16)
    plt.legend(fontsize = 16)
    return X

def aff1(l1, abs, ord1, pas):
    X =[]
    Y1 = []
    for ligne in l1:
        X.append(ligne[abs])
        Y1.append(ligne[ord1])
    plt.plot(X, Y1, label = pas)
    plt.legend()

def aff_echelle(l1, l2, abs, ord1, a, b, ord2):   # a*(x + b) sur la 1ere coord
    X =[]
    Y1 = []
    Y2 = []
    for ligne in l1:
        X.append(ligne[abs])
        Y1.append((ligne[ord1] + b) * a)
    for ligne in l2:
        Y2.append(ligne[ord2])
    plt.plot(X, Y1, label = 'Accélération avec le tracé théorique')
    plt.plot(X, Y2, label = 'Accélération mesurée')
    plt.title('Validation du modèle : accélérations à la vitesse réelle')
    plt.legend()
    return X


## VALIDATION DU MODELE EN ACCELERATION
## prendre un pas vers 275 m si on prend les 2 en ATB
# reel = fusion(acc, dev, 406, 455, 0.275)
# aff(th(trace, 406, 455, 0.275, reel), reel, 0, 3, 5, "Validation du modèle : accélération à la vitesse réelle", "Point Kilométrique (km)", "Accélération latérale ressentie par le passager en caisse (m/s²)", "Accélération avec le tracé théorique", "Accélération mesurée")

## avec l'ATC : pas de 50m:
# reel = fusion(acc, dev, 406, 455, 0.05)
# aff(th(trace, 406, 455, 0.05, reel), reel, 0, 3, 5)

# COMPARER DIFFERENTS PAS :
# for i in range(10, 110,10):
#    reel = fusion(acc, dev, 406, 455, i/1000)
#    aff(th(trace, 406, 455, i/1000, reel), reel, 0, 3, 5)
#    plt.figure()



## ANGLE DE PENDULATION:
# v en m/s, dev en rad et renvoit dev_p en rad
def dev_p(v, dev, h=1.1, R = 1200, M = 50000, d = 1, k = 3.6e5):     
    return (-(dev*h*M*g+(dev*0.6*M-R*h*M)*v*v/(R*R))/(2*d*d*k + h*M*g + 0.6*M*v*v/(R*R)))
    
## AFFICHAGE DE LA PENDULATION AVEC LE REEL:
# reel = fusion(acc, dev, 406, 455, 0.05)
# aff(th(trace, 406, 455, 0.05, reel, a = 1, b = 0), reel, 0, 3, 5)

## AFFICHAGE DE LA PENDULATION AVEC LE THEORIQUE
# reel = fusion(acc, dev, 406, 455, 0.05)
# theo = th(trace, 406, 455, 0.05, reel, a = 1, b = 0)
# plt.title("Simulation de l’accélération avec et sans pendulation : amélioration du confort", fontsize = 20)
# plt.xlabel("Point Kilométrique (km)", fontsize = 16)  
# plt.ylabel("Accélération ressentie en caisse (m/s²)", fontsize = 16)  
# aff_th(theo, 0, 3, "Accélération du modèle témoin")
# aff_th(theo, 0, 5, "Accélération du modèle avec pendulation")

    
## GAIN PENDULATION
def aff_th(th, abs, ord, leg):
    X =[]
    Y = []
    for ligne in th:
        X.append(ligne[abs])
        Y.append(ligne[ord])
    plt.plot(X, Y, label = leg)
    plt.legend(fontsize = 16)

## COMPARAISON DES THEORIQUES POUR DIFFERENTES VITESSES:
# aff_th(th(trace, 406, 455, 0.05, reel, a = 1, b = 0), 0, 5, 'label')
# et jouer sur v = a*v_reel + b
# témoin (il faut prendre ATB): aff_th(th(trace, 406, 455, 0.05, reel, a = 1, b = 0), 0, 3, 'témoin')   
# puis faire plt.legend() et plt.title("fbrcubueb")

## AFFICHAGE ANGLE DE PENDULATION
def aff_pend(th, abs, leg):
    X =[]
    Y = []
    for ligne in th:
        X.append(ligne[abs])
        Y.append(ligne[8]/(np.pi)*180)
    plt.plot(X, Y, label = leg)
    plt.legend(fontsize = 16) 
    
# POUR DIFFERENTS K:
# reel = fusion(acc, dev, 406, 455, 0.05)
# theo = th(trace, 406, 455, 0.05, reel, k_raid = 150000)
# k_test = 200000
# theo = th(trace, 406, 455, 0.05, reel, k_raid = k_test)
# aff_pend(theo, 0, 'Angle de pendulation')
# plt.title('Angle de pendulation de la caisse en degré pour k = {}'.format(k_test))
# plt.xlabel('Point kilométrique (PK)')
# plt.ylabel('Angle de pendulation (°)')
# plt.plot([406, 455], [3.44, 3.44], color = 'red', label = 'Angle de pendulation limite')
# plt.plot([406, 455], [-3.44, -3.44], color = 'red')

# légère modif de trace pour retourner la pendulation max
# PendMax(trace, 406, 455, 0.05, reel, a = 1, b = 0, k_raid = 201000)
def PendMax(trace, pkd, pkf, pas, reel, a = 1, b = 0, k_raid = 3.6e5):   # en degrés
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
            if abs(pend) > max:
                max, PKmax = abs(pend), trace[k][0]/1000
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
    
def determination_ressort(angle_pendMax, k0, pas, a = 1, b = 0):  ##angle_pendMax en degrés
    k = k0
    (max, PKmax) = PendMax(trace, PKdbt, PKfin, 0.05, reel, a = a, b = b, k_raid = k)
    while max - angle_pendMax < 0:
        k -= pas         #il faut dimuner k pour augmenter l'angle
        (max, PKmax) = PendMax(trace, PKdbt, PKfin, 0.05, reel, k_raid = k)
    return k
    
# determination_ressort(3.44, 250000, 1000, a = 1, b = 0)