#!/usr/bin/env python
# coding: utf-8

# # Capstone assignment - the battle of neigborhoods - week 2
# ### Sushi and ramen noodle business case in the Norwegian capital Oslo

# ### Table of contents
# * [Introduction: Business Problem](#introduction)
# * [Data](#data)
# * [Methodology](#methodology)
# * [Analysis](#analysis)
# * [Results and Discussion](#results)
# * [Conclusion](#conclusion)

# 
# 
# ## Problem description
# You work in the analytics division of an international food chain. 
# The chain has become popular in Asia and North- America and is looking towards establishing a foothold in Europe. 
# The chain has two kinds of restaurants – ramen noodle and sushi restaurants. 
# The head of the strategy division asks you to analyze the market for sushi and noodle restaurants in the Norwegian capital, Oslo, and recommend which kind of restaurants to establish and in which boroughs. He tells you further that your input will be an important source of information for the executive team, who will 
# take their decisions upon it and use it to carve out their strategy for entering Euope, beginning with Norway. 
# 
# ## Data 
# You want the executive team to get a thorough understanding of the characteristics of Oslo.  You decide to visualize the existing market for sushi and noodle 
# restaurants within each Oslo borough through choropleth graphs, and use machine learning algorithms to show which borrows are similar and which are not.  
# 
# The information sources you use to inform the executive on how to enter the Norwegian market are: 
# 
# - A list of boroughs from Wikipedia: https://en.wikipedia.org/wiki/List_of_boroughs_of_Oslo
# 
# - FourSquare to search for existing sushi and noodle restaurants in each Oslo borough
# 
# - Coordinates for the Oslo boroughs from Statistcs Norway (to make the choropleth maps): https://kart.ssb.no/
# 
# From the Wikipedia page you are able to segment Oslo into different boroughs. Latitude and longitude of each borough can be acquired from the Python Geopy library.
# These coordinates are then be used to search for sushi and noodle restaurants from FourSqaure within a 1 km. range of each coordinate. 
# 
# For each borough you count the number of sushi and noodle restaurants, respectively. These totals are used to create choropleth map of the Oslo boroughs showing the density of sushi and noodle restaurants in Oslo. The coordinates of Oslo boroughs are given by Statistics Norway. 
# 
# Further the coordinates of the sushi and noodle restaurants will be plotted in maps showing the the exact locations of sushi and noodle restaurants within the borougs. 

# 
# #### We begin by importing the necessary libraries 

# In[546]:


import pandas as pd # library for data analsysis
import requests # library to handle requests
import urllib.request # library to handle requests
get_ipython().system('pip install BeautifulSoup4 # library to handle URL sites ')
get_ipython().system('pip install html5lib #library to use for handling html')
from bs4 import BeautifulSoup
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe
get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes')
import folium

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

import numpy as np

get_ipython().system('conda install -c conda-forge geopy --yes ')
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values


print("Libraries are installed")


# #### We download the table showing the boroughs in Oslo from Wikipedia

# In[602]:


url = "https://en.wikipedia.org/wiki/List_of_boroughs_of_Oslo"
page = urllib.request.urlopen(url)
soup = BeautifulSoup(page, "html5lib")


# #### We read only the table containing the borough names and store the names in a pandas dataframe 

# In[603]:


table = soup.find('table', class_='wikitable sortable')


# In[604]:


#print(table)


# In[605]:


A = []
B = []
C = []
D = []


for row in table.findAll('tr'):
    cells=row.findAll('td')
    if len(cells)==4:
        A.append(cells[0].find(text=True))
        B.append(cells[1].find(text=True))
        C.append(cells[2].find(text=True))
        D.append(cells[3].find(text=True))


# In[606]:


df_Oslo_borough = pd.DataFrame(A,columns=['Borough'])
df_Oslo_borough['Residents'] = B
df_Oslo_borough['Area_km'] = C
df_Oslo_borough['Borough_number'] = D
df_Oslo_borough


# #### We clean the table

# In[607]:


df_Oslo_borough.drop(["Residents", "Area_km"], axis =1, inplace = True)
df_Oslo_borough = df_Oslo_borough.replace("\n", "", regex = True) #We remove the newlines command \n


# #### We need to change the borough numbers somewhat to use them later on for the choropleth graphs

# In[608]:


placeholder = []
#df_Oslo_borough["City"] = []
for i in range(0,len(df_Oslo_borough["Borough_number"])):
    if int(df_Oslo_borough["Borough_number"][i]) < 10:
        placeholder.append("03010" + df_Oslo_borough["Borough_number"][i]) 
    else:
        placeholder.append("0301" + df_Oslo_borough["Borough_number"][i])
placeholder


# In[609]:


df_Oslo_borough["Borough_number1"] = placeholder 


# #### The wikipedia list does not include the city center as a separate Borough - and so we add the city center to the list 

# In[610]:


City = pd.DataFrame([["Center", "16", "030116"]], columns = ["Borough", "Borough_number", "Borough_number1"])
df_Oslo_borough = pd.concat([City, df_Oslo_borough]).reset_index(drop =True)
df_Oslo_borough


# #### We get the coordinates of the boroughs and add them to the dataframe

# In[611]:


Lat = [] 
Long = []
for borough in df_Oslo_borough["Borough"]:
    address = borough + ",Oslo"
    geolocator = Nominatim(user_agent="ny_explorer")
    location = geolocator.geocode(address)
    latitude = location.latitude
    longitude = location.longitude
    Lat.append(latitude)
    Long.append(longitude)


# In[612]:


df_Oslo_borough["Latitude"] = Lat 
df_Oslo_borough["Longitude"] = Long
df_Oslo_borough


# ## Foursquare 

# Now that we have all Oslo boroughs and their respective coordinates, we use the Foursquare API to get info on sushi and nooble restaurants in each neighborhood.
# 
# We include in our list only venues that have 'sushi' or 'noodle' in category name.

# #### We define our FourSquare credentials (taken out)

# In[613]:


CLIENT_ID =  # Foursquare ID
CLIENT_SECRET =  # Foursquare Secret
VERSION = '20180605' # Foursquare API version
LIMIT = 50


# #### We define the get requests

# In[614]:


search_query = 'Sushi'
latitude = 59.887563
longitude = 10.832748
radius = 1000
address = "Østensjø"
LIMIT = 100


# In[615]:


url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, search_query, radius, LIMIT)
results = requests.get(url).json()

venues = results['response']['venues'][0]
venue_category = json_normalize(venues) # flatten JSON
venue_category


# #### We define a function that extracts the category of the restaurant  

# In[616]:


# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[617]:


venues = results['response']['venues']
    
venue_category = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['name', 'categories', 'location.lat', 'location.lng']
venue_category = venue_category.loc[:, filtered_columns]
# filter the category for each row
venue_category['categories'] = venue_category.apply(get_category_type, axis=1)

# clean columns
venue_category.columns = [col.split(".")[-1] for col in venue_category.columns]

venue_category.head()


# In[618]:


def getRestaurants(names, latitudes, longitudes, query, radius=1000,):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET,  
            lat, 
            lng,
            VERSION,
            query,
            radius, 
            100)
            
        # make the GET request
        results = requests.get(url).json()['response']['venues']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['name'], 
            v['location']['lat'], 
            v['location']['lng']) for v in results])

    venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    venues.columns = ['Borough', 
                  'Borough Latitude', 
                  'Borough Longitude', 
                  'Venue name', 
                  'Venue Latitude', 
                  'Venue Longitude']
    
    return(venues)


# #### We begin by searching for sushi restaurants for each borough

# In[620]:


search_query = 'Sushi'
Oslo_sushi = getRestaurants(names=df_Oslo_borough['Borough'],
                                   latitudes=df_Oslo_borough['Latitude'],
                                   longitudes=df_Oslo_borough['Longitude'],
                                   query = search_query)


# #### We add "Sushi restaurant" as a venue category label in the dataframe 

# In[621]:


Oslo_sushi["Venue_Category"] = "Sushi restaurant"


# #### We now count the number of sushi restaurants per borough 

# In[622]:


df_sushi_count = Oslo_sushi.groupby(['Borough', 'Borough Latitude', 'Borough Longitude', 'Venue_Category'], as_index=False).agg("count")


# In[623]:


df_sushi_count.rename({'Venue name': 'Count'}, axis = 1, inplace = True)
df_sushi_count.drop(['Venue Latitude', 'Venue Longitude'], axis = 1, inplace=True)


# #### We include the Borough numbers into the dataframe 

# In[624]:


df_sushi_merged = pd.merge(df_sushi_count, df_Oslo_borough, on="Borough")


# In[625]:


df_sushi_merged.drop(['Latitude', 'Longitude'], axis = 1, inplace=True)


# #### We redo the analysis for noodle restaurants

# In[626]:


search_query = 'Noodle'
Oslo_noodle = getRestaurants(names=df_Oslo_borough['Borough'],
                                   latitudes=df_Oslo_borough['Latitude'],
                                   longitudes=df_Oslo_borough['Longitude'],
                                   query = search_query)


# In[627]:


Oslo_noodle['Venue_category'] = "Noodle restaurant"


# In[628]:


df_noodle_count = Oslo_noodle.groupby(['Borough', 'Borough Latitude', 'Borough Longitude', 'Venue_category'], as_index=False).agg("count")


# In[629]:


df_noodle_count.rename({'Venue name': 'Count'}, axis = 1, inplace = True)
df_noodle_count.drop(['Venue Latitude', 'Venue Longitude'], axis = 1, inplace=True)


# #### We include the borough numbers into the dataframe

# In[630]:


df_noodle_merged = pd.merge(df_noodle_count, df_Oslo_borough, on="Borough")


# In[631]:


df_noodle_merged.drop(['Latitude', 'Longitude'], axis = 1, inplace=True)


# ## Methodology

# The purpose of the analysis is to understand where there are many sushi and noodle restaurants today. Boroughs that have a low density of sushi restaurants is likely not to have a market for neither sushi nor noodle restaurants. Boroughs with a high density of sushi restaurants and a low density of noodle restaurants is likely to be an ideal borough to open a new noodle restaurant, as the borough displays great demand for Asian food allready. 
# 
# If there are boroughs with similar properties with the boroughs that have a high density of sushi restaurants, but has low sushi restaurant density, these boroughs are ideal for new sushi restaurants. 

# ## Analysis

# We do some basic analysis to understand how many sushi and noodle restaurants are established in Oslo, respectively, and how many of each are in the different Oslo borouhgs. 
# We first take a look at the sushi restaurants in each borough.

# In[632]:


df_sushi_merged


# There are 177 sushi restaurants located in Oslo in total. We can see that particularly five boroughs stand out with a high density of sushi restaurants: the city center, Frogner, Grunerløkka, Sagene and St.Hanshaugen. In these five boruoghs a total of 160 sushi restaurants are located. We now take a look at noodle restaurants.

# In[633]:


df_noodle_merged


# While there are 177 sushi restaurants in Oslo, there are only five noodle restaurants. Only four of the 16 boroughs have a noodle restaurant.  

# #### Now we can create the maps 

# #### We read the GeoJson file containing the coordiantes of the city boroughs from the file Bydeler.geojson 

# In[634]:


import json 
with open("Bydeler.geojson") as f:
    gj = json.load(f)


# In[635]:


Oslo_map = folium.Map(location=[59.9100, 10.7258], zoom_start=11)


# In[636]:


# generate choropleth map using the count of sushi restaurants of each borough
Oslo_map.choropleth(
    geo_data=gj,
    data=df_sushi_merged,
    columns=['Borough_number1', 'Count'],
    key_on='feature.properties.bydelsnr',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Sushi restaurants in Oslo'
)

# display map
Oslo_map


# #### We draw a map of noodle restaurant density

# In[637]:


Oslo_map1 = folium.Map(location=[59.9100, 10.7258], zoom_start=11)


# In[638]:


# generate choropleth map using the total immigration of each country to Canada from 1980 to 2013
Oslo_map1.choropleth(
    geo_data=gj,
    data=df_noodle_merged,
    columns=['Borough_number1', 'Count'],
    key_on='feature.properties.bydelsnr',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Noodle restaurants in Oslo'
)

# display map
Oslo_map1


# #### We now analyze the boroughs to understand which of them are similar

# #### We define a function to extract venue information from FourSquare

# In[639]:


address = 'Østensjø, Oslo'

geolocator = Nominatim(user_agent="foursquare_agent")
location = geolocator.geocode(address)
latitude =  59.887563
longitude = 10.832748 
radius = 1000
LIMIT = 100

url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, radius, LIMIT)
url


# In[640]:


results = requests.get(url).json()


# In[641]:


# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[642]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]
# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head()


# In[643]:


def getNearbyVenues(names, latitudes, longitudes, radius=1000):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Borough', 
                  'Borough Latitude', 
                  'Borough Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[644]:


Oslo_venues = getNearbyVenues(names=df_Oslo_borough['Borough'],
                                   latitudes=df_Oslo_borough['Latitude'],
                                   longitudes=df_Oslo_borough['Longitude'])


# In[645]:


print(Oslo_venues.shape)


# In[ ]:





# In[646]:


# one hot encoding
Oslo_onehot = pd.get_dummies(Oslo_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
Oslo_onehot['Borough'] = Oslo_venues['Borough'] 

# move neighborhood column to the first column
index = Oslo_onehot.columns.get_loc("Borough")
fixed_columns = [Oslo_onehot.columns[index]] + list(Oslo_onehot.columns[:index]) + list(Oslo_onehot.columns[index+1:])
Oslo_onehot = Oslo_onehot[fixed_columns]

Oslo_onehot.head()


# In[647]:


Oslo_grouped = Oslo_onehot.groupby('Borough').mean().reset_index()
Oslo_grouped


# #### We write a function to sort the venues in descending order.

# In[648]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[649]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Borough']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
Borough_venues_sorted = pd.DataFrame(columns=columns)
Borough_venues_sorted['Borough'] = Oslo_grouped['Borough']

for ind in np.arange(Oslo_grouped.shape[0]):
    Borough_venues_sorted.iloc[ind, 1:] = return_most_common_venues(Oslo_grouped.iloc[ind, :], num_top_venues)

Borough_venues_sorted.head()


# #### We cluster the boroughs

# In[650]:


# set number of clusters
kclusters = 5

Oslo_grouped_clustering = Oslo_grouped.drop('Borough', axis=1)
# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(Oslo_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:38] 


# #### We display the cluster labels on an Oslo map
# 

# In[651]:


# add clustering labels
Borough_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

Oslo_merged = df_Oslo_borough

# merge Oslo_grouped with Oslo_data to add latitude/longitude for each neighborhood
Oslo_merged = Oslo_merged.join(Borough_venues_sorted.set_index('Borough'), on='Borough')


# In[652]:


address = 'Oslo, Norway'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinates of Oslo are {}, {}.'.format(latitude, longitude))


# In[653]:


# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(Oslo_merged['Latitude'], Oslo_merged['Longitude'], Oslo_merged['Borough'], Oslo_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    print(cluster)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# In[ ]:





# ## Results and discussion 

# Our analysis shows that there are a great number of sushi restaurants located in Oslo, but very few noodle restaurants. Most of the sushi restaurants are located in mainly five boroughs. The few noodle restaurants that exist today are also located within these five boroughs. This suggests that there is great demand for Asian food in these five boroughs. You conclude that a noodle restaurant should be opened within one of these five boroughs. Looking at the city map you decide to recommend opening a noodle restaurant in the southern part of St. Hanshaugen, which is geographically closest to all of the five boroughs with a high sushi restaurant density.
# 
# 

# As for sushi restaurants, you recommend opening one in either of the five boroughs. Looking at your statistical analysis you see that both Nordre Aker and Vestre Aker bear similar characteristics as the five boroughs with a high sushi restaurants, but these two boroughs contain few sushi restaurants. You suggest to your superiors that these two boroughs are worthwhile exploring further. 

# ## Conclusion 

# The purpose of the analysis was to identify which boroughs are ideal for opening new sushi and/ or noodle restaurants. You have successfully identified five candidate boroughs for noodle restaurants, of which St. Hanshaugen seems to be most tempting based on its geographical location. You have also identified seven candidate boroughs for sushi restaurants, out of which 2 contain few competitors today. 

# In[ ]:




