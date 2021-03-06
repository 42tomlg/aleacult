import scipy
from scipy.stats import expon, boltzmann, truncexpon
import math
import datetime
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup
import requests
import json

#10 ans en jours
ten_years = 10 * 365.25

def pref_lambda(p=0.5,value=10):
    "donne lambda en fonction du percentile visé, value en année, retourne des jours"
    days = value * 365.25
    return -math.log(1-p)/days

def get_scale(lam):
    return 1/lam

def days_from_date(day=1,month=1,year=1950):
    delta= datetime.date.today() - datetime.date(year=year,month=month,day=day)
    return delta.days

D_max_album = days_from_date()

#Fonctions de plot
def draw_exp(p=0.5,value=10):
    fig,ax=plt.subplots(1,1)
    xlim = 80*365.25
    x = np.linspace(0,xlim,num=200)
    ax.plot(x,expon.pdf(x,scale=1/pref_lambda(p,value)))
    ymax=expon.pdf(0,scale=1/pref_lambda(p,value))
    ax.vlines(value*365.25,0,ymax,label='percentile: {}'.format(p))
    ax.legend()
    plt.show

#Ecriture de la fonction principale : à partir d'un scale, on fait un tirage de jours
# on convertir ces jours en date du passé, ce qui donne une année ce qui donne une catégorie

def tirage_jours(lambda_,genre="albums"):
    if genre == "albums":
        b = D_max_album
    return boltzmann.rvs(lambda_,N=b)

def jours2an(jour):
    past_date = datetime.date.today()-datetime.timedelta(days=jour)
    return past_date.year

def an2cat(an):
    if an >= 2000:
        return an
    elif an >= 1960:
        return an // 10 * 10
    else:
        return 1950

def get_xs():
    "renvoie les coordonnées en fonction du jour actuel"
    this_year=datetime.date.today().year
    debut = [i for i in range(this_year,1999,-1)]
    fin = [1990,1980,1970,1960,1950]
    return debut + fin

def get_xmax():
    'renvoie un float qui correspond à aujourd hui en fraction d année civile'
    yday = datetime.date.today().timetuple()[-2]
    year = datetime.date.today().year
    return year + yday/365.25

def get_probs(lambda_,points):
    """
    scale est le paramètre de la loi exponentielle
    points est une liste de points sur lesquels évaluer les proba
    """
    today=datetime.date.today()
    N=D_max_album
    x = [0.]
    for years in points[:-1]:
        day = datetime.date(years,1,1)
        delta_day=(today-day).days
        x.append(delta_day)
    rv = boltzmann(lambda_,N)
    max_ = rv.ppf(0.999)
    x.append(max_)
    probs = np.diff(rv.cdf(x))
    return probs

def get_xmin(lambda_):
    N = D_max_album
    rv = boltzmann(lambda_=lambda_,N=N)
    #on obtient donc un nombre de jours
    max_ = rv.ppf(0.999)
    max_year = (datetime.date.today()-datetime.timedelta(max_)).year
    return max(1950,max_year)


def plot_prob_cat(lambda_):
    """
    dessine un graphique en fonction de scale en bar chart en fonction des catégories
    """
    xmin = get_xmin(lambda_)
    xs = get_xs()
    xmax = get_xmax()
    all_points=[xmax]+xs
    widths = -np.diff(all_points)
    heights = get_probs(lambda_,xs)
    heights_cum = np.cumsum(heights)
    plt.bar(xs,heights,widths,align='edge')
    plt.bar(xs,heights_cum,widths,align='edge',alpha=0.5)
    plt.xlim(xmax,xmin)
    plt.show()

def plot_pref(p=0.5,value=10):
    N1 = days_from_date()
    perc = 100 * value * 365.25 / N1
    lambda_ = pref_lambda_boltzmann(p,perc,N1)
    plot_prob_cat(lambda_)
# Ecriture des fonctions pour le choix du classement
#D'abord une fonction pour définir la préférence

#choix du k en fonction de la catégorie

def N_from_cat(cat):
    """
    fonction qui va chercher le nombre d'items dans la liste d'une catégorie donnée
    """
    return len(get_list_items(cat))

def pref_lambda_boltzmann(prob=0.5,perc=20,N=100):
    """retourne un lambda pour lequel le tirage du top "perc"% est prob"""
    a=10
    b=1/(10*N)
    place = N*perc/100
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
    N1 = days_from_date()
    perc = 100 * v1 * 365.25 / N1
    categorie = an2cat(jours2an(tirage_jours(pref_lambda_boltzmann(p1,perc,N1))))
    N = N_from_cat(categorie)
    classement = tirage_classement(pref_lambda_boltzmann(p2,v2,N),N)
    return categorie , classement


#Maintenant faut que je fasse un scraper de senscritique...
# commençons par faire la liste de liens : 
links_albums = {'2021':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2021/2925866',
'2020':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2020/2582689',
'2019':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2019/2301842',
'2018':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2018/1757827',
'2017':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2017/1585750',
'2016':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2016/1176005',
'2015':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2015/703389',
'2014':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2014/367148',
'2013':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2013/173212',
'2012':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2012/165131',
'2011':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2011/840716',
'2010':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2010/840719',
'2009':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2009/840721',
'2008':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2008/840725',
'2007':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2007/840730',
'2006':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2006/840732',
'2005':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2005/840734',
'2004':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2004/840736',
'2003':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2003/840737',
'2002':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2002/840738',
'2001':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2001/840742',
'2000':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_de_2000/840745',
'1990':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_des_annees_1990/689494',
'1980':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_des_annees_1980/689488',
'1970':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_des_annees_1970/689466',
'1960':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_des_annees_1960/689452',
'1950':'https://www.senscritique.com/top/resultats/Les_meilleurs_albums_des_annees_1950/935588'}

def get_list_items(categorie):
    """
    renvoie la liste des oeuvres pour la catégorie donnée
    """
    link = links_albums[str(categorie)]
    req = requests.get(link)
    soup = BeautifulSoup(req.text,'lxml')
    list_items = soup.find("script",type="application/ld+json")
    list_dict = json.loads(list_items.contents[0])
    return list_dict['itemListElement']

def give_album_link(categorie,classement):
    "renvoie le lien de l'album qui correspond aux annees categories et au classement"
    i = classement - 1
    res=get_list_items(categorie)[i]
    return res['url']


