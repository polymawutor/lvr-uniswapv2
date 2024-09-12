import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# Function to calculate LVR
def calculate_lvr(min_ep, max_ep):
    volatility = (max_ep - min_ep) / ((max_ep + min_ep) / 2)
    return (volatility ** 2) / 8 * 10000  # Convert to basis points

# Function to safely parse dates
def safe_parse_date(date_string):
    date_string = date_string.strip()  # Remove any leading/trailing whitespace
    try:
        return pd.to_datetime(date_string, format='%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            return pd.to_datetime(date_string, format='%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                return pd.to_datetime(date_string)
            except ValueError:
                return pd.NaT  # Return Not-a-Time for unparseable dates

# Read the CSV file
df = pd.read_csv('../dataset/optimism.csv', encoding='utf-8-sig')  # Use UTF-8 with BOM encoding

# Apply safe date parsing
df['DATE'] = df['DATE'].apply(safe_parse_date)

# Remove rows with invalid dates
df = df.dropna(subset=['DATE'])

# Calculate LVR
df['LVR'] = df.apply(lambda row: calculate_lvr(row['MIN_EP'], row['MAX_EP']), axis=1)

# Add columns for week and month
df['WEEK'] = df['DATE'].dt.to_period('W')
df['MONTH'] = df['DATE'].dt.to_period('M')

# 1. Bar chart of overall average daily, weekly, and monthly LVR
daily_lvr = df['LVR'].mean()
weekly_lvr = df.groupby('WEEK')['LVR'].mean().mean()
monthly_lvr = df.groupby('MONTH')['LVR'].mean().mean()

plt.figure(figsize=(10, 6))
plt.bar(['Daily', 'Weekly', 'Monthly'], [daily_lvr, weekly_lvr, monthly_lvr], color='black')
plt.title('Optimism Overall Average LVR (Daily, Weekly, Monthly)')
plt.ylabel('LVR (basis points)')
plt.tight_layout()
plt.savefig('../charts/optimism_overall_avg_lvr.png')
plt.close()

# 2. Bar chart of average daily LVR of 10 longest active pools
pool_activity = df.groupby('POOL_NAME')['DATE'].agg(['min', 'max'])
pool_activity['duration'] = pool_activity['max'] - pool_activity['min']
top_10_pools = pool_activity.nlargest(10, 'duration').index

top_10_daily_lvr = df[df['POOL_NAME'].isin(top_10_pools)].groupby('POOL_NAME')['LVR'].mean().sort_values(ascending=False)

plt.figure(figsize=(12, 6))
top_10_daily_lvr.plot(kind='bar', color='black')
plt.title('Optimism Average Daily LVR of 10 Longest Active Pools')
plt.xlabel('Pool Name')
plt.ylabel('LVR (basis points)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('../charts/optimism_top_10_pools_daily_lvr.png')
plt.close()

# 3. Chart showing overall average daily LVR over time
daily_avg_lvr = df.groupby('DATE')['LVR'].mean()

plt.figure(figsize=(12, 6))
daily_avg_lvr.plot(color='black')
plt.title('Optimism Overall Average Daily LVR Over Time')
plt.xlabel('Date')
plt.ylabel('LVR (basis points)')
plt.tight_layout()
plt.savefig('../charts/optimism_overall_daily_lvr_over_time.png')
plt.close()

# 4. Chart showing day-of-week analysis
df['DAY_OF_WEEK'] = df['DATE'].dt.day_name()
day_of_week_lvr = df.groupby('DAY_OF_WEEK')['LVR'].mean()
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_of_week_lvr = day_of_week_lvr.reindex(day_order)

plt.figure(figsize=(10, 6))
day_of_week_lvr.plot(kind='bar', color='black')
plt.title('Optimism Average LVR by Day of Week')
plt.xlabel('Day of Week')
plt.ylabel('LVR (basis points)')
plt.tight_layout()
plt.savefig('../charts/optimism_lvr_by_day_of_week.png')
plt.close()

# 5. Chart showing week-of-month analysis
df['WEEK_OF_MONTH'] = df['DATE'].dt.day.map(lambda x: (x - 1) // 7 + 1)
week_of_month_lvr = df.groupby('WEEK_OF_MONTH')['LVR'].mean()

plt.figure(figsize=(10, 6))
week_of_month_lvr.plot(kind='bar', color='black')
plt.title('Optimism Average LVR by Week of Month')
plt.xlabel('Week of Month')
plt.ylabel('LVR (basis points)')
plt.xticks(range(5), ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'])
plt.tight_layout()
plt.savefig('../charts/optimism_lvr_by_week_of_month.png')
plt.close()

print("All charts have been generated and saved.")