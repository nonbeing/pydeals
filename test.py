#!/usr/bin/python2.6

from geopy import geocoders
from geopy.distance import distance as geodistance

from configobj import ConfigObj, ConfigObjError

import re, httplib2, socket

from BeautifulSoup import BeautifulSoup
##############################
#
# GLOBALS
#

config = None

search_location = 'Lottegollahalli, Bangalore'

search_city = 'Bangalore'

deal_sites = ['snapdeal']

###############################################################################





def test_snapdeal(keyword='spa'):
    """function to get all deals from snapdeal matching a particular keyword

        Args: 
            keyword : optional string specifying what kind of deals you want
                to search for. Examples: 'spa', 'gym', 'massage', 'cake'
        
    """
    snapdeal_url='http://www.snapdeal.com/deals-Bangalore'

    print "[INFO] | process_snapdeal() | Going to URL: " + snapdeal_url
    socket.setdefaulttimeout(5.0)
    h = httplib2.Http('.cache')
    resp, content = h.request(snapdeal_url)
    print "[INFO] | process_snapdeal() | Getting soup!"
    soup = BeautifulSoup(content)


    finaloutput = {}
    finaloutput[keyword] = {}
    finaloutput[keyword] ['snapdeal'] = []

    print "[INFO] | process_snapdeal() | finding '%s' in soup div tags" %(keyword)

    reslist=[]
    for i in soup('div', {'class':'sidebar-deal-excerpt'}):   # soup.findAll('div', {"class" : "sidebar-deal-excerpt"} ):
        if keyword in i.a.span.string.lower():
            reslist.append(i.a)

    for deal in reslist:
        print "[INFO] | process_snapdeal() | got result: " + deal.span.string
        nextdiv = deal.findNext('div')

        if nextdiv.attrs:
            while 'location' not in str(nextdiv.attrs):
                nextdiv = nextdiv.findNext('div')
        else:
            continue
        
        deal_location = nextdiv.string

        print("[INFO] | process_snapdeal() | getting distance to: " 
                + deal_location)
        deal_distance = "%.2f" % get_distance(deal_location)

        print "[INFO] | process_snapdeal() | distance = " + deal_distance

        finaloutput[keyword] ['snapdeal'].append( 
            { 
                'deal':deal.span.string, 
                'location':deal_location, 
                'link':deal.findPrevious('a')['href'],
                'distance':deal_distance
            }
        )


    print "[INFO] | process_snapdeal() | finding keyword in soup h2 tags"

    reslist=[]
    for i in soup('h2', {'class':'deal-title'}):   # soup.findAll('h2', {'class' : 'deal-title'}):
        if keyword in i.string.lower():
            reslist.append(i.string)

    for deal in reslist:
        print "[INFO] | process_snapdeal() | got result: " + deal.string.strip()

        prevtag = deal.findPrevious('h3')

        if prevtag.attrs:
            while 'location' not in str(prevtag.attrs):
                prevtag = prevtag.findPrevious('h3')
        else:
            continue

        deal_location = prevtag.string
        
        print("[INFO] | process_snapdeal() | getting distance to: "
                + deal_location)
        deal_distance = "%.2f" % get_distance(deal_location)
        print "[INFO] | process_snapdeal() | distance = " + deal_distance

        finaloutput[keyword] ['snapdeal'].append( 
            { 
                'deal':deal.string.strip(), 
                'location':deal_location, 
                'link':deal.findNext('a', {'class':'buylink'})['href'],
                'distance':deal_distance
            }
        )

    print "finaloutput: " + str(finaloutput)









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

        print ("[DEBUG] | get_distance() | socket timeout is "
                 + str(socket.getdefaulttimeout()) )

        _, start_coords = list(g.geocode(start, exactly_one=False))[0]        

        # append 'search_city' to the destination string, if needed
        # ( not all location strings from dealsites contain city name)
        if search_city not in dest.lower() :
            dest = dest + ', ' + search_city

        _, dest_coords = list(g.geocode(dest, exactly_one=False))[0]

        return geodistance(start_coords, dest_coords).kilometers
    except Exception, e:
        print '[ERROR] | get_distance() | ' + str(e)








test_snapdeal()
