import os
import pandas as pd
import datetime
import xarray as xr
import numpy as np
import netCDF4 as nc

def get_base_height(filepath, hour, lat, lon):
    dataset = xr.open_dataset(filepath)
    time_seconds = hour * 3600
    time_index = np.argmin(np.abs(dataset['time_offset'].values - time_seconds))
    level_index = 1
    latitude = 29 - round((lat - 28.5) / 0.5)
    longitude = round((lon + 130) / 0.5)

    try:
        cloudbase = dataset['cloud_height_base_level'][time_index, latitude, longitude, level_index] * 1000
        return cloudbase.item() if not np.isnan(cloudbase) else np.nan
    except (IndexError, KeyError):
        return np.nan

def get_top_height(filepath, hour, lat, lon):
    dataset = xr.open_dataset(filepath)
    time_seconds = hour * 3600
    time_index = np.argmin(np.abs(dataset['time_offset'].values - time_seconds))
    level_index = 1
    latitude = 29 - round((lat - 28.5) / 0.5)
    longitude = round((lon + 130) / 0.5)

    try:
        cloudtop = dataset['cloud_height_top_level'][time_index, latitude, longitude, level_index] * 1000
        return cloudtop.item() if not np.isnan(cloudtop) else np.nan
    except (IndexError, KeyError):
        return np.nan

def get_cloud_fraction(filepath, hour, lat, lon):
    dataset = xr.open_dataset(filepath)
    time_seconds = hour * 3600
    time_index = np.argmin(np.abs(dataset['time_offset'].values - time_seconds))
    level_index = 1
    latitude = 29 - round((lat - 28.5) / 0.5)
    longitude = round((lon + 130) / 0.5)

    try:
        cloudfraction = dataset['cloud_percentage_level'][time_index, latitude, longitude, level_index] * 1000
        return cloudfraction.item() if not np.isnan(cloudfraction) else np.nan
    except (IndexError, KeyError):
        return np.nan

def is_point_in_mixing(lat, lon, current_date_time, alt, ratio):
    hour = current_date_time.hour
    formatted_date = current_date_time.strftime("%Y%m%d") + '.000000'
    filepath = f"/Users/nattamonmaneenoi/Desktop/trajectoryplotting/epcvisstgridg18minnisX1.c1/epcvisstgridg18minnisX1.c1.{formatted_date}.cdf"

    base_height = get_base_height(filepath, hour, lat, lon)
    top_height = get_top_height(filepath, hour, lat, lon)
    cloud_fraction = get_cloud_fraction(filepath, hour, lat, lon)

    if top_height > base_height and alt < top_height and cloud_fraction > 20:
        return 1 - (base_height / top_height)
    else:
        return 0

def count_hours_in_cloud(file_path, transit_time_limit, matchingUTC):
    data = nc.Dataset(file_path)
    filename = os.path.basename(file_path)
    date_str = filename.split('.')[2]
    date_obj = datetime.datetime.strptime(date_str, '%Y%m%d')
    date_time = date_obj.strftime('%Y-%m-%d')
    latitude = data.variables['latitude_ens_mean'][:,:]
    longitude = data.variables['longitude_ens_mean'][:,:]
    altitude = data.variables['height_ens_mean'][:,:]
    height_to_pblh_ratio = data.variables['height_to_pblh_ratio_ens_mean'][:,:]
    total_hours_CBL_LA = []

    for t_idx in range(latitude.shape[0]):
        hr_in_CBL = 0
        iteration_count = 0
        time_in_hours = data.variables['time'][t_idx] / 3600
        dateUTC = f'{date_time} {int(time_in_hours):02d}:00'
        datematching = f'{date_time} {int(time_in_hours):02d}:00:00'
        index = np.where(np.array(matchingUTC) == datematching)[0]
        transit_time = transit_time_limit[index[0]]

        for lat, lon, alt, ratio in zip(latitude[t_idx], longitude[t_idx], altitude[t_idx], height_to_pblh_ratio[t_idx]):
            if transit_time == 0:
                hr_in_CBL = 0
                hours_CBL = (dateUTC, hr_in_CBL, transit_time)
            if iteration_count >= transit_time:
                break

            current_date_time = datetime.datetime.strptime(dateUTC, '%Y-%m-%d %H:%M') - datetime.timedelta(hours=iteration_count)
            hr_in_CBL += is_point_in_mixing(lat, lon, current_date_time, alt, ratio)
            hours_CBL = (dateUTC, hr_in_CBL, transit_time)
            iteration_count += 1

        total_hours_CBL_LA.append(hours_CBL)
        
    return total_hours_CBL_LA

# Read transit time limit data
transit_time_file = '/Users/nattamonmaneenoi/Desktop/finalized data/EPCAPE - LA-SD TT CBL - QC.csv'
transit_time_data = pd.read_csv(transit_time_file)
transit_time_limit = transit_time_data['24 hr limit'].values
matchingUTC = transit_time_data['Start Time'].values

# Process NetCDF files
directory = '/Users/nattamonmaneenoi/Desktop/trajectoryplotting/epcarmtrajsfcM1.c1'
nc_files = sorted([f for f in os.listdir(directory) if f.endswith('.nc')])

# Collect cloud hours data
all_cloud_hours_LA = []
for file_name in nc_files:
    file_path = os.path.join(directory, file_name)
    total_hours_CBL_LA = count_hours_in_cloud(file_path, transit_time_limit, matchingUTC)
    all_cloud_hours_LA.extend(total_hours_CBL_LA)

# Save results to CSV
columns = ['dateUTC', '24hr-UCVF', 'transit_time_limit']
all_hours_CBL_df = pd.DataFrame(all_cloud_hours_LA, columns=columns)
all_hours_CBL_df.to_csv('/Users/nattamonmaneenoi/Desktop/trajectoryplotting/epcarmtrajsfcM1.c1/3hrly_EPCAPE_24hrUCVF.csv', index=False)
