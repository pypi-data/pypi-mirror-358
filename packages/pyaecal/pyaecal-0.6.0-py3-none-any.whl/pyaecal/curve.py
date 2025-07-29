#  Copyright (c) 2017-2023 Jeorme Douay <jerome@far-out.biz>
#  All rights reserved.

import numpy as np
import pwlf
import polars as pl
from .axis import Axis

"""
Curve Class
"""

class Curve(object):
    """
    Curve allows the definition and extrapolation of data of a curve.

    This class is usually returned by the DCM class after importing a file.
    """

    def __init__(self, x, y, name="curve"):
        if isinstance(x, Axis):
            self._x = x
        else:
            self._x = Axis(x, name + '_x')
        self._y = y  # array of values
        self.name = name
        self.size = len(self._x.values)  # Initialize size to the length of x-axis data

    def set_size(self, new_size):
        """
        Update the number of points in the curve and refit the curve to the new size.

        :param new_size: New number of points for the curve (must be positive)
        :return: None
        """
        if not isinstance(new_size, int) or new_size < 1:
            raise ValueError("new_size must be a positive integer")
        
        self.size = new_size
        # Refit the curve to the new size
        x_values = np.array(self._x.values)
        y_values = np.array(self._y)
        
        # If no points exist, create a default flat line
        if len(x_values) == 0:
            x_values = np.linspace(0, 1, self.size)
            y_values = np.zeros(self.size)
        else:
            # Generate new x range with the specified size
            x_min = np.min(x_values)
            x_max = np.max(x_values)
            x_new_range = np.linspace(x_min, x_max, self.size)
            # Interpolate y values if necessary to match new size
            if len(x_values) != self.size:
                y_values = np.interp(x_new_range, x_values, y_values)
            else:
                y_values = y_values[:self.size]  # Truncate if necessary
            
            # Use pwlf to refit the curve
            my_pwlf = pwlf.PiecewiseLinFit(x_values, y_values)
            my_pwlf.fit(self.size)
            y_fitted = my_pwlf.predict(x_new_range)
            y_values = y_fitted

        # Update the curve's x and y values
        self._x.values = x_new_range.tolist()
        self._y = y_values.tolist()

    def insert(self, x, y, y_min=None, y_max=None, weight=1):
        """
        Insert or update points defined by x and y values, maintaining a monotonous x-axis.
        The number of points remains identical to self.size, and the curve is refitted using pwlf to minimize errors.
        If y_min and/or y_max are provided, discards points with y values below y_min or above y_max,
        then updates the curve by adjusting y values around each point.
        
        :param x: Polars Series or list of x values to insert or update
        :param y: Polars Series or list of y values corresponding to x
        :param y_min: Minimum y value (optional, discards points below this value if provided)
        :param y_max: Maximum y value (optional, discards points above this value if provided)
        :param weight: Weight for the update (optional, default=1, used only when y_min or y_max is provided)
        :return: None
        """
        # Convert inputs to lists if they are Polars Series
        if isinstance(x, pl.Series):
            x = x.to_list()
        if isinstance(y, pl.Series):
            y = y.to_list()

        # Validate input lengths
        if len(x) != len(y):
            raise ValueError("x and y must have the same length")

        # Convert x and y values to numpy arrays
        x_values = np.array(self._x.values)
        y_values = np.array(self._y)

        # Filter out points outside y_min and/or y_max if provided
        if y_min is not None or y_max is not None:
            mask = np.ones(len(y_values), dtype=bool)
            if y_min is not None:
                mask &= y_values >= y_min
            if y_max is not None:
                mask &= y_values <= y_max
            x_values = x_values[mask]
            y_values = y_values[mask]

        # If y_min or y_max is provided, perform update behavior for each point
        if y_min is not None or y_max is not None:
            for x_new, y_new in zip(x, y):
                # Skip points that don't satisfy y_min or y_max
                if (y_min is not None and y_new < y_min) or (y_max is not None and y_new > y_max):
                    continue
                delta = (y_new - self.y(x_new)) / weight
                for i in range(len(x_values)):
                    _xi = x_values[i]
                    alpha = np.arctan((_xi - x_new) / delta)
                    y_values[i] += np.cos(alpha) * delta
                    if y_min is not None:
                        y_values[i] = max(y_values[i], y_min)
                    if y_max is not None:
                        y_values[i] = min(y_values[i], y_max)
        else:
            # Insert the new points
            for x_new, y_new in zip(x, y):
                insert_idx = np.searchsorted(x_values, x_new)
                x_values = np.insert(x_values, insert_idx, x_new)
                y_values = np.insert(y_values, insert_idx, y_new)

        # Ensure x_values are strictly monotonous (increasing)
        x_values, indices = np.unique(x_values, return_index=True)
        y_values = y_values[indices]

        # If no points remain after filtering, use a flat line at y=0
        if len(x_values) == 0:
            x_values = np.linspace(0, 1, self.size)
            y_values = np.zeros(self.size)
        # If too few points, interpolate to restore size
        elif len(x_values) < self.size:
            x_new_range = np.linspace(np.min(x_values), np.max(x_values), self.size)
            y_values = np.interp(x_new_range, x_values, y_values)
            x_values = x_new_range
        # If too many points, proceed to fit with pwlf to reduce to size

        # Update min and max of x-axis
        x_min = np.min(x_values)
        x_max = np.max(x_values)

        # Generate new x values with the specified size
        x_new_range = np.linspace(x_min, x_max, self.size)

        # Use pwlf for piecewise linear fitting
        my_pwlf = pwlf.PiecewiseLinFit(x_values, y_values)
        my_pwlf.fit(self.size)
        # Predict y values for the new x range
        y_fitted = my_pwlf.predict(x_new_range)

        # Update the curve's x and y values
        self._x.values = x_new_range.tolist()
        self._y = y_fitted.tolist()

    def y(self, x):
        """
        Interpolate the y value for a given x.
        
        :param x: x value to interpolate
        :return: Interpolated y value
        """
        x_table = self._x.values
        z_table = self._y
        if x <= x_table[0]:
            return z_table[0]
        if x >= x_table[len(x_table) - 1]:
            return z_table[len(z_table) - 1]

        # Linear search
        i = 1
        while x > x_table[i]:
            i += 1

        Aux_ = z_table[i - 1]
        Aux__a = z_table[i]

        # Interpolation
        Aux__b = x - x_table[i - 1]
        Aux__c = x_table[i] - x_table[i - 1]

        if Aux_ <= Aux__a:
            # Positive slope
            Aux_ += ((Aux__a - Aux_) * Aux__b) / Aux__c
        else:
            # Negative slope
            Aux_ -= ((Aux_ - Aux__a) * Aux__b) / Aux__c

        return Aux_

    def fraction(self, x_table, N, x):
        """
        Find the index and fraction of x in x_table.

        :param x_table: Table of x values
        :param N: Length of array
        :param x: Value to search for
        :return: Tuple of (irx, fraction) where irx is the index and fraction is the position between irx and irx+1
        """
        if x <= x_table[0]:
            irx = 0
            fraction = 0
        elif x >= x_table[N - 1]:
            irx = N - 1
            fraction = 0
        else:
            Aux_ = 0
            x_table_index = 0
            while x >= x_table[x_table_index]:
                Aux_ += 1
                x_table_index += 1

            x_table_index -= 1
            irx = Aux_
            fraction = int(
                ((x - x_table[x_table_index]) << 8)
                / (x_table[x_table_index + 1] - x_table[x_table_index])
            )
        return irx, fraction