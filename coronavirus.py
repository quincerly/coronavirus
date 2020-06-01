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
        self.swindow=[-7, 0] # Smoothing window extent (days)

    def listAreas(self, area_type):
        return sorted(set(self.area_names[np.where(self.area_types == area_type)]))
    def listAreaTypes(self):
        return sorted(list(set(self.area_types)))
    def getCurveForArea(self, area_name, smooth=False):
        warea=np.where(self.area_names == area_name)
        date64=pd.to_datetime(self.data['Specimen date']).to_numpy()[warea]
        date=[datetime.datetime.utcfromtimestamp(d.astype('O')/1e9) for d in date64]
        datenum=np.array(list(map(mdates.date2num, date64)))
        daily=self.data['Daily lab-confirmed cases'].to_numpy()[warea]
        cumulative=self.data['Cumulative lab-confirmed cases'].to_numpy()[warea]
        if smooth:
            #w=[-3.5, 3.5] # Smoothing window extent (days)
            daily=Smooth(datenum, daily, self.swindow)
            cumulative=Smooth(datenum, cumulative, self.swindow)
        return {
            'datetime': date,
            'datetime64': date64,
            'datenum': datenum,
            'daily': daily,
            'cumulative': cumulative,
        }

def Smooth(t, y, w):
    ys=[]
    for thist in t:
        ys.append(y[np.where((t > thist+w[0]) & (t <= thist+w[1]))].mean())
    return np.array(ys)

def NInfectious(curve, t_infectious):
    n_infectious=[]
    for thisdate in curve['datenum']:
        n_infectious.append(curve['daily'][np.where((curve['datenum'] >= thisdate-t_infectious) & (curve['datenum'] <= thisdate))].sum())
    return np.array(n_infectious)
