import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import csv

def calculate_lvr(min_ep, max_ep):
    volatility = (max_ep - min_ep) / ((max_ep + min_ep) / 2)
    return (volatility ** 2) / 8 * 10000  # Convert to basis points

def safe_parse_date(date_string):
    date_string = date_string.strip()
    try:
        return pd.to_datetime(date_string, format='%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            return pd.to_datetime(date_string, format='%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                return pd.to_datetime(date_string)
            except ValueError:
                return pd.NaT

def process_network_data(file_path):
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    df['DATE'] = df['DATE'].apply(safe_parse_date)
    df = df.dropna(subset=['DATE'])
    df['LVR'] = df.apply(lambda row: calculate_lvr(row['MIN_EP'], row['MAX_EP']), axis=1)
    return df.groupby('DATE')['LVR'].mean().reset_index()

def process_volume_data(file_path):
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    df['DAY'] = df['DAY'].apply(safe_parse_date)
    df = df.dropna(subset=['DAY'])
    df['VOLUME_USD'] = pd.to_numeric(df['VOLUME_USD'].replace('null', np.nan), errors='coerce')
    return df.dropna(subset=['VOLUME_USD'])

networks = ['arbitrum', 'base', 'mainnet', 'optimism']

# Process data for each network
network_data = {}
volume_data = {}
tam_data = {}

for network in networks:
    network_data[network] = process_network_data(f'../dataset/{network}.csv')
    volume_data[network] = process_volume_data(f'../dataset/{network}_volume.csv')
    
    # Calculate TAM for each network
    df = pd.merge(network_data[network], volume_data[network], left_on='DATE', right_on='DAY', how='inner')
    df['TAM'] = df['LVR'] * df['VOLUME_USD'] / 10000  # LVR is in basis points, so divide by 10000
    tam_data[network] = df[['DATE', 'TAM']]

# 1. Bar chart of average daily TAM for each network
avg_daily_tam = {network: df['TAM'].mean() / 1e6 for network, df in tam_data.items()}  # Convert to millions

plt.figure(figsize=(12, 6))
plt.bar(avg_daily_tam.keys(), avg_daily_tam.values(), color='black')
plt.title('Average Daily TAM by Network')
plt.xlabel('Network')
plt.ylabel('Average Daily TAM (Millions USD)')
plt.tight_layout()
plt.savefig('../charts/avg_daily_tam_by_network.png')
plt.close()

# Generate CSV for average daily TAM by network
with open('../dataset/avg_daily_tam_by_network.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Network', 'Average Daily TAM (Millions USD)'])
    for network, tam in avg_daily_tam.items():
        writer.writerow([network, tam])

# 2. Line chart of TAM over time for all networks
plt.figure(figsize=(14, 8))

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
line_styles = ['-', '--', '-.', ':']

for (network, df), color, style in zip(tam_data.items(), colors, line_styles):
    plt.plot(df['DATE'], df['TAM'] / 1e6, label=network.capitalize(), 
             color=color, linestyle=style, linewidth=2)

plt.title('TAM of All Networks Over Time')
plt.xlabel('Date')
plt.ylabel('TAM (Millions USD)')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.savefig('../charts/tam_over_time_all_networks.png')
plt.close()

print("All charts have been generated and saved.")
print("CSV file 'avg_daily_tam_by_network.csv' has been created.")

# Print date ranges and average daily TAM for each network
total_avg_daily_tam = 0
for network, df in tam_data.items():
    avg_tam = df['TAM'].mean() / 1e6
    total_avg_daily_tam += avg_tam
    print(f"{network.capitalize()} data range: {df['DATE'].min()} to {df['DATE'].max()}")
    print(f"{network.capitalize()} average daily TAM: ${avg_tam:.2f} million")

print(f"\nTotal average daily TAM across all networks: ${total_avg_daily_tam:.2f} million")