#!/usr/bin/python2.6

from geopy import geocoders
from geopy.distance import distance as geodistance

from configobj import ConfigObj, ConfigObjError

import re

from BeautifulSoup import BeautifulSoup

###############################################################################
#
# GLOBALS


config = None

search_location = None

search_city = None

deal_sites = None

deal_keywords = []

finaloutput = {}

###############################################################################
import httplib2


def read_config(configfile='scraper.ini'):
    """Reads Configuration from a config file using ConfigObj
    ConfigObj: http://www.voidspace.org.uk/python/configobj.html

    Args: 
        configfile: string containing the path of the config file.
            Defaults to "scraper.ini" in the current directory

    Returns:
        the 'config' object parsed from the 'configfile'

    Raises:
        IOError: if the configfile could not be read

    """


    try:
        global config 
        config = ConfigObj(configfile, file_error=True)
    except (ConfigObjError, IOError), e:
        print '[ERROR] | read_config() for file:' + configfile + ' | ' + str(e)
    except Exception, e:
        print '[ERROR] | read_config() | ' + str(e)
    

















def get_distance(dest, start=None):
    """Gets the distance from the "search_location" to a given location.

    This distance is the point-to-point ellipsoidal (Vincenty) distance.
    This function does not calculate the driving/walking/travel distance.
    The idea is to offer a simple estimate of the shortest distance between 
    two locations.

    Uses the google geocoding API to geocode locations and calculate distances
    (via the awesome 'geopy' library: http://code.google.com/p/geopy/)

    Args: 
        dest: a string containing the target location (destination)
            to where the distance is to be calculated

        start: an *optional* string containing the start location
            from where the distance is to be calculated.
            If not provided, start will default to the value of the
            global variable, 'search_location'

    Returns:
        a floating point number representing the distance between 
        'start' and 'dest'

    Raises:

    Examples: 
        # uses the default value of search_location for 'start':
        my_dist = get_distance('Vishalakshi Mantap, Bangalore')

        # uses 'RMV 2nd Stage' as 'start' 
        # ('search_city' is appended to both start and dest)
        dist2 = get_distance('Jayanagar', 'RMV 2nd Stage')

    To Do:
        See if walking/driving/travel distance can be found and given
        instead of the ellipsoidal surface distance
    """

    try:
        # set default value of 'start' if none provided
        # to 'search_location' : a global var
        if start in [None, '']:
            start = search_location 
        elif search_city not in start.lower() :
            start = start + ', ' + search_city

        g = geocoders.Google(domain='maps.google.co.in')
        

        _, start_coords = g.geocode(start)    
        

        # append 'search_city' to the destination string, if needed
        # ( not all location strings from dealsites contain city name)
        if search_city not in dest.lower() :
            dest = dest + ', ' + search_city

        _, dest_coords = g.geocode(dest)

        return geodistance(start_coords, dest_coords).kilometers
    except Exception, e:
        print '[ERROR] | get_distance() | ' + str(e)








def process_snapdeal():

    global config, finaloutput, search_city    

    sd_url = config['Deal Sites'] ['snapdeal'] ['start_url']

    snapdeal_url = re.sub(r'{search_city}', search_city, sd_url)
    
    print "[INFO] | process_snapdeal() | Going to URL: " + snapdeal_url

    
    h = httplib2.Http('.cache')

    resp, content = h.request(snapdeal_url)

    soup = BeautifulSoup(content)

    

    reslist = soup.findAll(text=re.compile('gym membership', re.I))

    #initialize finaloutput's snapdeal list to an empty list
    finaloutput['snapdeal']=[]

    for result in reslist:

        nextdiv = result.findNext('div')

        while 'location' not in str(nextdiv.attrs):
            nextdiv = nextdiv.findNext('div')

        dist = "%.2f" % get_distance(nextdiv.string)

        finaloutput['snapdeal'].append( 
            { 
                'deal':result, 
                'location':nextdiv.string, 
                'link':result.findPrevious('a')['href'],
                'distance':dist
            }
        )





















def main():
    global search_city, search_location, deal_sites, deal_keywords


    read_config()

    search_city = config['Globals']['search_city']
    search_location = config['Globals']['search_location']

    deal_sites = config['Deal Sites'].keys()

    deal_keywords = config['Globals']['deal_keywords']

    print '[DEBUG] | main() | Dealsites = ' + str(deal_sites)

    # url1 = config['Deal Sites'] [deal_sites[0]] ['start_url']
    # print "Going to URL: %s" %(url1)

    process_snapdeal()

    print '\n\n[INFO] | main() | finaloutput: ' + str(finaloutput)















if __name__ == "__main__":
    main()
