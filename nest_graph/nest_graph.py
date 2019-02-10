#!/usr/bin/env python
"""
"""
import click
import zipfile
import os
import json
import csv
import numpy as np
import matplotlib.pyplot as plt


def parse_summary_json(file):
    events = []
    cycles = []

    print(f"Reading from: {file}")
    with open(file) as f:
        data = json.load(f)

    # Json file contains top level keys for each day
    for day in data:
        # Save each event
        for x in data[day]["events"]:
            value = None
            # EVENT_TYPE_HEAT has x.setPoint.targets.heatingTarget
            if "setPoint" in x:
                value = x["setPoint"]["targets"]["heatingTarget"]

            # EVENT_TYPE_AUTOAWAY has x.ecoAutoAway.targets.heatingTarget
            if "ecoAutoAway" in x:
                value = x["ecoAutoAway"]["targets"]["heatingTarget"]

            events.append(
                {
                    "time": x["startTs"],
                    "duration": x["duration"],
                    "type": x["eventType"],
                    "value": value,
                }
            )

        # Save each cycle
        for x in data[day]["cycles"]:
            cycles.append({"time": x["startTs"], "duration": x["duration"]})

    return (events, cycles)


def print_data(events, cycles, sensors):
    print("Events:")
    for x in events:
        print(x)

    print("Cycles:")
    for x in cycles:
        print(x)

    print("Sensors:")
    for x in sensors:
        print(x)


def parse_sensors_csv(file):
    sensors = []

    print(f"Reading from: {file}")
    with open(file) as f:
        data = csv.DictReader(f)

        for x in data:
            date = x["Date"]
            time_offset = x["Time"]
            sensors.append(
                {
                    "time": f"{date}T{time_offset}:00Z",
                    "temp": x["avg(temp)"],
                    "humidity": x["avg(humidity)"],
                }
            )

    return sensors


def parse_data(folder, year, month):
    summary_file = os.path.join(folder, year, month, f"{year}-{month}-summary.json")
    (events, cycles) = parse_summary_json(summary_file)

    sensor_file = os.path.join(folder, year, month, f"{year}-{month}-sensors.csv")
    sensors = parse_sensors_csv(sensor_file)

    return (events, cycles, sensors)


@click.command()
@click.version_option()
@click.option("--archive", help="Nest Data archive", required=True)
@click.option("--extract-to", help="Extract to folder", default="archive")
@click.option("--thermostat-id", help="Extract to folder", default=None)
@click.option("--date", help="date year,month", nargs=2, default=None)
def main(archive, extract_to, thermostat_id, date):
    x = np.arange(0, 5, 0.1)
    y = np.sin(x)
    plt.plot(x, y)
    plt.show()

    with zipfile.ZipFile(archive, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    thermostats_folder = os.path.join(extract_to, "NEST_DATA", "Nest", "thermostats")
    if thermostat_id is None:
        print("Must use the --thermostat-id flag")
        print("List of available thermostats:")
        for x in os.listdir(thermostats_folder):
            print(f"Thermostat ID: {x}")
        exit(1)

    selected_thermostat_folder = os.path.join(thermostats_folder, thermostat_id)

    available_months = []
    if not date:
        for year in os.listdir(selected_thermostat_folder):
            for month in os.listdir(os.path.join(selected_thermostat_folder, year)):
                available_months.append((year, month))
    else:
        available_months.append(date)

    events = []
    cycles = []
    sensors = []
    for year, month in available_months:
        (e, c, s) = parse_data(selected_thermostat_folder, year, month)
        events.extend(e)
        cycles.extend(c)
        sensors.extend(s)

    print(len(events))
    print(len(cycles))
    print(len(sensors))


if __name__ == "__main__":
    main()
