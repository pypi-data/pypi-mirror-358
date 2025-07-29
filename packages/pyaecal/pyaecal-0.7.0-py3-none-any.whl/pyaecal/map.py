#  Copyright (c) 2017-2025 [Your Name]
#  All rights reserved.

import numpy as np
import polars as pl
from scipy.interpolate import RegularGridInterpolator
from .axis import Axis

"""
Map Class
"""

class Map(object):
    """
    Map allows the definition and extrapolation of a 3D surface (x, y, z).

    This class is designed for 3D table manipulation, typically used in automotive calibration.
    The map extends its initial size with new points instead of resizing, removing duplicates, and all data is retained internally.
    """

    def __init__(self, x, y, z, name="map"):
        """
        Initialize the Map with x, y, and z data.
        
        :param x: List or array of x-axis values
        :param y: List or array of y-axis values
        :param z: 2D list or array of z values corresponding to the (x, y) grid
        :param name: Name of the map (default: "map")
        """
        if isinstance(x, Axis):
            self._x = x
        else:
            self._x = Axis(x, name + '_x')
        if isinstance(y, Axis):
            self._y = y
        else:
            self._y = Axis(y, name + '_y')
        self._z = np.array(z)  # 2D array of z values
        self.name = name
        self.size_x = len(self._x.values)  # Number of points along x-axis
        self.size_y = len(self._y.values)  # Number of points along y-axis
        self.initial_x = np.array(x)  # Store initial x values
        self.initial_y = np.array(y)  # Store initial y values
        self.poly_coeffs = None  # Store polynomial coefficients for best-fit
        self.x_min, self.x_max = min(self._x.values), max(self._x.values)
        self.y_min, self.y_max = min(self._y.values), max(self._y.values)
        
        # Validate dimensions
        if self._z.shape != (self.size_y, self.size_x):
            raise ValueError(f"z must be a 2D array of shape ({self.size_y}, {self.size_x})")
        
        # Initial surface fit
        self.fit_surface(degree=3)

    def fit_surface(self, degree=3):
        """
        Fit a polynomial surface to the (x, y, z) data to create a best-fit function.

        :param degree: Degree of the polynomial to fit (default: 3)
        :return: None
        """
        x_values = np.array(self._x.values)
        y_values = np.array(self._y.values)
        z_values = self._z.flatten()
        
        # Normalize x and y to [0, 1]
        x_normalized = (x_values - self.x_min) / (self.x_max - self.x_min)
        y_normalized = (y_values - self.y_min) / (self.y_max - self.y_min)
        
        # Create a meshgrid for polynomial fitting
        X, Y = np.meshgrid(x_normalized, y_normalized)
        X_flat = X.flatten()
        Y_flat = Y.flatten()
        
        # Create the design matrix for a 2D polynomial
        terms = []
        for i in range(degree + 1):
            for j in range(degree + 1 - i):
                terms.append((X_flat ** i) * (Y_flat ** j))
        design_matrix = np.vstack(terms).T
        
        # Validate dimensions
        if design_matrix.shape[0] != len(z_values):
            raise ValueError(f"Design matrix rows ({design_matrix.shape[0]}) must match z values ({len(z_values)})")
        
        # Solve for polynomial coefficients using least squares
        coeffs, _, _, _ = np.linalg.lstsq(design_matrix, z_values, rcond=None)
        self.poly_coeffs = coeffs.flatten()  # Ensure 1D array

    def evaluate_best_fit(self, x, y):
        """
        Evaluate the best-fit polynomial surface at a given (x, y) point.

        :param x: x value to evaluate
        :param y: y value to evaluate
        :return: Predicted z value
        """
        if self.poly_coeffs is None:
            raise ValueError("Best-fit surface not computed. Call fit_surface() first.")
        
        # Normalize input x and y
        x_normalized = (x - self.x_min) / (self.x_max - self.x_min)
        y_normalized = (y - self.y_min) / (self.y_max - self.y_min)
        
        # Compute the polynomial value
        num_coeffs = len(self.poly_coeffs)
        degree = int(np.sqrt(num_coeffs * 2 + 0.25) - 0.5)  # Reverse calculate degree
        z_pred = 0
        idx = 0
        for i in range(degree + 1):
            for j in range(degree + 1 - i):
                if idx < num_coeffs:
                    z_pred += self.poly_coeffs[idx] * (x_normalized ** i) * (y_normalized ** j)
                    idx += 1
        return z_pred

    def insert(self, x, y, z):
        """
        Extend the initial size of the table with the new points, remove duplicates, and refit the curve.
        
        :param x: Polars Series or list of x values to insert or update
        :param y: Polars Series or list of y values to insert or update
        :param z: Polars Series or list of z values corresponding to (x, y) points
        :return: Updated z values for the extended x and y grid
        """
        # Convert inputs to lists if they are Polars Series
        if isinstance(x, pl.Series):
            x = x.to_list()
        if isinstance(y, pl.Series):
            y = y.to_list()
        if isinstance(z, pl.Series):
            z = z.to_list()

        # Validate input lengths
        if len(x) != len(y) or len(y) != len(z):
            raise ValueError("x, y, and z must have the same length")

        # Extend x and y with new points and remove duplicates
        self._x.values = np.unique(np.append(self._x.values, x))
        self._y.values = np.unique(np.append(self._y.values, y))
        self.size_x = len(self._x.values)
        self.size_y = len(self._y.values)
        # Update min/max for normalization
        self.x_min, self.x_max = min(self._x.values), max(self._x.values)
        self.y_min, self.y_max = min(self._y.values), max(self._y.values)

        # Generate initial z values using polynomial coefficients for the extended grid
        X, Y = np.meshgrid(self._x.values, self._y.values)
        z_new = np.zeros((self.size_y, self.size_x))
        for i in range(self.size_y):
            for j in range(self.size_x):
                z_new[i, j] = self.evaluate_best_fit(X[i, j], Y[i, j])

        # Replace the points with the points to be inserted
        for x_new, y_new, z_new_val in zip(x, y, z):
            x_idx = np.searchsorted(self._x.values, x_new)
            y_idx = np.searchsorted(self._y.values, y_new)
            # Clamp indices to the valid range (0 to size-1)
            x_idx = max(0, min(x_idx, self.size_x - 1))
            y_idx = max(0, min(y_idx, self.size_y - 1))
            z_new[y_idx, x_idx] = z_new_val  # Safe access due to clamping

        # Update the map's z values temporarily
        self._z = z_new

        # Refit the curve with the new points
        self.fit_surface(degree=3)

        # Recalculate z values based on the new fit
        X, Y = np.meshgrid(self._x.values, self._y.values)
        z_recalculated = np.zeros((self.size_y, self.size_x))
        for i in range(self.size_y):
            for j in range(self.size_x):
                z_recalculated[i, j] = self.evaluate_best_fit(X[i, j], Y[i, j])

        # Update the map's z values with the recalculated fit
        self._z = z_recalculated

        # Return the updated z values for the extended grid
        return self._z

    def create_new_map(self, x, y):
        """
        Create a new Map instance with specified x and y arrays, generating z values from the refitted surface.
        
        :param x: List or array of new x-axis values
        :param y: List or array of new y-axis values
        :return: New Map instance with computed z values
        """
        if isinstance(x, Axis):
            new_x = x
        else:
            new_x = Axis(x, self.name + '_new_x')
        if isinstance(y, Axis):
            new_y = y
        else:
            new_y = Axis(y, self.name + '_new_y')
        
        new_size_x = len(new_x.values)
        new_size_y = len(new_y.values)
        X, Y = np.meshgrid(new_x.values, new_y.values)
        grid_points = np.vstack((Y.flatten(), X.flatten())).T
        
        # Interpolate z values using the current fit
        interp = RegularGridInterpolator(
            (self._y.values, self._x.values), self._z,
            method='linear', bounds_error=False, fill_value=0
        )
        z_new = interp(grid_points).reshape(new_size_y, new_size_x)
        
        # Create and return new Map instance
        return Map(x=new_x.values, y=new_y.values, z=z_new, name=self.name + "_new")

    def z(self, x, y):
        """
        Interpolate the z value for a given (x, y) point.
        
        :param x: x value to interpolate
        :param y: y value to interpolate
        :return: Interpolated z value
        """
        x_values = np.array(self._x.values)
        y_values = np.array(self._y.values)
        
        # Handle edge cases
        if x <= x_values[0] or x >= x_values[-1] or y <= y_values[0] or y >= y_values[-1]:
            interp = RegularGridInterpolator(
                (y_values, x_values), self._z, method='linear', bounds_error=False, fill_value=0
            )
            return float(interp((y, x)))
        
        # Find the indices for x and y
        i_x = np.searchsorted(x_values, x) - 1
        i_y = np.searchsorted(y_values, y) - 1
        
        # Clamp indices to prevent out-of-bounds access
        i_x = min(max(i_x, 0), len(x_values) - 2)
        i_y = min(max(i_y, 0), len(y_values) - 2)
        
        # Get the four surrounding points
        x0, x1 = x_values[i_x], x_values[i_x + 1]
        y0, y1 = y_values[i_y], y_values[i_y + 1]
        z00 = self._z[i_y, i_x]
        z01 = self._z[i_y, i_x + 1]
        z10 = self._z[i_y + 1, i_x]
        z11 = self._z[i_y + 1, i_x + 1]
        
        # Bilinear interpolation
        t = (x - x0) / (x1 - x0)
        u = (y - y0) / (y1 - y0)
        z = (1 - t) * (1 - u) * z00 + t * (1 - u) * z01 + (1 - t) * u * z10 + t * u * z11
        return z