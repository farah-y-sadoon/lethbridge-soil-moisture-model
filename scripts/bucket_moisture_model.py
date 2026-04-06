import os
import pandas as pd
import numpy as np
import glob
import pvlib
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox

class Window(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)        
        self.master = master

        # BUILD GUI WIDGETS
        # Working directory name
        wdir_frame = tk.Frame(master, padx = 10, pady = 5) # Defines the widget group
        wdir_label = tk.Label(wdir_frame, text = "Working directory:")
        wdir_label.grid(column = 0, row = 0, sticky = tk.W)
        self.wdir_name = tk.StringVar()
        wdir_entry = tk.Entry(wdir_frame, width = 40, textvariable = self.wdir_name)
        wdir_entry.grid(column = 1, row = 0, sticky = tk.E)
        wdir_button = tk.Button(wdir_frame, text = "...", command = self.wdir_selector)
        wdir_button.grid(column = 2, row = 0)
        wdir_frame.grid_columnconfigure(1, weight = 1)
        wdir_frame.grid(column = 0, row = 0, sticky = tk.W + tk.E) # First row of widgets

        # Field Capacity
        field_cap_frame = tk.Frame(master, padx = 10, pady = 5) 
        field_cap_label = tk.Label(field_cap_frame, text = 'Field capacity:')
        field_cap_label.grid(column = 0, row = 0, sticky = tk.W)
        self.field_capacity = tk.StringVar(value = '0.28') # Set default for loam-texture soil (Lethbridge) from Saxton and Rawls
        field_cap_entry = tk.Entry(field_cap_frame, width = 12, justify = tk.RIGHT, textvariable = self.field_capacity)
        field_cap_entry.grid(column = 1, row = 0, sticky = tk.E)
        field_cap_frame.grid_columnconfigure(1, weight = 1)
        field_cap_frame.grid(column = 0, row = 1, sticky = tk.W + tk.E)

        # Root Zone Depth
        root_zd_frame = tk.Frame(master, padx = 10, pady = 5)
        root_zd_label = tk.Label(root_zd_frame, text = 'Root zone depth (mm):')
        root_zd_label.grid(column = 0, row = 0, sticky = tk.W)
        self.root_zone_depth = tk.StringVar(value = '1000') # Set default for root zone depth matching maximum Alberta root zone values
        root_zd_entry = tk.Entry(root_zd_frame, width = 12, justify = tk.RIGHT, textvariable = self.root_zone_depth)
        root_zd_entry.grid(column = 1, row = 0, sticky = tk.E)
        root_zd_frame.grid_columnconfigure(1, weight = 1)
        root_zd_frame.grid(column = 0, row = 2, sticky = tk.W + tk.E)

        # Drainage Coefficient
        drain_coeff_frame = tk.Frame(master, padx = 10, pady = 5)
        drain_coeff_label = tk.Label(drain_coeff_frame, text = 'Drainage coefficient (mm/min):')
        drain_coeff_label.grid(column = 0, row = 0, sticky = tk.W)
        self.drainage_coeff_mm_min = tk.StringVar(value = '0.258') # Set default for loam-texture soil (Lethbridge) from Saxton and Rawls
        drain_coeff_entry = tk.Entry(drain_coeff_frame, width = 12, justify = tk.RIGHT, textvariable = self.drainage_coeff_mm_min)
        drain_coeff_entry.grid(column = 1, row = 0, sticky = tk.E)
        drain_coeff_frame.grid_columnconfigure(1, weight = 1)
        drain_coeff_frame.grid(column = 0, row = 3, sticky = tk.W + tk.E)

        # Cloud Cover Days
        cloud_cov_days_frame = tk.Frame(master, padx = 10, pady = 5)
        cloud_cov_days_label = tk.Label(cloud_cov_days_frame, text = 'Number of cloud cover days:')
        cloud_cov_days_label.grid(column = 0, row = 0, sticky = tk.W)
        self.cloud_cover_days = tk.StringVar(value = '3') # Set default cloud cover days to 3 days (prior to rain)
        cloud_cov_days_entry = tk.Entry(cloud_cov_days_frame, width = 12, justify = tk.RIGHT, textvariable = self.cloud_cover_days)
        cloud_cov_days_entry.grid(column = 1, row = 0, sticky = tk.E)
        cloud_cov_days_frame.grid_columnconfigure(1, weight = 1)
        cloud_cov_days_frame.grid(column = 0, row = 4, sticky = tk.W + tk.E)

        # Cloud Reduction Factor
        cloud_reduce_frame = tk.Frame(master, padx = 10, pady = 5)
        cloud_reduce_label = tk.Label(cloud_reduce_frame, text = 'Cloud cover correction factor:')
        cloud_reduce_label.grid(column = 0, row = 0, sticky = tk.W)
        self.cloud_reduction_factor = tk.StringVar(value = '0.5') # Set default cloud cover correction to 0.5 
        cloud_reduce_entry = tk.Entry(cloud_reduce_frame, width = 12, justify = tk.RIGHT, textvariable = self.cloud_reduction_factor)
        cloud_reduce_entry.grid(column = 1, row = 0, sticky = tk.E)
        cloud_reduce_frame.grid_columnconfigure(1, weight = 1)
        cloud_reduce_frame.grid(column = 0, row = 5, sticky = tk.W + tk.E)

        # Output Directory
        outdir_frame = tk.Frame(master, padx = 10, pady = 5)
        outdir_label = tk.Label(outdir_frame, text = "Output directory name:")
        outdir_label.grid(column = 0, row = 0, sticky = tk.W)
        self.outdir_name = tk.StringVar()
        outdir_entry = tk.Entry(outdir_frame, width = 40, textvariable = self.outdir_name)
        outdir_entry.grid(column = 1, row = 0, sticky = tk.E)
        output_button = tk.Button(outdir_frame, text = "...", command = self.outdir_selector)
        output_button.grid(column = 2, row = 0)
        outdir_frame.grid_columnconfigure(1, weight = 1)
        outdir_frame.grid(column = 0, row = 6, sticky = tk.W + tk.E) # Seventh row of widgets

        # Bottom Frame
        bottom_frame = tk.Frame(master, padx = 10, pady = 10)

        # Exit and OK buttons
        btn_frame = tk.Frame(bottom_frame)
        ok_btn = tk.Button(btn_frame, text = 'Run', command = self.calculate_soil_moisture)
        ok_btn.grid(column = 0, row = 0, sticky = tk.W)
        exit_btn = tk.Button(btn_frame, text = 'Exit', command = self.exit)
        exit_btn.grid(column = 1, row = 0, sticky = tk.W)
        btn_frame.grid(column = 0, row = 8, sticky = tk.W)

        # Grid bottom frame
        bottom_frame.grid_columnconfigure(1, weight = 1)
        bottom_frame.grid(column = 0, row = 8, sticky = tk.W + tk.E)

    # CHECK USER INPUTS FOR ERRORS
    def validate_inputs(self):
        errors = []
        warnings = []
        # Working directory
        if not self.wdir_name.get():
            errors.append('Invalid. Working directory is required.')
        
        # Output directory
        if not self.outdir_name.get():
            errors.append('Invalid. Output directory is required.')
        
        # Field capacity
        try:
            float(self.field_capacity.get())
            if float(self.field_capacity.get()) < 0: 
                warnings.append('Warning: Field capacity must be positive. Negative number has been converted.')
            elif float(self.field_capacity.get()) == 0:
                errors.append('Invalid. Field capacity cannot be zero.')
        except ValueError:
            errors.append('Invalid. Field capacity must be a number.')
        
        # Root zone depth
        try:
            float(self.root_zone_depth.get())
            if float(self.root_zone_depth.get()) < 0: 
                warnings.append('Warning: Root zone depth must be positive. Negative number has been converted.')
            elif float(self.root_zone_depth.get()) == 0:
                errors.append('Invalid. Root zone depth cannot be zero.')
        except ValueError:
            errors.append('Invalid. Root zone depth must be a number.')

        # Drainage coefficient
        try: 
            float(self.drainage_coeff_mm_min.get())
            if float(self.drainage_coeff_mm_min.get()) < 0: 
                warnings.append('Warning: Drainage coefficient must be positive. Negative number has been converted.')
        except ValueError: 
            errors.append('Invalid. Drainage coefficient must be a number.')
        
        # Cloud cover days
        try: 
            float(self.cloud_cover_days.get())
            if int(self.cloud_cover_days.get()) < 0: 
                warnings.append('Warning: Number of cloud cover days must be positive. Negative number has been converted.')
            elif float(self.cloud_cover_days.get()) == 0:
                errors.append('Invalid. Cloud cover days cannot be zero.')
        except ValueError: 
            errors.append('Invalid. Cloud cover days must be an integer.')

        # Cloud reduction factor
        try: 
            float(self.cloud_reduction_factor.get())
            if float(self.cloud_reduction_factor.get()) < 0: 
                warnings.append('Warning: Cloud correction must be positive. Negative number has been converted.')
        except ValueError: 
            errors.append('Invalid. Cloud correction must be a number.')
        
        return errors, warnings

    # RUN MODEL LOGIC 
    def calculate_soil_moisture(self): 
        # Check for input errors and warnings before running the model
        errors, warnings = self.validate_inputs()
        if errors: 
            messagebox.showinfo('There was a problem with your inputs:', '\n'.join(errors))
            return
        
        if warnings: 
            messagebox.showinfo('Warning', '\n'.join(warnings))

        try:
            print("Starting workflow")

            # Set parameters to user inputs 
            field_capacity = abs(float(self.field_capacity.get()))
            root_zone_depth_mm = abs(float(self.root_zone_depth.get()))
            drainage_coeff_mm_min = abs(float(self.drainage_coeff_mm_min.get()))
            cloud_cover_days = abs(int(self.cloud_cover_days.get()))
            cloud_reduction_factor = abs(float(self.cloud_reduction_factor.get()))
            wdir = self.wdir_name.get()
            outdir = self.outdir_name.get()

            # Create data frame from all CSV files in working directory
            all_files = glob.glob(os.path.join(wdir, "*.csv"))
            file_list = []

            for filename in all_files: 
                try: 
                    df = pd.read_csv(filename, index_col = None, header = 0, encoding = "latin1")
                    file_list.append(df)
                except Exception as e:
                    print('Error reading file:', e)
            
            df_weather = pd.concat(file_list, axis = 0, ignore_index = True)

            # Clean weather data frame
            # Select only necessary columns - this expects the user to have columns with these names formatted in this way
            keep_columns = ['date', 
                    'min_temp', 
                    'max_temp', 
                    'avg_temp', 
                    'precip']
            df_weather = df_weather[keep_columns]
            
            # Convert date object to date time format and sort data frame based on date
            df_weather['date'] = pd.to_datetime(df_weather['date'], dayfirst = True)
            df_weather = df_weather.sort_values(by = 'date')
            df_weather = df_weather.set_index('date')
            df_weather = df_weather[~df_weather.index.duplicated(keep = 'first')] # only keep the first instance of the date if there are duplicates

            # Calculate extraterrestrial radiation
            times = df_weather.index # extract date values for equation
        
            # Get Ra in W/m^2 (instantaneous), then convert to MJ/m^2/day (accumulated) for Hargreaves 
            df_weather['Ra'] = pvlib.irradiance.get_extra_radiation(times) * 0.0864 # to determine how much evaporation occurred in a day

            # Calculate ET
            # Multiply by 0.408 to account for kg/m2 to mm conversion 
            df_weather['ET0'] = ((0.0023 * (df_weather['avg_temp'] + 17.8) \
                                        * np.sqrt(df_weather['max_temp'] - df_weather['min_temp']) \
                                        * df_weather['Ra']) * 0.408).clip(lower = 0)
            
            # Calculate cloud cover correction 
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
                # CALCULATE stress_ET to scale ET by available water - when storage falls below 50% of storage capacity, ET decreases; accounts for root activity
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
            output_csv = os.path.join(outdir, 'soil_moisture_results.csv')
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

            # Generate plot and set axes labels and ticks
            fig1, ax1 = plt.subplots(figsize = (12, 5))
            ax1.plot(df_doy_average.index, df_doy_average['St'], color = '#8EA998')
            ax1.set_title(f'Average Daily Soil Moisture {min_year} - {max_year}', fontsize = 15)
            ax1.set_xticks(month_ticks.values)
            ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            ax1.set_ylabel('Soil Moisture (mm)', fontsize = 10)
            ax1.tick_params(axis = 'x', labelsize = 10, rotation = 30)
            ax1.tick_params(axis = 'y', labelsize = 10)

            # Save plot
            output_plot_1 = os.path.join(outdir, 'avg_doy_soil_moisture.png')
            fig1.savefig(output_plot_1, dpi = 900, bbox_inches = "tight")
        
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
            colors = ['#D4E1F5', '#8EA998', '#E7E0AE', '#E1D5E7']

            winter = df_seasonal_average.loc['Winter'].values
            spring = df_seasonal_average.loc['Spring'].values
            summer = df_seasonal_average.loc['Summer'].values
            autumn = df_seasonal_average.loc['Autumn'].values
            data_arrays   = [winter, spring, summer, autumn]

            # Generate plot and set axes labels and ticks
            fig2, ax2 = plt.subplots(figsize = (12, 6))
            
            ax2.set_title(f'Soil Moisture by Season {min_year} - {max_year}', fontsize = 15)
            ax2.set_ylabel('Soil Moisture (mm)')
            ax2.tick_params(axis = 'x', labelsize = 10, rotation = 30)
            ax2.tick_params(axis = 'y', labelsize = 10)

            # Create boxplots
            bplot = ax2.boxplot(data_arrays, patch_artist = True,
                            tick_labels = season_labels)

            # Fill each boxplot with specified colours
            for patch, color in zip(bplot['boxes'], colors):
                patch.set_facecolor(color)

            # Save plot
            output_plot_2 = os.path.join(outdir, 'seasonal_soil_moisture_boxplots.png')
            fig2.savefig(output_plot_2, dpi = 900, bbox_inches = "tight")
        
            # Show all plots
            plt.show()

        except Exception as e:
            print(f"An error occurred: {e}")

        finally: 
            print("Workflow complete.")

    def exit(self):
        exit(0)

    def wdir_selector(self):
        fn = filedialog.askdirectory(title = 'Select your working directory',
                                     initialdir=os.path.expanduser('~'))  # start search at home directory instead of root
        self.wdir_name.set(fn)

    def outdir_selector(self):
        fn = filedialog.askdirectory(title = 'Select your output directory',
                                     initialdir = os.path.expanduser('~'))
        self.outdir_name.set(fn)

root = tk.Tk()
app = Window(root)
root.wm_title("Calculate Soil Moisture")
root.mainloop()
