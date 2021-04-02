import scipy
from scipy.stats import expon, boltzmann
import math
import datetime
import matplotlib.pyplot as plt
import numpy as np

#10 ans en jours
ten_years = 10 * 365.25

def pref_lambda(p=0.5,value=10):
    "donne lambda en fonction du percentile visé, value en année, retourne des jours"
    days = 10 * 365.25
    return -math.log(1-p)/days

def get_scale(lam):
    return 1/lam

#Fonctions de plot
def draw_exp(p=0.5,value=ten_years):
    fig,ax=plt.subplots(1,1)
    xlim = 80*365.25
    x = np.linspace(0,xlim,num=200)
    ax.plot(x,expon.pdf(x,scale=1/pref_lambda(p,value)))
    ymax=expon.pdf(0,scale=1/pref_lambda(p,value))
    ax.vlines(value,0,ymax,label='percentile: {}'.format(p))
    ax.legend()
    plt.show

#Ecriture de la fonction principale : à partir d'un scale, on fait un tirage de jours
# on convertir ces jours en date du passé, ce qui donne une année ce qui donne une catégorie

def tirage_jours(scale):
    return expon.rvs(scale=scale)

def jours2an(jour):
    past_date = datetime.date.today()-datetime.timedelta(days=jour)
    return past_date.year

def an2cat(an):
    if an >= 2010:
        return an
    elif an >= 1960:
        return an // 10 * 10
    else:
        return 1950


# Ecriture des fonctions pour le choix du classement
#D'abord une fonction pour définir la préférence

#choix du k en fonction de la catégorie

def N_from_cat(cat):
    if cat==1950:
        return 50
    else:
        return 100

def pref_lambda_boltzmann(prob=0.5,place=20,N=100):
    """retourne un lambda pour lequel le tirage du top "place" est prob"""
    a=10
    b=1/(10*N)
    res=scipy.optimize.brentq(lambda x:boltzmann.cdf(place-1,x,N)-prob,a,b)
    return res

def tirage_classement(lambda_,N):
    return 1+boltzmann.rvs(lambda_=lambda_,N=N)

def bouton_magique(p1=0.5,v1=10,p2=0.5,v2=20):
    """donne un couple classement / catégorie
    p1 : percentile pour le tirage de l'année
    v1 : valeur pour le tirage de l'année
    p2 : percentile pour le tirage du classement
    v2 : valeur pour le tirage du classement
    """
    categorie = an2cat(jours2an(tirage_jours(1/pref_lambda(p1,v1))))
    N = N_from_cat(categorie)
    classement = tirage_classement(pref_lambda_boltzmann(p2,v2,N),N)
    return categorie , classement


#Maintenant faut que je fasse un scraper de senscritique...

