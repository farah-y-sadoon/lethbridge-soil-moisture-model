import os
import pandas as pd
import numpy as np
import glob
import pvlib
import matplotlib
import matplotlib.pyplot as plt

def main(): 
    try:
        print("Starting workflow")
        
        # Set working directory for files
        working_directory = input("Please enter your working directory: ")
        
        # Set output directory prefix 
        output_directory = input("Please enter the output directory: ")

        # Set parameters # CHANGE THESE TO USER INPUTS
        field_capacity = 0.28 # for loam-texture soil from Saxton and Rawls - UPDATE IF DOING EXTRA STEP OF MAKING THESE DYNAMIC
        root_zone_depth_mm = 1000
        drainage_coeff_mm_min = 15.5 / 60 # for loam-texture soil from Saxton and Rawls - UPDATE IF DOING EXTRA STEP OF MAKING THIS DYNAMIC
        cloud_cover_days = 3
        cloud_reduction_factor = 0.5

        # Create data frame from all CSV files in working directory
        all_files = glob.glob(os.path.join(working_directory, "*.csv"))
        file_list = []

        for filename in all_files: 
            try: 
                df = pd.read_csv(filename, index_col = None, header = 0, encoding = "latin1")
                file_list.append(df)
            except Exception as e:
                print("Error reading file:", e)
        
        df_weather = pd.concat(file_list, axis=0, ignore_index=True)

        # Clean weather data frame
        # Select only necessary columns
        keep_columns = ['Date (Local Standard Time)', 
                'Air Temp. Min. (°C)', 
                'Air Temp. Max. (°C)', 
                'Air Temp. Avg. (°C)', 
                'Precip. (mm)']
        df_weather = df_weather[keep_columns]
        print(df_weather.columns)
        print(df_weather.head(100))
        print(df_weather.isna().sum())

        # Rename columns
        df_weather = df_weather.rename(columns = {'Date (Local Standard Time)': 'date',
                                                            'Air Temp. Min. (°C)': 'min_temp', 
                                                            'Air Temp. Max. (°C)': 'max_temp',
                                                            'Air Temp. Avg. (°C)': 'avg_temp',
                                                            'Precip. (mm)': 'precip'
                                                            })
        
        # Convert date object to date time format and sort data frame based on date
        df_weather['date'] = pd.to_datetime(df_weather['date'], dayfirst = True)
        df_weather = df_weather.sort_values(by = 'date')
        df_weather = df_weather.set_index('date')
        df_weather = df_weather[~df_weather.index.duplicated(keep = 'first')] # only keep the first instance of the date if there are duplicates

        # CALCULATE extraterrestrial radiation
        times = df_weather.index # extract date values for equation
    
        # Get Ra in W/m^2 (instantaneous), then convert to MJ/m^2/day (accumulated) for Hargreaves 
        df_weather['Ra'] = pvlib.irradiance.get_extra_radiation(times) * 0.0864 # to determine how much evaporation occurred in a day

        # CALCULATE ET
        # Multiply by 0.408 to account for kg/m2 to mm conversion 
        df_weather['ET0'] = ((0.0023 * (df_weather['avg_temp'] + 17.8) \
                                    * np.sqrt(df_weather['max_temp'] - df_weather['min_temp']) \
                                    * df_weather['Ra']) * 0.408).clip(lower = 0)
        
        # CALCULATE cloud cover correction 
        rainy_days = df_weather['precip'] > 0.0 
        cloud_shadow = rainy_days.rolling(window = cloud_cover_days, min_periods = 1).max().astype(bool)
        
        # Apply the correction
        df_weather['cloud_correction'] = np.where(cloud_shadow, cloud_reduction_factor, 1.0)
        df_weather['ET0'] = df_weather['ET0'] * df_weather['cloud_correction']
        
        # Iterate through each day in the dataset and calculate Dt (drainage value) and storage:
        # Set initial value of storage at field capacity * root zone depth and ensure daily ET cannot be 
        S_current = field_capacity * root_zone_depth_mm * 0.5 # multiply by 0.5 so that field capacity is not 100% on day 1 
        capacity_mm = field_capacity * root_zone_depth_mm 

        # Initialize Dt and St columns
        df_weather['Dt'] = 0.0
        df_weather['St'] = 0.0

        for i, row in df_weather.iterrows():
            # CALCULATE stress_ET to scale ET by available water - when storage falls below 50% of field capacity, ET decreases; accounts for root activity
            stress = min(1.0, S_current / (0.5 * capacity_mm))  # ET starts declining below 50% capacity
            stress_ET = row['ET0'] * stress

            # CALCULATE provisional state of storage (S)
            S_provisional = S_current + row['precip'] - stress_ET

            # CALCULATE drainage 
            if S_provisional > capacity_mm:
                drainage_mm = drainage_coeff_mm_min * (S_provisional - capacity_mm)
            elif S_provisional <= capacity_mm: 
                drainage_mm = 0.0

            # CALCULATE final storage (St) for the day
            S_final = max(0, S_provisional - drainage_mm)

            # Write values to data frame
            df_weather.at[i, 'Dt'] = drainage_mm
            df_weather.at[i, 'St'] = S_final
             
            # Update provisional to point to current day's storage value for tomorrow's calculation
            S_current = S_final
        
        # Save results
        output_csv = os.path.join(output_directory, 'soil_moisture_results.csv')
        df_weather.to_csv(output_csv, index = True)

        # CREATE plots
        # 1 - Average soil moisture for day of year
        # Create column for day of year and calculate average for each day of the year
        df_weather['doy'] = df_weather.index.day_of_year
        df_doy_average = df_weather.groupby('doy').mean() # group all the same days together and calculate mean in a new dataframe

        # Create labels for each month to make chart more readable
        month_ticks = df_weather.groupby(df_weather.index.month)['doy'].min()

        # Extract maximum and minimum years for title 
        min_year = df_weather.index.year.min()
        max_year = df_weather.index.year.max() 

        # Generate plot
        plt.plot(df_doy_average.index, df_doy_average['St'])
        plt.xticks(month_ticks.values, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

        # Add a plot title
        plt.title(f'Average Daily Soil Moisture {min_year} - {max_year}', fontsize = 15)

        # Add axis labels
        plt.ylabel('Soil Moisture (mm)', fontsize = 15)

        # Rotate axis ticks
        plt.xticks(rotation = 30, fontsize = 15)

        # Save plot
        output_plot = os.path.join(output_directory, 'avg_doy_soil_moisture.png')
        plt.savefig(output_plot, dpi = 900, bbox_inches = "tight")
    
        # Show plot
        plt.show()

        # 2 - Seasonal statistics boxplots
        # Add a column to data frame for each season
        conditions  = [df_weather.index.month.isin([12,1,2]), df_weather.index.month.isin([3,4,5]), 
                       df_weather.index.month.isin([6,7,8]), df_weather.index.month.isin([9,10,11])]
        choices     = [ 'Winter', 'Spring', 'Summer', 'Autumn' ]
                    
        df_weather['season'] = np.select(conditions, choices, default = "NA")
        df_weather['year'] = df_weather.index.year
        df_weather['month'] = df_weather.index.month_name()

        # Calculate seasonal averages for each year and month 
        df_seasonal_average = df_weather.groupby(['season', 'year'])['St'].mean()

        # Extract each season as an array to plot as boxplots
        season_labels = ['Winter (Dec-Feb)', 'Spring (Mar-May)', 'Summer (Jun-Aug)', 'Autumn (Sep-Nov)']
        colors = ['#4EA8DE', '#57CC99', '#FFD166', '#F4845F']

        winter = df_seasonal_average.loc['Winter'].values # loc indicates specific columns in pandas that belong to each array
        spring = df_seasonal_average.loc['Spring'].values
        summer = df_seasonal_average.loc['Summer'].values
        autumn = df_seasonal_average.loc['Autumn'].values
        data_arrays   = [winter, spring, summer, autumn]

        # Generate plot
        fig, ax = plt.subplots()
        ax.set_ylabel('Soil Moisture (mm)')

        bplot = ax.boxplot(data_arrays, patch_artist = True, # fill with color
                        tick_labels = season_labels)  # will be used to label x-ticks

        # Fill with specified colours
        for patch, color in zip(bplot['boxes'], colors):
            patch.set_facecolor(color)

        # Add a plot title
        plt.title(f'Soil Moisture by Season {min_year} - {max_year}', fontsize = 15)

        # Rotate axis ticks
        plt.xticks(rotation = 30, fontsize = 15)
        plt.yticks(fontsize = 15)

        # Save plot
        output_plot = os.path.join(output_directory, 'seasonal_soil_moisture_boxplots.png')
        plt.savefig(output_plot, dpi = 900, bbox_inches = "tight")
    
        # Show plot
        plt.show()

    except Exception as e: 
        print(f"An error occurred: {e}")

    finally: 
        print("Workflow complete.")

main()

# NEXT STEPS
# CREATE GUI WITH USER SPECIFIED PARAMS
    # FIELD CAPACITY
    # ROOT ZONE DEPTH
    # DRAINAGE COEFF

