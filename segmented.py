import numpy

# Describes a 2D point with an X and a Y coordinate
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
		returns.append([i,j])

	return returns
# Read Input and run algo
points = []
print("Enter the cost of creating a new segment")

C = int(raw_input());
print("Enter points in the format x y on each line:")

while (True) :
	try:
		coords = raw_input().split(" ")
		points.append(Point(int(coords[0]),int(coords[1])))
	except (EOFError):
		break
	except (ValueError):
		break

ret = segmented(points, C)

# for seg in ret:
# 	print "Segment point #%d to point #%d.\n" % (seg[0], seg[1])
