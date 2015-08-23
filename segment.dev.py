#include <cstdio>
#include <algorithm>
#include <stack>
#include <limits>
#define MAXN 1000
#define INF numeric_limits<double>::infinity()
# using namespace std;
#
# struct Point {
# 	int x, y;
# 	bool operator < (const Point& that) const {
# 		return x < that.x;
# 	}
# } points[MAXN + 1];
import numpy

class Point:
	""" Point class represents and manipulates x,y coords. """

	def __init__(self, x, y):
		""" Create a new point at the origin """
		self.x = x
		self.y = y

	def __lt__(self, other):
		return self.x < other.x

	def ___le__(self, other):
		return self.x <= other.x

	def __eq__(self, other):
		return self.x == other.x

	def __ne__(self, other):
		return self.x != other.x

	def __gt__(self, other):
		return self.x > other.x

	def __ge__(self, other):
		return self.x >= other.x

def segmented(points,C):
# // Used for computing E[i][j] which is the square error of a segment
# // that is best fit to the points {points[i], points[i+1], ..., points[j]}
#
# // cumulative_x[i] is sum(points[j].x) for 1 <= j <= i
# // cumulative_y[i] is sum(points[j].y) for 1 <= j <= i
# // cumulative_xy[i] is sum(points[j].x * points[j].y) for 1 <= j <= i
# // cumulative_xSqr[i] is sum(points[j].x * points[j].x) for 1 <= j <= i
#
# // slope[i][j] is the slope of the segment that is best fit to
# // the points {points[i], points[i+1], ..., points[j]}
#
# // intercept[i][j] is the y-intercept of the segment that is best fit to
# // the points {points[i], points[i+1], ..., points[j]}
#
# // E[i][j] is the square error of the segment that is best fit to
# // the points {points[i], points[i+1], ..., points[j]}

# long long cumulative_x[MAXN + 1], cumulative_y[MAXN + 1], cumulative_xy[MAXN + 1], cumulative_xSqr[MAXN + 1];
# double slope[MAXN + 1][MAXN + 1], intercept[MAXN + 1][MAXN + 1], E[MAXN + 1][MAXN + 1];




# // OPT[i] is the optimal solution (minimum cost) for the points {points[1], points[2], ..., points[i]}
# double OPT[MAXN + 1];

# // [opt_segment[i], i] is the last segment in the optimal solution
# // for the points {points[1], points[2], ..., points[i]}
#int opt_segment[MAXN + 1];
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

	print "Total of %d points\n" % N

	# sort the points in non-decreasing order of x coordinate
	# sort (points + 1, points + N + 1);

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
	for j in range(1,N+1):
		print cumulative_x
		print points
		print j

		cumulative_x[j] = cumulative_x[j-1] + points[j-1].x;
		print("Set cumulative_x[%d] to %d\n" % (j, cumulative_x[j]));

		cumulative_y[j] = cumulative_y[j-1] + points[j-1].y;
		print("Set cumulative_y[%d] to %d\n" % (j, cumulative_y[j]));

		cumulative_xy[j] = cumulative_xy[j-1] + points[j-1].x * points[j-1].y;
		print("Set cumulative_xy[%d] to %d\n" % (j, cumulative_xy[j]));

		cumulative_xSqr[j] = cumulative_xSqr[j-1] + points[j-1].x * points[j-1].x;
		print("Set cumulative_xSqr[%d] to %d\n" % (j, cumulative_xSqr[j]));


		for i in range(1,j+1):
			interval = j - i + 1
			x_sum = cumulative_x[j] - cumulative_x[i-1]
			print "cumulative_y[i-1] is %d" % cumulative_y[i-1]
			print "cumulative_y[j] is %d" % cumulative_y[j]
			y_sum = cumulative_y[j] - cumulative_y[i-1]
			xy_sum = cumulative_xy[j] - cumulative_xy[i-1]
			xsqr_sum = cumulative_xSqr[j] - cumulative_xSqr[i-1]

			num = interval * xy_sum - x_sum * y_sum

			print("The Num is %d, the j is %d, the i is %d: %d, %d, %d, %d\n" % (num, j, i, interval, xy_sum, x_sum, y_sum))
			print(cumulative_x)

			if (num == 0):
				slope[i][j] = 0.0
			else:
				denom = interval * xsqr_sum - x_sum * x_sum

				slope[i][j] = INF if (denom == 0) else (num / denom)

			intercept[i][j] = (y_sum - slope[i][j] * x_sum) / interval
			print("Setting intercept[%d][%d] to %d" % (i,j,intercept[i][j]))
			E[i][j] = 0.0
			for k in range(i,j+1):
				tmp = points[k-1].y - slope[i][j] * points[k-1].x - intercept[i][j];
				E[i][j] += tmp * tmp;

	# // find the cost of the optimal solution
	OPT = [None]*(N+1)
	opt_segment = [None]*(N+1)
	print E
	OPT[0] = opt_segment[0] = 0;
	for j in range(1, N+1):
		mn = INF
		k = 0
		for i in range(1, j+1):
			tmp = E[i][j] + OPT[i-1];
			if (tmp < mn) :
				mn = tmp
				k = i

		OPT[j] = mn + C
		print("Setting OPT[j] to %d" % OPT[j])
		opt_segment[j] = k
		print("Setting opt_segment[j] to %d" % opt_segment[j])



	print "\nCost of the optimal solution : %lf\n" % OPT[N]

	# // find the optimal solution
	segments = []
	i = N
	j = opt_segment[N]
	while (i > 0):
		print "Pushing " + str(i)
		segments.append(i)
		print "Pushing " + str(j)
		segments.append(j)
		i = j-1
		j = opt_segment[i]

	print "\nAn optimal solution :\n"
	while (segments != []):
		i = segments.pop()
		print "Popped " + str(i)
		j = segments.pop()
		print "Popped " + str(j)
		print intercept
		print slope
		print "Segment (y = %f * x + %f) from point #%d: %d %d to point #%d: %d %d with square error %lf.\n" % (slope[i][j], intercept[i][j], i, points[i-1].x, points[i-1].y, j, points[j-1].x, points[j-1].y, E[i][j])


points = []
C = int(raw_input());

while (True) :
	try:
		coords = raw_input().split(" ")
		points.append(Point(int(coords[0]),int(coords[1])))
	except (EOFError):
		break
	except (ValueError):
		break
segmented(points, C)
