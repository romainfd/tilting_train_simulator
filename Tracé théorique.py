#### ATTENTION !!!!!!!!!!!!!!!!!!!!!!
# Il faut aller dans le dossier avec les fichiers puis faire étoile et aller dans ce dossier (shell courant)  !!!!!!!!!!!!
PKdbt = 406
PKfin = 455

## FICHIERS UTILISES
# TraceM : PK1,	PKF,	distance,	SENS,	RaYON,	DEVERS(mm),	dev (rad)
# TraceTest : deux virages après PK 430

## ZONE ETUDIEE
# pk de 406 à 455

## APPELS DE FONCTIONS
# tracer : tracer(trace, 406, 455, 1, 0, epaisseur = 3)
# vitesse et accélération fction du temps et temps total : tps(trace, 406, 455, v_confort, 120/3.6, 1)

import scipy.io as sio
import matplotlib.pyplot as plt
import numpy as np
from numpy import cos, sin
g = 9.81

LT = [i for i in range(10)]     #liste test


# ouverture du fichier Excel 
# convertir un fichier excel
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
  
# TRACE SNCF
trace = excel('traceMF - RP.csv')
for c in '12345678':
    num(trace, int(c)-1)      # -1 à case du décalage des indices python

# TRACE TEST : virage vers PK430 +
traceTest = excel('traceTest - RP.csv')
for c in '1234568':
    num(traceTest, int(c)-1)      # -1 à case du décalage des indices python
    
def dichotomie(l, val):    #retourne la paire d'indice des valeurs encadrant val dans la liste l
    a = 0
    b = len(l) - 1
    while b - a > 1:
        m = (a + b) // 2
        if l[m] > val :
            b = m
        else:
            a = m
    return a, b

def dichotomie_c(l, val, c):   # encadre par rapport à la colonne c (qui doit être triée)
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
    
# Avancer d'un petit tronçon de longueur pas
def avancement(pos, pas, eps, R):    # pos = (angle, x, y)
    a = pos[0]
    x = pos[1] + pas*cos(a)
    y = pos[2] + pas*sin(a)
    if R == 0:
        return (a, x, y)      # l'angle ne change que s'il y a un rayon
    else:
        a -= eps * pas/R      # pour coller avec la réalité : -1
        return (a, x, y)      # angle (pour le suivant) et coordonnées (pour ploter)

# Tracer tous les tronçons
def tracer(trace, pkd, pkf, pas, a0, leg = 0, epaisseur = 2):
    dbt, fin = bornes(trace, pkd, pkf, m=1)
    pos = [(a0, 0, 0)]
    for sec in range(dbt, fin + 1):   # toutes les sections
        posSec = [pos[-1]]
        d = trace[sec][2]
        eps = trace[sec][3]    # à gauche ou à droite
        R = trace[sec][4]
        for i in range(int(d//pas)):    # tracer sur toute la longueur du tronçon
            posSec.append(avancement(posSec[-1], pas,eps, R)) 
        posSec.append(avancement(posSec[-1], d%pas, eps, R))
        X, Y = [], []
        for i in range(len(posSec)):
            X.append(posSec[i][1])
            Y.append(posSec[i][2])        
        plt.plot(X, Y, label = 'PK {} à PK {}'.format(trace[sec][0]/1000, trace[sec][1]/1000), linewidth = epaisseur)
        del posSec[0]    # déjà pris avec la section d'avant
        pos += posSec
    if leg == 1:
        plt.legend(loc = 'best')
    plt.axis('equal')

## TEMPS DE TRAJET

# 1) VITESSE
def v_confort(R, dev):
    return np.sqrt(R * g * dev)
    
def v_max(R, dev, A_lat_max = 1.2):
    return np.sqrt(R*(A_lat_max + g*dev))
    
def v_cste(R, dev, v= 120/3.6):
    return v
    
def tps(trace, pkd, pkf, fct_v, vDroit, aff = 0):  # temps de trajet avec une fonction de vitesse précise
    dbt, fin = bornes(trace, pkd, pkf)
    temps = 0
    V = []
    T = []
    A = []
    for sec in range(dbt, fin + 1):
        distance = trace[sec][2] 
        R = trace[sec][4]
        dev = trace[sec][6]/1000000
        if R == 0 or dev < 10/1435:
            v = vDroit
            aLat = 0
        else:
            if dev ==0:
                print(sec)
            v = fct_v(R, dev)
            aLat = (- g * dev + v*v/R)*100
        V.append(v*3.6)
        T.append(temps)
        A.append(aLat)
        temps += distance / v
        V.append(v*3.6)
        T.append(temps)
        A.append(aLat)
        if v*3.6<75:
            print(sec)
    if aff == 1:
        plt.plot(T, V)
        plt.plot(T, A)
    return temps
        
def T_V(trace, pkd, pkf):
    V = [v for v in range(60, 300, 10)]
    T = [tps(trace, pkd, pkf, v/3.6) for v in V]
    plt.plot(V, T)
        