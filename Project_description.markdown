## Sushi and ramen noodle business case in the Norwegian capital Oslo

#### Problem description
You work in the analytics division of an international food chain. 
The chain has become popular in Asia and North- America and is looking towards establishing a foothold in Europe. 
The chain has two kinds of restaurants – ramen noodle and sushi restaurants. 
The head of the strategy division asks you to analyze the market for sushi and noodle restaurants in the Norwegian capital, Oslo, and recommend which kind of restaurants to establish and in which boroughs. He tells you further that your input will be an important source of information for the executive team, who will 
take their decisions upon it and use it to carve out their strategy for entering Euope, beginning with Norway. 

#### Data 
You want the executive team to get a thorough understanding of the characteristics of Oslo.  You decide to visualize the existing market for sushi and noodle 
restaurants within each Oslo borough through choropleth graphs, and use machine learning algorithms to show which borrows are similar and which are not.  

The information sources you use to inform the executive on how to enter the Norwegian market are: 

- A list of boroughs from Wikipedia: https://en.wikipedia.org/wiki/List_of_boroughs_of_Oslo

- FourSquare to search for existing sushi and noodle restaurants in each Oslo borough

- Coordinates for the Oslo boroughs from Statistcs Norway (to make the choropleth maps): https://kart.ssb.no/

From the Wikipedia page you are able to segment Oslo into different boroughs. Latitude and longitude of each borough can be acquired from the Python Geopy library.
These coordinates are then be used to search for sushi and noodle restaurants from FourSqaure within a 1 km. range of each coordinate. 

For each borough you count the number of sushi and noodle restaurants, respectively. These totals are used to create choropleth map of the Oslo boroughs showing the density of sushi and noodle restaurants in Oslo. The coordinates of Oslo boroughs are given by Statistics Norway. 

Further the coordinates of the sushi and noodle restaurants will be plotted in maps showing the the exact locations of sushi and noodle restaurants within the borougs. 


