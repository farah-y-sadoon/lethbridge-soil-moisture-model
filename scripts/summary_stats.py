import pandas as pd
import numpy as np

df = pd.read_csv('../results/soil_moisture_results.csv', index_col = 0, parse_dates = True)

conditions = [df.index.month.isin([12,1,2]), df.index.month.isin([3,4,5]), 
              df.index.month.isin([6,7,8]), df.index.month.isin([9,10,11])]
choices = ['Winter', 'Spring', 'Summer', 'Autumn']
df['season'] = np.select(conditions, choices, default = 'NA')

cols = ['precip', 'ET0', 'Dt', 'St']

# Table 1 - Seasonal stats
seasonal_stats = df.groupby('season')[cols].agg(['mean', 'min', 'max'])
print("SEASONAL STATISTICS")
print(seasonal_stats)

print("\n")

# Table 2 - Annual stats
annual_stats = df[cols].agg(['mean', 'std', 'min', 'max'])
print("ANNUAL STATISTICS")
print(annual_stats)