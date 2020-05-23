#! /usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import requests
import io

class Data:
    def __init__(self, url):
        csv_content=requests.get(url).content.decode('utf-8')
        self.data=pd.read_csv(io.StringIO(csv_content),
                               quotechar='"', skipinitialspace=True)
        #csv_content=requests.get(url).content.decode('utf-8')
        #self.data=pd.read_csv(url, quotechar='"', skipinitialspace=True)
        self.area_names=self.data['Area name'].to_numpy()
        self.area_types=self.data['Area type'].to_numpy()

    def listAreas(self, area_type):
        return set(self.area_names[np.where(self.area_types == area_type)])

    def getCurveForArea(self, area_name):
        warea=np.where(self.area_names == area_name)
        date=pd.to_datetime(self.data['Specimen date']).to_numpy()[warea]
        return {'date': date,
                'datenum': np.array(list(map(mdates.date2num, date))),
                'daily': self.data['Daily lab-confirmed cases'].to_numpy()[warea],
                'cumulative': self.data['Cumulative lab-confirmed cases'].to_numpy()[warea]}

def NInfectious(curve, t_infectious):
    n_infectious=[]
    for thisdate in curve['datenum']:
        n_infectious.append(curve['daily'][np.where((curve['datenum'] >= thisdate-t_infectious) & (curve['datenum'] <= thisdate))].sum())
    return np.array(n_infectious)

def Plot(data, area_type, t_infectious):
    size_cm=(21.0, 29.7)
    fig=plt.figure(figsize=(size_cm[0]/2.54, size_cm[1]/2.54))
    #fig=plt.figure()
    Dax=fig.add_subplot(2, 1, 1)
    Rax=fig.add_subplot(2, 1, 2)
    Dax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    Dax.set_xlabel("Date")
    Dax.set_ylabel("Daily cases")
    plt.setp(Dax.get_xticklabels(), rotation=45, ha='right')
    Rax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    Rax.set_xlabel("Date")
    Rax.set_ylabel("R value")
    plt.setp(Rax.get_xticklabels(), rotation=45, ha='right')
    for area in data.listAreas(area_type):
        curve=data.getCurveForArea(area)
        n_infectious=NInfectious(curve, t_infectious)
        R=curve['daily']*t_infectious/n_infectious
        Dax.plot(curve['datenum'], curve['daily'], label=area)
        Rax.plot(curve['datenum'], R, label=area)
    Dax.legend()
    Rax.legend()
    return fig

def Run():
    data=Data('https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv')
    fig=Plot(data,
             area_type='Region',
             t_infectious=7 # Days for which a patient is infectious
    )
    plt.show()


if __name__ == "__main__":
    Run()
