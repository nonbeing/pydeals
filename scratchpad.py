http://where.yahooapis.com/v1/places.q('sydney%20opera%20house')?appid=k7WzQbDV34GdQulCoOH5ENuVeoh8Djv4VhyhG27ZuSLtMqY9lf8_UVouXOi56CTf5dZ84KVpFYQ-


http://where.yahooapis.com/geocode?q=1600+Pennsylvania+Avenue,+Washington,+DC&appid=k7WzQbDV34GdQulCoOH5ENuVeoh8Djv4VhyhG27ZuSLtMqY9lf8_UVouXOi56CTf5dZ84KVpFYQ-




highlight LineNr cterm=None ctermfg=darkgrey  ctermbg=grey



<ul>
 <li>An unrelated list
</ul>

<h1>Heading</h1>
<p>This is 
    <b>the list you want</b>:
</p>
<ul>
    <li>The data you want
</ul>
















search_location = 'Lottegollahalli, Bangalore'
search_city = 'Bangalore'

from geopy import geocoders
from geopy.distance import distance as geodistance








def get_distance(dest, start=None):
    """Gets the distance from the "current_location" to a given location.

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
            global variable, 'current_location'

    Returns:
        a floating point number representing the distance between 
        'start' and 'dest'

    Raises:

    Examples: 
        # uses the default value of current_location for 'start':
        my_dist = get_distance('Vishalakshi Mantap, Bangalore')

        # uses 'RMV 2nd Stage' as 'start' 
        # ('Bangalore' is appended to both start and dest)
        dist2 = get_distance('Jayanagar', 'RMV 2nd Stage')

    To Do:
        See if walking/driving/travel distance can be found and given
        instead of the ellipsoidal surface distance
    """

    # set default value of 'start' if none provided
    if start in [None, '']:
        start = current_location # current_location: a global var
    elif 'bengaluru' not in start.lower() and 'bangalore' not in start.lower() :
        start += ', Bangalore'

    g = geocoders.Google(domain='maps.google.co.in')
    

    _, start_coords = g.geocode(start)    
    
    # append ", bangalore" to the destination string, if needed
    # since not all location strings from dealsites contain 'bangalore'

    if 'bengaluru' not in dest.lower() and 'bangalore' not in dest.lower() :
        dest += ', Bangalore'

    _, dest_coords = g.geocode(dest)

    return geodistance(start_coords, dest_coords).kilometers
    








def process_snapdeal():
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




        print "\ndeal = " + result
        print "location = " + nextdiv.string #the location of the resultant deal
        print "link = " + result.findPrevious('a')['href']
        print "\n\n"













def test():
    finaloutput = {}
    finaloutput['spa'] = {}
    finaloutput['spa'] ['snapdeal'] = []

    print "[INFO] | process_snapdeal() | finding keyword in soup"
    reslist = soup.findAll(text=re.compile('spa', re.I))

    for result in reslist:

        print "[INFO] | process_snapdeal() | got result: " + result
        nextdiv = result.findNext('div')

        if nextdiv.attrs:
            while 'location' not in str(nextdiv.attrs):
                nextdiv = nextdiv.findNext('div')
        else:
            continue

        print("[INFO] | process_snapdeal() | getting distance to: " 
                + nextdiv.string)
        dist = "%.2f" % get_distance(nextdiv.string)

        finaloutput['spa'] ['snapdeal'].append( 
            { 
                'deal':result, 
                'location':nextdiv.string, 
                'link':result.findPrevious('a')['href'],
                'distance':dist
            }
        )







soup('a')[75].findAll(text=re.compile('gym membership', re.I))



for i in soup('a'):
    if i.findAll(text=re.compile('spa', re.I)):
        mylist.append(i)









for i in soup('a'):
    if i.find('span'):
        if i.find('span').find(text=re.compile('gym', re.I)):
            somelist.append(i)





for i in soup('h2'):
    if i.find(text=text=re.compile(deal_keywords[i], re.I)):
        reslist.append(i)













def test2():
    finaloutput = {}
    finaloutput['spa'] = {}
    finaloutput['spa'] ['snapdeal'] = []

    print "[INFO] | process_snapdeal() | finding keyword in soup div tags"

    reslist=[]
    for i in soup('div', {'class':'sidebar-deal-excerpt'}):   # soup.findAll('div', {"class" : "sidebar-deal-excerpt"} ):
        if 'spa' in i.a.span.string.lower():
            reslist.append(i.a)

    for deal in reslist:
        print "[INFO] | process_snapdeal() | got result: " + str(deal)
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

        print "[INFO] | process_snapdeal() | distance = " + dist

        finaloutput['spa'] ['snapdeal'].append( 
            { 
                'deal':str(deal), 
                'location':deal_location, 
                'link':deal.findPrevious('a')['href'],
                'distance':deal_distance
            }
        )


    print "[INFO] | process_snapdeal() | finding keyword in soup h2 tags"

    reslist=[]
    for i in soup('h2', {'class':'deal-title'}):   # soup.findAll('h2', {'class' : 'deal-title'}):
        if 'spa' in i.string.lower():
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
        print "[INFO] | process_snapdeal() | distance = " + dist

        finaloutput['spa'] ['snapdeal'].append( 
            { 
                'deal':deal.string.strip(), 
                'location':deal_location, 
                'link':deal.findNext('a', {'class':'buylink'})['href'],
                'distance':deal_distance
            }
        )

    print "finaloutput: " + str(finaloutput)

