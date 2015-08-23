#include <cstdio>
#include <algorithm>
#include <stack>
#include <limits>
#define MAXN 1000
#define INF numeric_limits<double>::infinity()
using namespace std;

struct Point {
	int x, y;
	bool operator < (const Point& that) const {
		return x < that.x;
	}
} points[MAXN + 1];

// Used for computing E[i][j] which is the square error of a segment
// that is best fit to the points {points[i], points[i+1], ..., points[j]}

// cumulative_x[i] is sum(points[j].x) for 1 <= j <= i
// cumulative_y[i] is sum(points[j].y) for 1 <= j <= i
// cumulative_xy[i] is sum(points[j].x * points[j].y) for 1 <= j <= i
// cumulative_xSqr[i] is sum(points[j].x * points[j].x) for 1 <= j <= i

// slope[i][j] is the slope of the segment that is best fit to
// the points {points[i], points[i+1], ..., points[j]}

// intercept[i][j] is the y-intercept of the segment that is best fit to
// the points {points[i], points[i+1], ..., points[j]}

// E[i][j] is the square error of the segment that is best fit to
// the points {points[i], points[i+1], ..., points[j]}

long long cumulative_x[MAXN + 1], cumulative_y[MAXN + 1], cumulative_xy[MAXN + 1], cumulative_xSqr[MAXN + 1];
double slope[MAXN + 1][MAXN + 1], intercept[MAXN + 1][MAXN + 1], E[MAXN + 1][MAXN + 1];

// OPT[i] is the optimal solution (minimum cost) for the points {points[1], points[2], ..., points[i]}
double OPT[MAXN + 1];

// [opt_segment[i], i] is the last segment in the optimal solution
// for the points {points[1], points[2], ..., points[i]}
int opt_segment[MAXN + 1];

int main()	{
	int N, i, j, k, interval;
	long long x_sum, y_sum, xy_sum, xsqr_sum, num, denom;
	double tmp, mn, C;

	printf("Enter the cost of creating a new segment : ");
	scanf("%lf", &C);

	printf("Enter points in the format x y on each line:\n");
	N = 0;
  i = 0;

	while (true) {
		i++;
		int result = scanf("%d %d", &points[i].x, &points[i].y);
		if ( 2 != result ) {
			break;
		}
		N++;

	}
	printf("Got %d points\n", N);

	// sort the points in non-decreasing order of x coordinate
	sort (points + 1, points + N + 1);

	// precompute the error terms
	cumulative_x[0] = cumulative_y[0] = cumulative_xy[0] = cumulative_xSqr[0] = 0;
	for (j = 1; j <= N; j++)	{
		cumulative_x[j] = cumulative_x[j-1] + points[j].x;
		printf("Set cumulative_x[%d] to %d\n", j, cumulative_x[j]);

		cumulative_y[j] = cumulative_y[j-1] + points[j].y;
		printf("Set cumulative_y[%d] to %d\n", j, cumulative_y[j]);

		cumulative_xy[j] = cumulative_xy[j-1] + points[j].x * points[j].y;
		printf("Set cumulative_xy[%d] to %d\n", j, cumulative_xy[j]);

		cumulative_xSqr[j] = cumulative_xSqr[j-1] + points[j].x * points[j].x;
		printf("Set cumulative_xSqr[%d] to %d\n", j, cumulative_xSqr[j]);

		for (i = 1; i <= j; i++)	{
			interval = j - i + 1;
			x_sum = cumulative_x[j] - cumulative_x[i-1];
			y_sum = cumulative_y[j] - cumulative_y[i-1];
			xy_sum = cumulative_xy[j] - cumulative_xy[i-1];
			xsqr_sum = cumulative_xSqr[j] - cumulative_xSqr[i-1];

			num = interval * xy_sum - x_sum * y_sum;

			printf("The Num is %d, the j is %d, the i is %d: %d, %d, %d, %d\n", num, j, i, interval, xy_sum, x_sum, y_sum);

			if (num == 0)
				slope[i][j] = 0.0;
			else {
				denom = interval * xsqr_sum - x_sum * x_sum;
				slope[i][j] = (denom == 0) ? INF : (num / double(denom));
			}
			intercept[i][j] = (y_sum - slope[i][j] * x_sum) / double(interval);

			printf("Setting intercept[i][j] to %f\n", intercept[i][j]);

			for (k = i, E[i][j] = 0.0; k <= j; k++)	{
				tmp = points[k].y - slope[i][j] * points[k].x - intercept[i][j];
				E[i][j] += tmp * tmp;
				printf("Setting E[i][j] to %f\n", E[i][j]);
			}
		}
	}

	// find the cost of the optimal solution
	OPT[0] = opt_segment[0] = 0;
	for (j = 1; j <= N; j++)	{
		for (i = 1, mn = INF, k = 0; i <= j; i++)	{
			tmp = E[i][j] + OPT[i-1];
			if (tmp < mn)	{
				mn = tmp;
				k = i;
			}
		}
		OPT[j] = mn + C;
		printf("Setting OPT[j] to %f\n", OPT[j]);
		opt_segment[j] = k;
		printf("Setting opt_segment[j] to %d\n", opt_segment[j]);
	}

	printf("\nCost of the optimal solution : %lf\n", OPT[N]);

	// find the optimal solution
	stack <int> segments;
	for (i = N, j = opt_segment[N]; i > 0; i = j-1, j = opt_segment[i])	{
		printf("Pushing %d\n", i);
		segments.push(i);
		printf("Pushing %d\n", j);
		segments.push(j);
	}

	printf("\nAn optimal solution :\n");
	while (!segments.empty())	{
		i = segments.top(); segments.pop();
		j = segments.top(); segments.pop();

		printf("i is %d, j is %d\n", i, j);
		int t,s;
		for (t=0; t < 3; t++) {
			for (s=0; s < 3; s++) {
				printf("Intercepts at [%d][%d] is %f\n", t, s, intercept[t][s]);
			}
		}

		printf("Segment (y = %lf * x + %lf) from point #%d: %d %d to point #%d: %d %d with square error %lf.\n",
				slope[i][j], intercept[i][j], i, points[i].x, points[i].y, j, points[j].x, points[j].y, E[i][j]);
	}

	return 0;
}
