#! /usr/bin/env python3

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import requests
import io
import datetime

def Divide(a_aerr, b_berr):
    a, aerr=a_aerr
    b, berr=b_berr
    return a/b, np.sqrt(aerr**2+a**2/b**2*berr**2)/b

def Smooth(t, y_yerr, w):
    y, yerr=y_yerr
    ys=[]
    yerrs=[]
    for thist in t:
        ind=np.where((t > thist+w[0]) & (t <= thist+w[1]))
        ys.append(y[ind].mean())
        yerrs.append((yerr[ind]**2).sum()**0.5/len(ind[0]))
    return np.array(ys), np.array(yerrs)

class Data:
    def __init__(self, url):
        self.url=url
        csv_content=requests.get(url).content.decode('utf-8')
        self.data=pd.read_csv(io.StringIO(csv_content),
                               quotechar='"', skipinitialspace=True)
        #csv_content=requests.get(url).content.decode('utf-8')
        #self.data=pd.read_csv(url, quotechar='"', skipinitialspace=True)
        self.area_names=self.data['Area name'].to_numpy()
        self.area_types=self.data['Area type'].to_numpy()
        #self.swindow=[-7, 0] # Smoothing window extent (days)
        self.swindow=[-3.5, 3.5] # Smoothing window extent (days)

    def listAreas(self, area_type):
        return sorted(set(self.area_names[np.where(self.area_types == area_type)]))
    def listAreaTypes(self):
        return sorted(list(set(self.area_types)))
    def getCurveForArea(self, area_type, area_name, smooth=False):
        warea=np.where((self.area_types == area_type) & (self.area_names == area_name))
        date64=pd.to_datetime(self.data['Specimen date']).to_numpy()[warea]
        tind=np.argsort(date64)

        date64=date64[tind]
        date=[datetime.datetime.utcfromtimestamp(d.astype('O')/1e9) for d in date64]
        weekday=np.array([this_date.weekday() for this_date in date])
        datenum=np.array(list(map(mdates.date2num, date64)))
        daily=self.data['Daily lab-confirmed cases'].to_numpy()[warea][tind]
        dailyerr=daily**0.5
        cumulative=self.data['Cumulative lab-confirmed cases'].to_numpy()[warea][tind]
        cumulativeerr=cumulative**0.5
        if smooth:
            #w=[-3.5, 3.5] # Smoothing window extent (days)
            daily, dailyerr=Smooth(datenum, (daily, dailyerr), self.swindow)
            cumulative, cumulativeerr=Smooth(datenum, (cumulative, cumulativeerr), self.swindow)
        return {
            'datetime': date,
            'datetime64': date64,
            'datenum': datenum,
            'daily': daily,
            'dailyerr': dailyerr,
            'cumulative': cumulative,
            'cumulativeerr': cumulativeerr,
        }

def CalcWeeklyFac(daily, dailyerr, datenum, weekday):
    weekday_total=np.zeros(7)
    for this_weekday in range(7):
        this_weekday_ind=np.where(weekday==this_weekday)
        weekday_total[this_weekday]=np.nansum(daily[this_weekday_ind])
    w, we=Divide((weekday_total, np.sqrt(weekday_total)), (weekday_total.sum(), np.sqrt(weekday_total.sum())))
    weeklyfac=np.zeros_like(daily, dtype='float')
    weeklyfacerr=np.zeros_like(daily, dtype='float')
    for this_weekday in range(7):
        this_weekday_ind=np.where(weekday==this_weekday)
        weeklyfac[this_weekday_ind]=7*w[this_weekday]
        weeklyfacerr[this_weekday_ind]=7*we[this_weekday]
    return weeklyfac, weeklyfacerr

def CalcNInfectious(curve, t_infectious):
    n_infectious=[]
    n_infectious_err=[]
    for thisdate in curve['datenum']:
        ind=np.where((curve['datenum'] >= thisdate-t_infectious) & (curve['datenum'] <= thisdate))
        n_infectious.append(curve['daily'][ind].sum())
        n_infectious_err.append((curve['dailyerr'][ind]**2).mean()**0.5)
    return np.array(n_infectious), np.array(n_infectious_err)

def CalcR(curve, t_infectious,):
    daily, dailyerr=curve['daily'], curve['dailyerr']
    return Divide((daily*t_infectious, dailyerr*t_infectious),
                  CalcNInfectious(curve, t_infectious))
