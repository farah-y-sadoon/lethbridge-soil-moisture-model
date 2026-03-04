import os
import pandas as pd
import glob 

def main(): 
    try:
        print("Starting workflow")
        
        # Set working directory for files
        working_directory = input("Please enter your working directory: ")
        
        # Set output directory prefix 
        output_directory = input("Please enter the output directory: ") # could also ask for prefix and create the directory for them

        # Create data frame from all CSV files in working directory
        all_files = glob.glob(os.path.join(working_directory, "*.csv"))
        file_list = []
        print(all_files)

        for filename in all_files: 
            print(f"Reading: {filename}")
            try: 
                df = pd.read_csv(filename, index_col = None, header = 0, encoding = "latin1")
                file_list.append(df)
            except Exception as e:
                print("Error reading file:", e) 
        
        df_weather_data = pd.concat(file_list, axis=0, ignore_index=True)
        print(df_weather_data.head(100))
        print(df_weather_data.columns)

        # Clean data frame
        # Remove unneccessary columns
        df_weather_data = df_weather_data.drop(columns = ['Station Name', 
                                               'Air Temp. Min. Source Flag', 
                                               'Air Temp. Min. Record Completeness (%)',
                                               'Air Temp. Max. Source Flag', 
                                               'Air Temp. Max. Record Completeness (%)', 
                                               'Air Temp. Avg. Source Flag', 
                                               'Air Temp. Avg. Record Completeness (%)', 
                                               'Relative Humidity Avg. (%)',
                                               'Relative Humidity Avg. Source Flag', 
                                               'Relative Humidity Avg. Record Completeness (%)',
                                               'Precip. Accumulated (mm)',
                                               'Precip. Accumulated Source Flag', 
                                               'Precip. Accumulated Comment',
                                               'Precip. Source Flag',
                                               'Precip. Comment',
                                               'Wind Speed 10 m Avg. (km/h)',
                                               'Wind Speed 10 m Avg. Source Flag',
                                               'Wind Speed 10 m Avg. Record Completeness (%)',
                                               'Wind Dir. 10 m Avg. (°)', 
                                               'Wind Dir. 10 m Avg. Source Flag',
                                               'Wind Dir. 10 m Avg. Record Completeness (%)',
                                               'ET. Std-Grass (mm)',
                                               'ET. Std-Grass Source Flag', 
                                               'ET. Std-Grass Comment',
                                               'Growing Degree Days (base 5°C) (GDD)',
                                               'Growing Degree Days (base 5°C) Source Flag',
                                               'Corn Heat Units (germinate on start date) (CHU)',
                                               'Corn Heat Units (germinate on start date) Source Flag',
                                               'Potato Heat Units (PHU)', 'Potato Heat Units Source Flag'
                                               ])
        print(df_weather_data.columns)
        print(df_weather_data.head(100))
        print(df_weather_data.isna().sum())

        # rename columns
        df_weather_data = df_weather_data.rename(columns = {'Date (Local Standard Time)': 'date',
                                                            'Air Temp. Min. (°C)': 'min_temp', 
                                                            'Air Temp. Max. (°C)': 'max_temp',
                                                            'Air Temp. Avg. (°C)': 'avg_temp',
                                                            'Precip. (mm)': 'precip'
                                                            })

        # convert date object to date time format and sort data frame based on date
        df_weather_data['date'] = pd.to_datetime(df_weather_data['date'], dayfirst = True)
        df_weather_data.sort_values(by = 'date')

        print(df_weather_data.columns)
        print(df_weather_data.head(100))
        print(df_weather_data.dtypes)








    except Exception as e: 
        print(f"An error occurred: {e}")

    finally: 
        print("Workflow complete.")

main()

# MODEL OUTPUTS: 
    # TIME SERIES GRAPHS AND STATISTICS ON DAILY WEATHER TRENDS FROM THE PERIOD OF TIME SPECIFIED

# def main() 
# USER INPUT DATA
# READ WEATHER DATA
# CREATE OUTPUT VARIABLE STORAGE
# LOOP OVER EVERY DAY
    # CALCULATE EVAPOTRANSPIRATION
    # CALCULATE DRAINAGE
    # CALCULATE SOIL MOISTURE
# SAVE OUTPUT
# CREATE VISUALIZATIONS FROM OUTPUTS

