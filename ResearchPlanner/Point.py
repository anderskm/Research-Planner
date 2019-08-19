import numpy as np
import utm

class Point(object):
    latitude = None
    longitude = None
    altitude = None # Altidude is only used for reference. All calculations are made without the altitude
    east = None
    north = None
    zone = None
    ID = None
    _source = None

    def __init__(self, x=None, y=None, latitude=None, longitude=None, altitude=None, east=None, north=None, zone=None):
        
        _source = None

        # If x or y is specified, try to guess if it is utm or latlon coordinates based on their size
        if (x is not None and y is not None):
            if y > 90.0 or y < -90.0 or x < -180.0 or x > 180.0:
                north = y
                east = x
            else:
                latitude = y
                longitude = x

        if (latitude is not None and longitude is not None):
            latitude = np.longdouble(latitude)
            longitude = np.longdouble(longitude)
            east, north, zone = self._to_utm(latitude, longitude)
            _source = 'latlon'

        elif (east is not None and north is not None):
            if (zone is None):
                zone = self._utm_estimate_zone(east)
            east = np.longdouble(east)
            north = np.longdouble(north)
            latitude, longitude = self._to_latlon(east, north, zone)
            _source = 'utm'

        else:
            #TODO: Raise error
            pass
        
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.east = east
        self.north = north
        self.zone = zone
        self._source = _source
    
    def __str__(self):
        str_out = ''
        if (self._source == 'latlon'):
            str_out += '(' + '{: 12.8f}'.format(self.latitude) + u"\u00b0" + ';' + '{: 12.8f}'.format(self.longitude) + u"\u00b0" ')\n'
        elif(self._source == 'utm'):
            str_out += '(' + '{: 12.3f}'.format(self.east) + ' m E' + ';' + '{: 12.3f}'.format(self.north) + ' m N' + '), Zone: ' + '{:d}'.format(self.zone) + '\n'
        else:
            str_out += 'Latitude : ' + '{: 12.8f}'.format(self.latitude) + u"\u00b0" + '\n'
            str_out += 'Longitude: ' + '{: 12.8f}'.format(self.longitude) + u"\u00b0" + '\n'
            str_out += 'Altitude : ' + '{: 12.8f}'.format(self.altitude) + ' m\n'
            str_out += 'UTM East : ' + '{: 12.3f}'.format(self.east) + ' m\n'
            str_out += 'UTM North: ' + '{: 12.3f}'.format(self.north) + ' m\n'
            str_out += 'UTM Zone : ' + '{:d}'.format(self.zone)
        return str_out

    def __add__(self, y):
        # Add two points together
        pass

    def __div__(self, s):
        # Divide point with a scalar
        pass

    def _to_latlon(self, east, north, zone=None):
        if (zone is None):
            zone = self._utm_estimate_zone(east)
        northern = True if north > 0 else False
        latitude, longitude = utm.to_latlon(east, np.abs(north), zone, northern=northern)
        return np.longdouble(latitude), np.longdouble(longitude)
    
    def _to_utm(self, latitude, longitude):
        east, north, zone, zone_letter = utm.from_latlon(latitude, longitude)
        east = np.longdouble(east)
        north = np.longdouble(north)
        north = north if (zone_letter >= 'N') else np.longdouble(-1.0)*north
        return east, north, zone

    def _utm_estimate_zone(self, east):
        earth_circumference = 40075017.0 # m
        if isinstance(east, list):
            zone = []
            for e in east:
                zone.append(self._utm_estimate_zone(e))
        else:
            zone = np.ceil(earth_circumference/np.float64(east))-30 # subtract 30, beacuse the zones starts west of the US
        return np.int(zone)

    def distance(self, y, method=None):
        # Distance between self and point y

        if (method is None):
            method = 'utm'
        
        if (method == 'utm'):
            distance = np.sqrt((self.east-y.east)**2 + (self.north - y.north)**2)
        elif(method == 'vincenty'):
            pass
        else:
            pass

        return distance
        

    @staticmethod
    def midpoint(P, method=None):
        # Returns the midpoint between self and the points in list P
        #   method: geographic, min_distance, average, utm
        #       geographic      ...
        #       min_distance    ...
        #       average         Calculate the average using sum(points.latlon)/len(points)
        #       utm             Calculate the average using sum(points.utm)/len(points)
        # For more info, see: http://www.geomidpoint.com/calculation.html

        if not isinstance(P,list) and not isinstance(P, Point):
            TypeError('Expected P to be either a list or a Point.')

        if not isinstance(P,list):
            P = [P]

        # if (self.latitude is not None):
        #     P = self + P

        if (method is None):
            method = 'geographic'

        method = method.lower()
            
        if (method == 'geographic'):
            # step 1: Convert to cartesian coordinates
            latitudes  = np.asarray([p.latitude for p in P])*np.pi/180.0
            longitudes = np.asarray([p.longitude for p in P])*np.pi/180.0

            X = np.multiply(np.cos(latitudes), np.cos(longitudes))
            Y = np.multiply(np.cos(latitudes), np.sin(longitudes))
            Z = np.sin(latitudes)

            # Step 2: calculate arithmetic mean of cartesian coordinates
            x = np.mean(X)
            y = np.mean(Y)
            z = np.mean(Z)

            # Step 3: Convert mean back to latitude-longitude coordinates
            longitude = np.arctan2(y, x)*180.0/np.pi
            hyp = np.sqrt(x**2 + y**2)
            latitude = np.arctan2(z, hyp)*180.0/np.pi

            point_dict = {'latitude': latitude, 'longitude': longitude}

        elif (method == 'min_distance'):
            pass
        elif (method == 'average'):
            pass
        elif (method == 'utm'):
            easts = np.asarray([p.east for p in P])
            norths = np.asarray([p.north for p in P])
            east = np.mean(easts)
            north = np.mean(norths)
            point_dict = {'east': east, 'north': north}
        else:
            NotImplementedError('Unknown method (' + str(method) + ') for calculating midpoint.')

        return Point(**point_dict)
# End of class Point