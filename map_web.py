from folium import Map , FeatureGroup , Marker , LayerControl ,Icon
from geopy.geocoders import Nominatim 
from geopy.extra.rate_limiter import RateLimiter 
import time 
import math
 

def user_input()->tuple: 
    """
    Gets information from user and returns tuple with it
    """
    user_latitude, user_longtitude = input('Enter your latitude, longtitude:').split() 
    user_coordinates = [user_latitude,user_longtitude] 
    user_year = input('Enter the year :') 
 
    return (user_coordinates, user_year) 
 
def create_dictionary(points:list)->list:
    """
    creates dictionary from list
    """
    dict_points ={}
    for element in points:
        dict_points[(element[1][0],element[1][1])] =[]
    for element in points:
        dict_points[(element[1][0],element[1][1])].append(element[1][-1])  
    return dict_points

 
def get_country(line:list)->str:
    """
    gets the country name from location
    """ 
    geolocator = Nominatim(user_agent='maap') 
    coordinates = str(line[0]) +', '+str(line[1]) 
    location =geolocator.reverse((coordinates),language='en') 
    print(location.address) 
    country =str(location.raw['address']['country']) 
    if country == 'United States':
        country = 'USA'
    elif country == 'United Kingdom':
        country='UK'

    return country 
 
 
def read_file(file_path:str, year:str,country:str)->list:
    """
    reads the file and returns list according to year and country parameters
    """  
    with open(file_path ,'r',encoding='latin1') as file_to_read: 
        lines = file_to_read.readlines() 
        lines =lines[14:-1]  
        new_lines =[]
        # new_lines.append('"qqqq" (1979) {(#9.19)}			qqq, qq') 
        for line in lines: 
            line =line.split('\t') 
            name_and_date =line[0] 
            name_and_date = name_and_date.split('(')[1] 
            date = name_and_date[:4] 
            location =line[1].split(',')[-1].strip() 
            movie_name = line[0].split('(')[0].strip()
            #print(movie_name)
            if str(year) == date and location==country : 

                line = [x for x in line if x !='']
                str_to_add = movie_name +'\t'+ line[1]
                if str_to_add not in new_lines:
                    new_lines.append(str_to_add) 
        if len(new_lines) > 100:
            new_lines = new_lines[:100]
         
    return new_lines 
                  
 
def find_location(locations:list)->list:
    """
    finds the location of places in list
    """ 
    geolocator = Nominatim(user_agent='maap') 
    # geocode = RateLimiter(geolocator.geocode,min_delay_seconds=0.5) 
    coordinates = [] 
    for point in locations:
        point = point.split('\t')
        location_name = point[1].strip()
        movie_name = point[0]
        if location_name.count(',')>=3:
            location_name = location_name.split(',')
            location_name = location_name[1:]
            location_name = ','.join(location_name)
            location_name = location_name.lstrip()
        elif " - " in location_name:
            location_name =location_name.split(' - ')
            location_name = location_name[1]
        try:
            location = geolocator.geocode(location_name) 
            coordinates.append((location.latitude,location.longitude,location_name,movie_name)) 
        except AttributeError:
            continue
    return coordinates
         
def count_distance(ur_latitude:float,ur_longtitude:float,movie_latitude:float,movie_longtitude:float)->float:
    """
    counts the distance between 2 places by their coordinates
    I borrowed this algoritm from https://www.kite.com/python/answers/how-to-find-the-distance-between-two-lat-long-coordinates-in-python
    """
    R = 6373.0
    ur_latitude = math.radians(ur_latitude)

    ur_longtitude = math.radians(ur_longtitude)
    movie_latitude = math.radians(movie_latitude)
    movie_longtitude = math.radians(movie_longtitude)

    longtitude_difference = movie_longtitude - ur_longtitude
    latitude_difference = movie_latitude - ur_latitude

    a = math.sin(latitude_difference / 2)**2 + math.cos(ur_latitude) * math.cos(movie_latitude) * math.sin(longtitude_difference / 2)**2


    some_geographic_value_1 = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * some_geographic_value_1
    return distance


def closest_movies(mcoordinates:list,user_coords:list)->list:
    """
    finds closests movies by distance
    """
    distances =[]
    for element in mcoordinates:
        mdistance = count_distance(float(user_coords[0]),float(user_coords[1]),float(element[0]),float(element[1]))
        distances.append((mdistance,element))
    distances.sort(key=lambda x: x[0])
    distances =distances[:10]
    return distances


      

def create_map(user_coords:list,closest_points:list)->None:
    """
    creates map and saves it
    """ 
    mp = Map(location=[user_coords[0],user_coords[1]], zoom_start=15) 
    markers = FeatureGroup() 
    closest_dict = create_dictionary(closest_points)
    for key in closest_dict:
        markers.add_child(Marker(location=[key[0], key[1]], 
                                    popup=closest_dict[key], 
                                    icon=Icon())) 
    your_location = FeatureGroup()
    your_location.add_child(Marker(location=[user_coords[0],user_coords[1]],
                                    popup='You are here',
                                    icon=Icon()))
    mp.add_child(markers) 
    mp.add_child(your_location)
    mp.add_child(LayerControl()) 
 
    mp.save('map1.html') 
 
    

def script(file_path):
    user_info = user_input()
    user_coordinates = user_info[0]
    user_date = user_info[1]
    
    country = get_country(user_coordinates)
    
    location_list = read_file(file_path,user_date,country)
    coordinates_and_name = find_location(location_list)
    closest = closest_movies(coordinates_and_name,user_coordinates)
    create_map(user_coordinates,closest)


if __name__=="__main__": 

    script('locations.list')
