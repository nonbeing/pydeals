#!/usr/bin/python2.6

from geopy import geocoders
from geopy.distance import distance as geodistance
from configobj import ConfigObj, ConfigObjError

import re, httplib2, socket, pprint, yaml

from BeautifulSoup import BeautifulSoup


###############################################################################
#
# GLOBALS


config = None

search_location = None

search_city = None

deal_sites = None

deal_keywords = []

final_output = {}

###############################################################################


def read_config(configfile='scraper.ini'):
    """Reads Configuration from a config file using ConfigObj
    ConfigObj: http://www.voidspace.org.uk/python/configobj.html

    Args: 
        configfile: string containing the path of the config file.
            Defaults to "scraper.ini" in the current directory

    Returns:
        the 'config' object parsed from the 'configfile'

    Raises:
        Exception: if unexpected type parsed from configfile's 'deal_keywords'
        IOError: if the configfile could not be read

    """


    try:
        global search_city, search_location, deal_sites, deal_keywords
        global config 
        config = ConfigObj(configfile, file_error=True)

        search_city = config['Globals']['search_city']
        search_location = config['Globals']['search_location']

        deal_sites = config['Deal Sites'].keys()
        print '[DEBUG] | read_config() | Dealsites = ' + str(deal_sites)

        keywords = config['Globals']['deal_keywords']
        
        if(type(keywords)==list): # more than one keyword results in a list
                deal_keywords = keywords
        elif(type(keywords)==str): # only one keyword results in a string
            if keywords not in [None, '']:
                deal_keywords.append(keywords)
        else:
            raise Exception, ("Unexpected keyword type : "
                              "Check 'deal_keywords' in configfile")
        print '[DEBUG] | read_config() | Keywords = ' + str(deal_keywords)

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


        _, start_coords = list(g.geocode(start, exactly_one=False))[0]        

        # append 'search_city' to the destination string, if needed
        # ( not all location strings from dealsites contain city name)
        if search_city not in dest.lower() :
            dest = dest + ', ' + search_city

        _, dest_coords = list(g.geocode(dest, exactly_one=False))[0]

        return geodistance(start_coords, dest_coords).kilometers
    except Exception, e:
        print '[ERROR] | get_distance() | ' + str(e)












def build_final_output(keyword, dealsite, deal_text, deal_location, 
                      deal_link, deal_distance):
    """
    Example: build_final_output(
                'gym', 
                'snapdeal', 
                'Rs 299 & get 1 month gym membership more worth Rs 5000',
                'Koramangala, Bangalore',
                17.05
             )

    """
    global final_output

    final_output[keyword][dealsite].append( 
        { 
            'deal_text': deal_text, 
            'deal_location':deal_location, 
            'deal_link':deal_link,
            'deal_distance':deal_distance
        }
    )










def process_snapdeal():

    global config, final_output, search_city    

    sd_url = config['Deal Sites']['snapdeal']['start_url']
    snapdeal_url = re.sub(r'{search_city}', search_city, sd_url)
    
    print "[INFO] | process_snapdeal() | Going to URL: " + snapdeal_url
    h = httplib2.Http('.cache')
    resp, content = h.request(snapdeal_url)
    print "[INFO] | process_snapdeal() | Getting soup!"
    soup = BeautifulSoup(content)


    def process_div_tags():
        reslist=[]
        for divtag in soup('div', {'class':'sidebar-deal-excerpt'}):   # soup.findAll('div', {"class" : "sidebar-deal-excerpt"} ):
            if keyword in divtag.a.span.string.lower():
                reslist.append(divtag.a)

        for deal in reslist:
            print "[INFO] | process_snapdeal() | got result: " + deal.span.string
            nextdiv = deal.findNext('div')

            if nextdiv.attrs:
                while 'location' not in str(nextdiv.attrs):
                    nextdiv = nextdiv.findNext('div')
            else:
                continue    # skip div tags without attributes
            
            deal_location = nextdiv.string
            print("[INFO] | process_snapdeal() | getting distance to: " 
                  + deal_location)
            deal_distance = "%.2f" % get_distance(deal_location)
            print "[INFO] | process_snapdeal() | distance = " + deal_distance
    
            build_final_output(keyword, 'snapdeal', deal.span.string, deal_location, deal.findPrevious('a')['href'], deal_distance)




    def process_h2_tags():
        reslist=[]
        for h2tag in soup('h2', {'class':'deal-title'}):   # soup.findAll('h2', {'class' : 'deal-title'}):
            if keyword in h2tag.string.lower():
                reslist.append(h2tag.string)

        for deal in reslist:
            print "[INFO] | process_snapdeal() | got result: " + deal.string.strip()

            prevtag = deal.findPrevious('h3')   # location is within a previous h3 tag

            if prevtag.attrs:
                while 'location' not in str(prevtag.attrs):
                    prevtag = prevtag.findPrevious('h3')
            else:
                continue    # skip h3 tags without attributes

            deal_location = prevtag.string
            print("[INFO] | process_snapdeal() | getting distance to: "
                  + deal_location)
            deal_distance = "%.2f" % get_distance(deal_location)
            print "[INFO] | process_snapdeal() | distance = " + deal_distance

            build_final_output(keyword, 'snapdeal', deal.string.strip(), deal_location, deal.findNext('a', {'class':'buylink'})['href'], deal_distance)




    #initialize final_output's snapdeal list to an empty list for each keyword
    for i in range(0, len(deal_keywords)):
        keyword = deal_keywords[i]

        print("[INFO] | process_snapdeal() | current keyword = "
              + keyword)
        final_output[keyword]={}
        final_output[keyword]['snapdeal']=[]
        print "[INFO] | process_snapdeal() | finding '%s' in soup div tags" %(keyword)
        process_div_tags()

        print "[INFO] | process_snapdeal() | finding %s in soup h2 tags" %(keyword)
        process_h2_tags()








def pretty_print():
    print '\n\n[INFO] | main() | final_output: \n\n' #+ str(final_output)
    
    pprint.pprint(final_output, indent=2, width=160)
    

    #print '\n\n[INFO] | main() | final_output: \n\n' 

    # The yaml dump doesn't look that great on the default console, 
    # but it looks awesome on the iPython console. It looks just as stunning 
    # when printed to a file via dump(..., stream=outfile, ...)
    # so will use this when logging is enabled to yaml.dump to the log file
    #
    #outfile = open('yaml.out.txt', 'w')
    #yaml.safe_dump(final_output, stream=outfile, indent=4, default_flow_style=False, width=260, explicit_start=True, explicit_end=True)
    #outfile.close()









def main():

    try:
        # set socket timeout to 5s
        # to prevent getting stuck in network calls (especially from geopy)
        socket.setdefaulttimeout(5.0)
        print ("[DEBUG] | main() | socket timeout is "
               + str(socket.getdefaulttimeout()) )

        read_config()

        process_snapdeal()

        pretty_print()

    except Exception, e:
        print "[ERROR]: main() : " + str(e)














if __name__ == "__main__":
    main()
