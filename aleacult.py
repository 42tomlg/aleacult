from scipy.stats import expon
import math
import datetime

#date d'aujourd'hui
today=datetime.date.today()

#10 ans en jours
ten_years = 10 * 365.25

def pref_lambda(p=0.5,value=ten_years):
    "donne lambda en fonction du percentile visé"
    return -math.log(1-p)/value

def get_scale(lam):
    return 1/lam

