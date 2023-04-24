import pandas as pd
from sodapy import Socrata
import requests
from fuzzywuzzy import fuzz
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def millions_formatter(x, pos):
    return f'{x * 1e-6:.0f}M'

# Fetch the data
client = Socrata("data.cityofchicago.org", None)
results = client.get("5neh-572f", where="date between '2019-01-01T00:00:00.000' and '2019-12-31T23:59:59.000'", limit=50000)
rides_df_2019 = pd.DataFrame.from_records(results)

results = client.get("5neh-572f", where="date between '2020-01-01T00:00:00.000' and '2020-12-31T23:59:59.000'", limit=50000)
rides_df_2020 = pd.DataFrame.from_records(results)

results = client.get("5neh-572f", where="date between '2021-01-01T00:00:00.000' and '2021-12-31T23:59:59.000'", limit=50000)
rides_df_2021 = pd.DataFrame.from_records(results)

results = client.get("5neh-572f", where="date between '2022-01-01T00:00:00.000' and '2022-12-31T23:59:59.000'", limit=50000)
rides_df_2022 = pd.DataFrame.from_records(results)


# Fetch the train station data
station_data = requests.get("https://data.cityofchicago.org/resource/8pix-ypme.json").json()

# Function to get the train line for a station
def get_train_line(station):
    return station["station_descriptive_name"].split("(")[-1].replace(")", "").strip()

# Create a dictionary to map station names to train lines
station_name_to_line = {
    station["station_name"].lower(): {
        "train_line": get_train_line(station),
        "location": station["location"]
    }
    for station in station_data
}


def fuzzy_match_station(name):
    best_match = max(station_name_to_line, key=lambda x: fuzz.token_sort_ratio(name.lower(), x))
    return station_name_to_line[best_match]


for df in [rides_df_2019, rides_df_2020, rides_df_2021, rides_df_2022]:
    df['train_line'] = df['stationname'].apply(lambda x: fuzzy_match_station(x)['train_line'])
    df['location'] = df['stationname'].apply(lambda x: fuzzy_match_station(x)['location'])
    df['rides'] = pd.to_numeric(df['rides'])
    df.set_index(pd.to_datetime(df['date']), inplace=True)

print(rides_df_2019)

# Group the data by month and sum the rides for each month
monthly_rides_2019 = rides_df_2019['rides'].resample('M').sum()
monthly_rides_2020 = rides_df_2020['rides'].resample('M').sum()
monthly_rides_2021 = rides_df_2021['rides'].resample('M').sum()
monthly_rides_2022 = rides_df_2022['rides'].resample('M').sum()

# Create bar plots
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 12))
fig.suptitle('Total Rides per Month for 2019, 2020, 2021, and 2022')

y_formatter = FuncFormatter(millions_formatter)

sns.barplot(x=monthly_rides_2019.index.strftime('%b'), y=monthly_rides_2019, ax=axes[0, 0])
axes[0, 0].set_title('2019')
axes[0, 0].set_xlabel('Month')
axes[0, 0].set_ylabel('Total Rides')
axes[0, 0].yaxis.set_major_formatter(y_formatter)

sns.barplot(x=monthly_rides_2020.index.strftime('%b'), y=monthly_rides_2020, ax=axes[0, 1])
axes[0, 1].set_title('2020')
axes[0, 1].set_xlabel('Month')
axes[0, 1].set_ylabel('Total Rides')
axes[0, 1].yaxis.set_major_formatter(y_formatter)

sns.barplot(x=monthly_rides_2021.index.strftime('%b'), y=monthly_rides_2021, ax=axes[1, 0])
axes[1, 0].set_title('2021')
axes[1, 0].set_xlabel('Month')
axes[1, 0].set_ylabel('Total Rides')
axes[1, 0].yaxis.set_major_formatter(y_formatter)

sns.barplot(x=monthly_rides_2022.index.strftime('%b'), y=monthly_rides_2022, ax=axes[1, 1])
axes[1, 1].set_title('2022')
axes[1, 1].set_xlabel('Month')
axes[1, 1].set_ylabel('Total Rides')
axes[1, 1].yaxis.set_major_formatter(y_formatter)

plt.show()