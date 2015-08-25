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
    context.lookback = 50
    
    # The percent difference between the min and max slopes to tolerate in order to call it a flag
    # context.flag_tolerance = .1
    context.flag_tolerance_degrees = 10
    
    # The absolute tolerance that a flag's min-max avg slope must be in order to hold the stock
    context.min_positive_slope = .1
    
    # The cost of creating a new segment in segmented least squares
    context.segment_cost = 2

def handle_data(context, data):
    high_history = history(bar_count=context.lookback, frequency="1d", field='high')
    low_history = history(bar_count=context.lookback, frequency="1d", field='low')
    buys = []
    # For each stock lets compute the slope of mins and the slope of maxes
    # O(s)
    for security in data:

        # Calculate the relative slopes (They aren't the exact slopes but they are accurate relative to each other)
        
        
        points = convert_to_points(high_history[security])
        
        print segmented(points, context.segment_cost)
        
        slope_high = calc_slope(high_history[security], context.lookback) # O(d)
        slope_low = calc_slope(low_history[security], context.lookback) # O(d)
        
        # Check whether the min slope is almost equal to the max slope.
        # if within_percent_tolerance(slope_low, slope_high, context.flag_tolerance):
        degrees_between = angle_between_slopes(slope_low, slope_high)
        if degrees_between < context.flag_tolerance_degrees:
            
            # Average the min and max slopes just to get a better idea
            avg_high_low_slope = np.mean([slope_low,slope_high])
            if avg_high_low_slope > context.min_positive_slope:
                log.warn("%s: SLOPE_LOW: %s SLOPE_HIGH: %s AVG: %s" % (security,slope_low,slope_high,avg_high_low_slope))
                buys.append(security)
                
                
    log.info("================END OF DAY================")
    
    
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

    print "Got %d points" % N

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


    print "Cost of the optimal solution : %lf" % OPT[N]

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

    print "\nAn optimal solution :"
    returns = []
    # O(n)
    while (segments != []):
        i = segments.pop()
        j = segments.pop()
        print "Segment (y = %f * x + %f) from point #%d: %d %d to point #%d: %d %d with square error %lf." % (slope[i][j], intercept[i][j], i, points[i-1].x, points[i-1].y, j, points[j-1].x, points[j-1].y, E[i][j])
        returns.append([i-1,j-1])

    return returns



# # Read Input and run algo
# points = []
# print("Enter the cost of creating a new segment")

# C = int(raw_input());
# print("Enter points in the format x y on each line:")

# while (True) :
#     try:
#         coords = raw_input().split(" ")
#         points.append(Point(int(coords[0]),int(coords[1])))
#     except (EOFError):
#         break
#     except (ValueError):
#         break

# ret = segmented(points, C)

# # for seg in ret:
# #     print "Segment point #%d to point #%d.\n" % (seg[0], seg[1])


# # This is a sample mean-reversion algorithm on Quantopian for you to test and adapt.

# # Algorithm investment thesis: 
# # Top-performing stocks from last week will do worse this week, and vice-versa.

# # Every Monday, we rank high-volume stocks based on their previous 5 day returns. 
# # We go long the bottom 20% of stocks with the WORST returns over the past 5 days.
# # We go short the top 20% of stocks with the BEST returns over the past 5 days.

# # This type of algorithm may be used in live trading and in the Quantopian Open.

# # Import the libraries we will use here
# import numpy as np

# # The initialize function is the place to set your tradable universe and define any parameters. 
# def initialize(context):
#     # Use the top 1% of stocks defined by average daily trading volume.
#     set_universe(universe.DollarVolumeUniverse(99, 100))
    
#     # Set execution cost assumptions. For live trading with Interactive Brokers 
#     # we will assume a $1.00 minimum per trade fee, with a per share cost of $0.0075. 
#     set_commission(commission.PerShare(cost=0.0075, min_trade_cost=1.00))
    
#     # Set market impact assumptions. We limit the simulation to 
#     # trade up to 2.5% of the traded volume for any one minute,
#     # and  our price impact constant is 0.1. 
#     set_slippage(slippage.VolumeShareSlippage(volume_limit=0.025, price_impact=0.10))
    
#     # Define the other variables
#     context.long_leverage = 0.5
#     context.short_leverage = -0.5
#     context.lower_percentile = 20
#     context.upper_percentile = 80
#     context.returns_lookback = 5
           
#     # Rebalance every Monday (or the first trading day if it's a holiday).
#     # At 11AM ET, which is 1 hour and 30 minutes after market open.
#     schedule_function(rebalance, 
#                       date_rules.week_start(days_offset=0),
#                       time_rules.market_open(hours = 1, minutes = 30))  

# # The handle_data function is run every bar.    
# def handle_data(context,data):    
#     # Record and plot the leverage of our portfolio over time. 
#     record(leverage = context.account.leverage)

#     # We also want to monitor the number of long and short positions 
#     # in our portfolio over time. This loop will check our positition sizes 
#     # and add the count of longs and shorts to our plot.
#     longs = shorts = 0
#     for position in context.portfolio.positions.itervalues():
#         if position.amount > 0:
#             longs += 1
#         if position.amount < 0:
#             shorts += 1
#     record(long_count=longs, short_count=shorts)

# # This rebalancing is called according to our schedule_function settings.     
# def rebalance(context,data):
#     # Get the last N days of prices for every stock in our universe.
#     prices = history(context.returns_lookback, '1d', 'price')

#     highs = history(context.returns_lookback, '1d', 'high')

#     lows = history(context.returns_lookback, '1d', 'low')

#     # Calculate the past 5 days' returns for each security.
#     returns = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]

#     avg_highs = highs.mean() # (highs.iloc[-1] - highs.iloc[0]) / highs.iloc[0]
#     avg_lows = lows.mean() # (lows.iloc[-1] - lows.iloc[0]) / lows.iloc[0]

#     slope_high = (avg_highs - put_current_high_here) / context.returns_lookback
        
#     slope_low = (avg_highs - put_current_high_here) / context.returns_lookback
#     # Remove stocks with missing prices.
#     # Remove any stocks we ordered last time that still have open orders.
#     # Get the cutoff return percentiles for the long and short portfolios.
#     returns = returns.dropna()
#     open_orders = get_open_orders()
#     if open_orders:
#         eligible_secs = [sec for sec in data if sec not in open_orders]
#         returns = returns[eligible_secs]

#     # Lower percentile is the threshhold for the bottom 20%, upper percentile is for the top 20%.
#     lower, upper = np.percentile(returns, [context.lower_percentile,
#                                            context.upper_percentile])
    
#     # Select the X% worst performing securities to go long.
#     long_secs = returns[returns <= lower]
    
#     # Select the Y% best performing securities to short.
#     short_secs = returns[returns >= upper]
    
#     # Set the allocations to even weights in each portfolio.
#     long_weight = context.long_leverage / len(long_secs)
#     short_weight = context.short_leverage / len(short_secs)
    
#     for security in data:
        
#         # Buy/rebalance securities in the long leg of our portfolio.
#         if security in long_secs:
#             order_target_percent(security, long_weight)
            
#         # Sell/rebalance securities in the short leg of our portfolio.
#         elif security in short_secs:
#             order_target_percent(security, short_weight)
            
#         # Close any positions that fell out of the list of securities to long or short.
#         else:
#             order_target(security, 0)
            
#     log.info("This week's longs: "+", ".join([long_.symbol for long_ in long_secs.index]))
#     log.info("This week's shorts: "  +", ".join([short_.symbol for short_ in short_secs.index]))
