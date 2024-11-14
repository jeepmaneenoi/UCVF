OVERVIEW

This analysis focuses on calculating the Upwind Cloud Vertical Fraction (UCVF) as a measure of cloud mixing within the boundary layer. UCVF quantifies the extent to which the well-mixed boundary layer is cloud-filled, serving as an indicator for the amount of time an air parcel has spent in cloud during its transit. To assess the most recent influence on aerosol composition, the UCVF is computed based on the average vertical fraction of the boundary layer with upwind clouds over the preceding 24 hours along the retrieved back-trajectories.

This script processes cloud layer data from NetCDF files for a specified region, using satellite-retrieved cloud properties from NASA Langley Research Center’s Satellite Cloud and Radiation Property Retrieval System (SatCORPS; Minnis et al., 2008, 2020). Specifically, the script extracts cloud base and top heights, and calculate the cloud fraction at each hourly point along the retrieved back trajeoctory based on set criteria. The goal is to assess the extent to which the trajectory encounters a Cloudy Boundary Layer (CBL) upwind within a 24-hour transit period.


REQUIREMENTS

To run this script, you'll need the following Python libraries:

os
pandas
geopandas
datetime
netCDF4
xarray
numpy

FUNCTIONS

1. get_base_height(vissstfilepath, hour_component, lat, lon)
   
Purpose: Retrieves the cloud base height in meters at a specified latitude and longitude for a given hour from a VISST NetCDF file.
Parameters:
- vissstfilepath: Path to the VISST NetCDF file.
- hour_component: The hour of the day (0-23).
- lat: Latitude of the location.
- lon: Longitude of the location.
Returns: Cloud base height in meters, or NaN if unavailable.

2. get_top_height(vissstfilepath, hour_component, lat, lon)

Purpose: Retrieves the cloud top height in meters at a specified latitude and longitude for a given hour from a VISST NetCDF file.
Parameters: Same as get_base_height.
Returns: Cloud top height in meters, or NaN if unavailable.

3. get_cloud_fraction(vissstfilepath, hour_component, lat, lon)

Purpose: Retrieves the cloud fraction percentage at a specified latitude and longitude for a given hour from a VISST NetCDF file.
Parameters: Same as get_base_height.
Returns: Cloud fraction as a percentage, or NaN if unavailable.

4. is_point_in_mixing(lat, lon, current_date_time, alt, ratio)
   
Purpose: Determines if a point falls within the cloud mixing layer by comparing altitude and cloud properties.
Parameters:
- lat: Latitude of the point.
- lon: Longitude of the point.
- current_date_time: Current datetime of interest.
- alt: Altitude of the point.
Returns: A value indicating cloud mixing level (0 to 1), based on the ratio of base height to top height.

5. count_hours_in_cloud(file_path, transit_time_limit, matchingUTC)
   
Purpose: Calculates the number of hours a point spends in the Cloudy Boundary Layer within a specified transit time limit.
Parameters:
- file_path: Path to a NetCDF file containing location and time data.
- transit_time_limit: Array of time limits (in hours) for cloud mixing assessment.
- matchingUTC: Array of UTC start times for matching.
Returns: A list containing records of hours spent in CBL for each timestamp in the file.

WORKFLOW

1. Load transit time limits from an external CSV file containing hourly limits and corresponding start times.
2. Retrieve NetCDF files from a specified directory (epcarmtrajsfcM1.c1) to analyze cloud data. Each file is processed individually.
3. Calculate 24-hr UCVF:

- For each file, iterate through data points and determine if the point falls within the cloud mixing layer.
- Apply criteria based on altitude, cloud base and top heights to determine cloud fraction at each hourly point along trajecotory and sum over the last 24-hr points.

4. Save Results: Results are saved in a CSV file, containing the date, number of hours in CBL, and transit time limit.
5. Output: The final output is a CSV file named 3hrly_EPCAPE_24hrUCVF.csv, saved in the specified directory. This file contains columns:

- dateUTC: The date and hour of the observation in UTC.
- 24hr-UCVF: Summed UCVF over the last 24 hours along each trajectory.
- transit_time_limit: Limit on the transit time for each point.

USAGE

To execute the script, modify the following paths to match your local setup:

- VISST NetCDF files: Update vissstfilepath in is_point_in_mixing.
- Directory of NetCDF files: Update directory in the main script.
- Transit time CSV file: Update transit_time_file.
Run the script to process cloud data files and generate the output CSV.

NOTES
1. Ensure the transit time CSV file format matches the expected columns: Start Time and 24 hr limit.
2. Latitude and longitude grid indices are hardcoded based on specific grid resolutions; adjust if using different data formats.
3. The script handles missing or invalid data by returning NaN values where applicable.
4. This script is optimized for batch processing cloud data files, with a focus on assessing cloud mixing layers over a 24-hour period based on transit time limits.
