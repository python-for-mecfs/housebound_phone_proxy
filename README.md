# housebound_phone_proxy
Takes Google phone location history and plots average daily distance travelled, with useful/descriptive overlays

Steps:

1) Get your Google phone location history (Google Takeout, follow steps online)
2) Unzip files. The only one you need is called "Records.json"
3) Run this python code. It will ask for the full filepath to Records.json file (e.g. C:\User\...\Takeout\Records.json), as well as illness onset date (this determines the location of the shaded box), and whether you want to include the text overlay.
4) Text overlay may not fit your data well--edit in the code if need be, or remove entirely and add text on top in a photo editor!

5) Requires Python 3.7+; calls json, glob, geopy.distance, datetime, numpy, pandas, matplotlib.pyplot, and matplotlib.dates 
