import os
import pandas as pd
import numpy as np
import glob
import pvlib

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
        df_weather = df_weather[~df_weather.index.duplicated(keep='first')]

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
        cloud_shadow = rainy_days.rolling(window = cloud_cover_days + 1, min_periods = 1).max().astype(bool)
        
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

        df_weather.to_csv(os.path.join(output_directory, '/df_weather_results.csv'), index = False)

    except Exception as e: 
        print(f"An error occurred: {e}")

    finally: 
        print("Workflow complete.")

main()

# NEXT STEPS
# MAKE INPUTS PARAMS ALL USER SPECIFIED
    # FIELD CAPACITY
    # ROOT ZONE DEPTH
    # DRAINAGE COEFF

# SAVE OUTPUT
# CREATE VISUALIZATIONS FROM OUTPUTS

### EXTRA: TO MAKE THIS OBJECT ORIENTED
            # METHOD 1 - CALCULATE DRAINAGE
            # METHOD 2 - CALCULATE EVAPOTRANSPIRATION
            # METHOD 3 - CALCULATE FINAL MODEL OUTPUT VALUES - STORAGE (MM)
                # OUTPUT FIGURES

### EXTRA: SET PROGRESS UPDATES FOR THE USER

