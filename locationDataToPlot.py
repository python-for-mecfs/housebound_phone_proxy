##Code to plot average distance travelled over time
##from Google Location history

##Processing of (unzipped) "Records.JSON" file from Google Takeout

import json
import glob
import os
import geopy.distance
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

###DEFINE SUBROUTINES#############################################
def loadJSON(filepath):


    filepath2=os.path.dirname(filepath)

    filename=os.path.basename(filepath)

    # Opening JSON file and loading the data
    print("Loading data...")
    data = []

    for f in glob.glob(os.path.join(filepath2, filename)):
        with open(f, "rb") as infile:
            data.append(json.load(infile))



    count = 0

    for n1 in data:
      for n2 in n1.values():
        print("Parsing and converting records to dataframe, n= ", len(n2))
        nth=0
        if count == 0:

            # Writing headers of CSV file
            header=['lat', 'long', 'utc_dt']
            ndx=range(0, len(n2))

            df= pd.DataFrame(columns=header, index=ndx)
            count += 1

        for n3 in n2:
            nth=nth+1
            if (nth%100)==0:
                print("Record ", nth, " of ", len(n2))

            entry = [i for i in n3.values()]
            
            ts = n3["timestamp"]
                
            utc=ts.replace('Z', '')
            
            if len(utc)==19:
                fmt='%Y-%m-%dT%H:%M:%S'
            else:
                fmt='%Y-%m-%dT%H:%M:%S.%f'
            
            utc_dt=dt.datetime.strptime(utc, fmt)
  
            lat=entry[0]/(10000000)
            long=entry[1]/(10000000)

            df.loc[ndx[nth-1]]=[lat, long, utc_dt]
           
            
          
    #calculate distances
    print("Calculating distances...")      
            

    deltaz=np.empty(len(n2))
    deltaz[0]=0


    for i in range(1, df.lat.size):
        coords_1=(df.lat[i-1], df.long[i-1])
        coords_2=(df.lat[i], df.long[i])
        dist=geopy.distance.geodesic(coords_1, coords_2).km
        deltaz[i]=dist
        

    df['deltaz']=deltaz

    print("Saving dataframe to pkl for future use...")
    dfname=os.path.join(filepath2, "all_loc_data.pkl")
    df.to_pickle(dfname)



    return(df)

def parseByDay(df):

    print("Converting to daily data summary (UTC to avoid travel/timezone complications)...")

    ##Aggregate by date
    pd_dt = pd.to_datetime(df['utc_dt'], infer_datetime_format=False, utc=True)

    # Calculate max poss distance (minlat, minlong)-->(maxlat, maxlong)

    temp = [df.deltaz, pd_dt]
    hds = ["deltaz", "date"]
    dfdz = pd.concat(temp, axis=1, keys=hds)

    dailysumdist = dfdz.groupby(dfdz.date.dt.date)["deltaz"].sum().reset_index()
    dsumdist = dailysumdist["deltaz"].astype('float')
    dates = dailysumdist["date"]

    temp = np.vstack((dates, dsumdist)).transpose()
    daily_dist = pd.DataFrame(data=temp, columns=['date', 'sumdist_km'])
    dailydfname = os.path.join(filepath2, 'dist_by_day.pkl')
    daily_dist.to_pickle(dailydfname)

    return (daily_dist)


def plotData(daily_dist, median_window, mean_window, iftext):

    plt.figure(1)
    x=daily_dist["date"].values
    y=daily_dist["sumdist_km"].values
    y2=daily_dist["sumdist_km"].rolling(median_window, min_periods=1, center=True).median()
    y3=y2.rolling(mean_window, min_periods=1, center=True).mean()
    plt.scatter(x, y, color='k', marker='.', s=1, alpha=0.3)
    plt.plot(x, y3, color=(0, 0.5, 0.5), linewidth=2)
    plt.xlabel('Date', size=20)
    plt.ylabel('Distance (km)', size=20)
    plt.xticks(size=16)
    plt.title('Average Distance Travelled Daily:\n'
              'Proxy for Sudden Onset Housebound Disability', size=16)
    plt.ylim(0, max(y3))
    plt.xlim(min(x), max(x))
    plt.grid(which='major',axis ='both', linewidth='0.5', color='gray')

    dateformat='%Y-%m-%d'
    input_date=input("Enter illness onset date in format YYYY-MM-DD :")
    onset_date=dt.datetime.strptime(input_date, dateformat)

    date=pd.to_datetime(daily_dist["date"], format=dateformat)
    cvdndx=date.where(date>=onset_date)
    temp=np.isnan(cvdndx)
    cvdndx=np.where(~temp)[0]
    yrng=range(0, 1+int(np.ceil(max(y3))))
    x1=cvdndx[0]
    x2=cvdndx[-1]
    plt.fill_betweenx(yrng, x[cvdndx[0]],x[cvdndx[-1]], facecolor=(0, 0.5, 0.5), alpha=0.15)

    if iftext==1:
        
        plt.text(x[int(np.ceil((x1+x2)/2))], int(np.ceil(np.median(y3))), 'Long Covid\nME/CFS\n\nSTOPS\nLIVES',
                 rotation=0, color=(0, 0.2, 0.2), ha='center', weight=700, size=16, fontstretch=1, style='italic')
        plt.text(x[int(np.ceil((x1)/20))], int(max(y3)*0.85), 'Normal variation in routine:\ne.g. job, commute,\n'
                 'social, volunteer\ncommitments etc.',
                 rotation=0, color=(0, 0.2, 0.2), ha='left', weight=300, size=12, fontstretch=1, style='italic', alpha=0.5)
        plt.text(x[int(np.ceil((x1)/100))], int(max(y3)*0.03), '*Data from Google phone location history',
                 rotation=0, color=(0, 0.2, 0.2), ha='left', weight=100, size=11, fontstretch=1, style='italic', alpha=0.5)
    if iftext==2:
        
        plt.text(x[int(np.ceil((x1+x2)/2))], int(np.ceil(np.median(y3))), 'ME/CFS\n\nSTOPS\nLIVES',
                 rotation=0, color=(0, 0.2, 0.2), ha='center', weight=700, size=16, fontstretch=1, style='italic')
        plt.text(x[int(np.ceil((x1)/20))], int(max(y3)*0.85), 'Normal variation in routine:\ne.g. job, commute,\n'
                 'social, volunteer\ncommitments etc.',
                 rotation=0, color=(0, 0.2, 0.2), ha='left', weight=300, size=12, fontstretch=1, style='italic', alpha=0.5)
        plt.text(x[int(np.ceil((x1)/100))], int(max(y3)*0.03), '*Data from Google phone location history',
                 rotation=0, color=(0, 0.2, 0.2), ha='left', weight=100, size=11, fontstretch=1, style='italic', alpha=0.5)

    
    ############ X axis date formatting #########
    locator = mdates.YearLocator()
    fmt = mdates.DateFormatter('%Y')
    X = plt.gca().xaxis
    X.set_major_locator(locator)
    X.set_major_formatter(fmt)
    plt.setp( X.get_majorticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    plt.show()

    return()

######END SUBROUTINES###############################################

#Ask for input file
filepath=input('Full file path ending in "Records.json" file from Google Takeout?:')

#Check for existence of pkl file
filepath2=os.path.dirname(filepath)
df_pkl="all_loc_data.pkl"
pkl_file=os.path.join(filepath2, df_pkl)

if (os.path.isfile(pkl_file)== True):
    print("Saved processed data file found, opening...")
    df = pd.read_pickle(pkl_file)
else:
    df=loadJSON(filepath)

#Check for existence of daily distance pkl filse
daily_dist_pkl="dist_by_day.pkl"
pkl_file2=os.path.join(filepath2, daily_dist_pkl)

if (os.path.isfile(pkl_file2)== True):
    print("Saved processed daily distance file found, opening...")
    daily_dist = pd.read_pickle(pkl_file2)
else:
    daily_dist=parseByDay(df)

#Plot data
median_window=90
mean_window=45

#Ask if want text overlay
iftext=input('Do you want text overlay on plot?(y/n)\n'
             '[NOTE: May not fit your data without editing code!]:')

if iftext=='Y' or iftext=='y':
    iftext=1
    choice=input('Do you want plot to say "ME/CFS" only instead of "Long Covid ME/CFS"? (y/n):')
    if choice=='Y' or choice=='y':
        iftext=2
else:
    iftext=0

plotData(daily_dist, median_window, mean_window, iftext)

print('Done!')



