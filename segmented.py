# This is a sample mean-reversion algorithm on Quantopian for you to test and adapt.

# Algorithm investment thesis: 
# Top-performing stocks from last week will do worse this week, and vice-versa.

# Every Monday, we rank high-volume stocks based on their previous 5 day returns. 
# We go long the bottom 20% of stocks with the WORST returns over the past 5 days.
# We go short the top 20% of stocks with the BEST returns over the past 5 days.

# This type of algorithm may be used in live trading and in the Quantopian Open.

# Import the libraries we will use here
import numpy as np
import math

def initialize(context):
    set_universe(universe.DollarVolumeUniverse(99.9, 100))
    context.lookback = 60
    
    # The percent difference between the min and max slopes to tolerate in order to call it a flag
    context.flag_tolerance_degrees = 25
    
    # The absolute tolerance that a flag's min-max avg slope must be in order to hold the stock
    context.min_positive_slope = .1
    
    # The cost of creating a new segment in segmented least squares
    context.segment_cost = 4

    context.error_threshold = 2

def handle_data(context, data):
    high_history = history(bar_count=context.lookback, frequency="1d", field='high')
    low_history = history(bar_count=context.lookback, frequency="1d", field='low')
    buys = []
    # For each stock lets compute the slope of mins and the slope of maxes
    # O(s)
    for security in data:

        # Calculate the relative slopes (They aren't the exact slopes but they are accurate relative to each other)
        points_high = convert_to_points(high_history[security])
        points_low = convert_to_points(low_history[security])
        
        segments_high = segmented(points_high, context.segment_cost)
        segments_low = segmented(points_low, context.segment_cost)
        
        if angle_between_slopes(segments_high[-1].slope, segments_low[-1].slope) < context.flag_tolerance_degrees:
            avg_slope = np.mean([segments_high[-1].slope,segments_low[-1].slope])
            if avg_slope > context.min_positive_slope:

                if segments_high[-1].sqerr < context.error_threshold and segments_high[-1].sqerr < context.error_threshold:
                    buys.append(security)


                    print("BUYING %s, S=%f, E_h=%f, E_l=%f" % (security, avg_slope, segments_high[-1].sqerr, segments_low[-1].sqerr))
                else:
                    nothing=1
                    log.warn("REJECTED %s because error is too high" % security)
            else:
                nothing=1
                log.warn("REJECTED %s not positive enough... threshold is %f" % (security, context.min_positive_slope))
        else:
            nothing=1
            print("REJECTED %s... not a flag" % security)
                
    log.info("================ END OF DAY ================")
    
    
    # If we have any buys then determine the percentage of our portfolio
    if len(buys) > 0:
        percent_per_sec = 1 / len(buys)
    else: 
        percent_per_sec = 0
        
    for security in data:
        if security in buys:
            # Invest percent_per_sec percent of our portfolio in the security
            order_target_percent(security, percent_per_sec)
        else:
            # if it isn't in the buys list, then sell it
            order_target(security, 0)

def calc_slope(dataframe, lookback):
    avg_bar = dataframe.mean()
    curr_bar = dataframe[-1]

    slope = ( curr_bar - avg_bar ) / lookback
    return slope
        
def within_percent_tolerance(num1, num2, tolerance):
    return math.fabs((num1 - num2) / num1) < tolerance and math.fabs((num2 - num1) / num2) < tolerance
       
def within_absolute_tolerance(num1, num2, tolerance):
    return math.fabs(num1 - num2) < tolerance and math.fabs(num2 - num1) < tolerance

# Applies the dot product of two slopes and returns the angle between the slopes
def angle_between_slopes(slope1, slope2):
    magnitudes = math.sqrt(1 + slope1**2) * math.sqrt(1 + slope2**2)
    dot_product = 1 + slope1*slope2
    alpha_in_radians = math.acos(clean_cos(dot_product / magnitudes))
    return math.degrees(alpha_in_radians)
    
def clean_cos(cos_angle):
    return min(1,max(cos_angle,-1))

def convert_to_points(history): 
    points = []
    i = 0
    for value in history:
        p = Point(i,value)
        points.append(p)
        i = i+1
    return points
    
    
#####################################
# Segmented Least Squares Algorithm #
#####################################

import numpy

# Describes a 2D point with an X and a Y coordinate
class Point:
    """ Point class represents and manipulates x,y coords. """

    def __init__(self, x, y):
        """ Create a new point at the origin """
        self.x = x
        self.y = y
        
    def __str__(self):
        return "x: %f, y: %f" % (self.x, self.y)
    
    def __repr__(self):
        return self.__str__()
    
    
    
class Segment:
    def __init__(self, p1, p2, slope, intercept, sqerr):
        self.p1 = p1
        self.p2 = p2
        self.slope = slope
        self.intercept = intercept
        self.sqerr = sqerr

    def __str__(self):
        return "POINT 1: %s, POINT 2: %s" % (self.p1, self.p2)
    
    def __repr__(self):
        return self.__str__()
    
# Takes a list of Point Objects (Ordered by X in ASC order) and a Constant C
def segmented(points,C):
    N = i = j = k = interval = 0
    x_sum = 0
    y_sum = 0
    xy_sum = 0
    xsqr_sum = 0
    num = 0
    denom = 0
    tmp = 0.0
    mn = 0.0
    INF = 99999999999999
    N = len(points)

    # Multi dimentional array that is N*N in size
    slope = numpy.zeros((N+1, N+1))
    intercept = numpy.zeros((N+1, N+1))
    E = numpy.zeros((N+1, N+1))

    # precompute the error terms
    cumulative_x = [None]*(N+1)
    cumulative_y = [None]*(N+1)
    cumulative_xy = [None]*(N+1)
    cumulative_xSqr = [None]*(N+1)
    cumulative_x[0] = cumulative_y[0] = cumulative_xy[0] = cumulative_xSqr[0] = 0
    
    # O(n^3)
    for j in range(1,N+1):
        cumulative_x[j] = cumulative_x[j-1] + points[j-1].x;
        cumulative_y[j] = cumulative_y[j-1] + points[j-1].y;
        cumulative_xy[j] = cumulative_xy[j-1] + points[j-1].x * points[j-1].y;
        cumulative_xSqr[j] = cumulative_xSqr[j-1] + points[j-1].x * points[j-1].x;
        # O(n^2)
        for i in range(1,j+1):
            interval = j - i + 1
            x_sum = cumulative_x[j] - cumulative_x[i-1]
            y_sum = cumulative_y[j] - cumulative_y[i-1]
            xy_sum = cumulative_xy[j] - cumulative_xy[i-1]
            xsqr_sum = cumulative_xSqr[j] - cumulative_xSqr[i-1]

            num = interval * xy_sum - x_sum * y_sum

            if (num == 0):
                slope[i][j] = 0.0
            else:
                denom = interval * xsqr_sum - x_sum * x_sum
                slope[i][j] = INF if (denom == 0) else (num / float(denom))

            intercept[i][j] = (y_sum - slope[i][j] * x_sum) / interval

            E[i][j] = 0.0
            
            # O(n)
            for k in range(i,j+1):
                tmp = points[k-1].y - slope[i][j] * points[k-1].x - intercept[i][j]
                E[i][j] += tmp * tmp;



    # find the cost of the optimal solution
    OPT = [None]*(N+1)
    opt_segment = [None]*(N+1)
    OPT[0] = 0
    opt_segment[0] = 0;
    
    # O(n)
    for j in range(1, N+1):
        mn = INF
        k = 0
        for i in range(1, j+1):
            tmp = E[i][j] + OPT[i-1];
            if (tmp < mn) :
                mn = tmp
                k = i

        OPT[j] = mn + C
        opt_segment[j] = k

    # find the optimal solution
    segments = []
    i = N
    j = opt_segment[N]
    # O(n)
    while (i > 0):
        segments.append(i)
        segments.append(j)
        i = j-1
        j = opt_segment[i]

    returns = []
    # O(n)
    while (segments != []):
        i = segments.pop()
        j = segments.pop()
        print "Segment (y = %f * x + %f) from point #%d: %d %d to point #%d: %d %d with square error %lf." % (slope[i][j], intercept[i][j], i, points[i-1].x, points[i-1].y, j, points[j-1].x, points[j-1].y, E[i][j])
        returns.append(Segment(points[i-1], points[j-1],slope[i][j], intercept[i][j], E[i][j]))

    return returns
