## INITIALISER LES 2 LISTES
reel = fusion(acc, dev, 406, 455, 0.05)
theo = th(trace, 406, 455, 0.05, reel, k_raid = 201000)


## AFFICHAGE DES VALEURS BRUTES SNCF
def aff_dev_prat(dev, pkd = 0, pkf = 1e10):
    X = []
    Y = []
    dbt, fin = bornes(dev, pkd, pkf)
    for k in range(dbt, fin + 1): 
        X.append(dev[k][0])
        Y.append(dev[k][1]/1435 * 180/np.pi)
    plt.plot(X, Y)
    plt.title("Expérience : dévers mesuré entre les PK " + str(int(np.floor(pkd))) + " et " + str(int(np.ceil(pkf))), fontsize = 20)
    plt.xlabel("Point Kilométrique (km)", fontsize = 16)  
    plt.ylabel("Dévers mesuré (en degrés)", fontsize = 16)     
            
def aff_acc_prat(acc, pkd = 0, pkf = 1e10):
    X = []
    Acc = []
    V = []
    dbt, fin = bornes(acc, pkd, pkf)
    for k in range(dbt, fin + 1):   
        X.append(acc[k][0])
        Acc.append(acc[k][3])
        V.append(acc[k][1])      # en km/h !!  
    plt.figure()
    plt.plot(X, Acc) 
    plt.title('Expérience : accélération latérale mesurée', fontsize = 20)
    plt.xlabel("Point Kilométrique (km)", fontsize = 16)  
    plt.ylabel("Accélération latérale (m/s²)", fontsize = 16)  
    plt.figure()  
    plt.plot(X, V)
    plt.legend()
    plt.title("Expérience : vitesse mesurée du train", fontsize = 20)
    plt.xlabel("Point Kilométrique (km)", fontsize = 16)  
    plt.ylabel("Vitesse (m/s)", fontsize = 16)  
    
## AFFICHER LES VALEURS BRUTES :
# aff_dev_prat(dev, pkd = 406, pkf = 455)
# aff_acc_prat(acc, pkd = 406, pkf = 455)    # affiche l'accélération et la vitesse
 
 
## TESTER DIFFERENTS INTERVALLES           
def pour100_courbe(trace, pkd, pkf):
    dbt, fin = bornes(trace, pkd, pkf, m=1)  
    r = 0   # rayon cumulé
    dev = 0 # devers cumulé
    lcourbe = 0
    v = 0
    for k in range(dbt, fin + 1): 
        dl = trace[k][1] - trace[k][0]
        lcourbe += dl * abs(trace[k][3])   # sens = 0 quand tourne pas
        r += trace[k][4] * dl
        dev += trace[k][5] * dl
    l = trace[fin][1]-trace[dbt][0]
    return l/1000, lcourbe/1000, round(r/l), round((dev * 180 / (1345 * np.pi)) / l, 2)  # longueur, longueur en courbe, pourcentage de courbe, dev en °

def v_moy(acc, pkd, pkf):
    dbt, fin = bornes(acc, pkd, pkf)  
    v = 0
    for k in range(dbt, fin + 1): 
        dl = acc[k+1][0] - acc[k][0]
        v += acc[k][1] * dl
    l = acc[fin][0]-acc[dbt][0]
    return v/l  # dev en °
    
## OPTIMISATION DU MODELE DE VITESSE
import scipy.optimize as opt

def Acce(th, ord):
    Y = []
    for ligne in th:
        Y.append(ligne[ord])
    return Y

def Acce_opt(X, c, k = 233600, d=0):  # abcisses, coef dilatation
    return Acce(th(trace, PKdbt, PKfin, 0.05, reel, a = c, b = d, k_raid = k), 5)

X = Acce(th(trace, PKdbt, PKfin, 0.05, reel, a = 1, b = 0), 0)    # les PK
Acce_temoin = Acce(th(trace, PKdbt, PKfin, 0.05, reel, a = 1, b = 0), 3)    # pour le témoin, pas de pendulation => on s'en fiche de k_raid
v_moy = v_moy(acc, PKdbt, PKfin)  
    
# OPTIMISATION EN LOI LINEAIRE
def opt_line():
    [a] = opt.curve_fit(Acce_opt, X, Acce_temoin, [1.13])[0]
    return a * v_moy, v_moy, a

# OPTIMISATION EN LOI AFFINE   (a * V + b en km/h)
def opt_affine():
    [a, b] = opt.curve_fit(Acce_opt, X, Acce_temoin, [1.13, 0])[0]
    return a*v_moy + b, v_moy, a, b

# TESTER SUR D'AUTRES TRONCONS EN ACTUALISANT 2 FOIS (car en bas de page)
PKdbt = 406
PKfin = 455

# FAIRE UNE OPTIMISATION :
# changer k directement dans la fonction Acce_opt
# juste faire opt_line() 

