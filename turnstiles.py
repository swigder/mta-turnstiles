import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


sns.set()

# read csv, including parsing dates
# todo all files
# todo don't hardcode
df = pd.read_csv('/Users/xx/Documents/source/mta-turnstiles/turnstile_180804.txt',
                 parse_dates=[['DATE', 'TIME']])
df.rename(columns=lambda x: x.strip(), inplace=True)  # EXITS column has too much whitespace

# convert cumulative counts to interval counts
# todo is this everything we need to group by?
# todo is this always sorted?
df[['ENTRIES_P', 'EXITS_P']] = df.groupby(['C/A', 'SCP']).diff()[['ENTRIES', 'EXITS']]
# sometimes counters are reset, leading to negative counts - set min to 0
# sometimes counters go crazy, leading to insanely large counts - set max to 1 per second for 4 hour interval
# todo more sophisticated if counts are above 0 in first interval after reset
df[['ENTRIES_P', 'EXITS_P']] = df[['ENTRIES_P', 'EXITS_P']].clip(lower=0, upper=14400)

# total entrances and exits per station
# multiple stations can have the same name, e.g., 77 ST, so uniquely id stations by STATION, LINENAME
station_totals = df.groupby(['STATION', 'LINENAME'])['ENTRIES_P', 'EXITS_P'].sum()


station = '77 ST'
line = 'R'


def generate_station_series(station, line):
    return df[(df.STATION == station) & (df.LINENAME == line)].groupby('DATE_TIME').sum().reset_index()


def plot_station_over_time(station, line):
    station_series = generate_station_series(station, line)
    plt.plot(station_series.DATE_TIME, station_series.ENTRIES_P)
    plt.plot(station_series.DATE_TIME, station_series.EXITS_P)
    plt.legend()
    plt.show()


def plot_people_in_town(station, line):
    station_series = generate_station_series(station, line)

    # some stations have exit-only turnstiles that don't record data.
    # to account for this, make the assumption that over a week, there are the same number
    # of entries and exits per station, and adjust accordingly
    proportion_entries_exits = station_series.sum().ENTRIES_P / station_series.EXITS_P.sum()
    station_series.EXITS_P *= proportion_entries_exits

    # number of people in town is the difference between # that enter town (exit station) and exit town (enter station)
    station_series['IN_TOWN'] = station_series.EXITS_P - station_series.ENTRIES_P
    plt.plot(station_series.DATE_TIME, station_series.IN_TOWN.cumsum())
    plt.xticks(rotation=90)
    plt.legend()
    plt.show()
