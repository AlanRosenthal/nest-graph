#!/usr/bin/env python
"""
"""
import click
import zipfile
import os
import json
import csv
import numpy as np
import dateutil.parser
import datetime
import pandas as pd
import plotly
import plotly.graph_objs as go


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

            # EVENT_TYPE_AWAY has x.ecoAway.targets.heatingTarget
            if "ecoAway" in x:
                value = x["ecoAway"]["targets"]["heatingTarget"]

            time = pd.to_datetime(x["startTs"])
            duration = pd.to_timedelta(x["duration"])
            events.append(
                {
                    "time": time,
                    "endtime": time + duration,
                    "type": x["eventType"],
                    "value": float(value) * 1.8 + 32,
                }
            )
            # events.append(
            #     {
            #         "time": time + duration,
            #         "endtime": time + duration,
            #         "type": x["eventType"],
            #         "value": float(value) * 1.8 + 32,
            #     }
            # )

        # Save each cycle
        for x in data[day]["cycles"]:
            time = pd.to_datetime(x["startTs"])
            duration = pd.to_timedelta(x["duration"])
            cycles.append({"time": time, "endtime": time + duration})

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
            temp = x["avg(temp)"]
            if temp is not "":
                sensors.append(
                    {
                        "time": dateutil.parser.parse(f"{date}T{time_offset}:00Z"),
                        "temp": float(x["avg(temp)"]) * 1.8 + 32,
                    }
                )

    return sensors


def parse_data(folder, year, month):
    summary_file = os.path.join(folder, year, month, f"{year}-{month}-summary.json")
    (events, cycles) = parse_summary_json(summary_file)

    sensor_file = os.path.join(folder, year, month, f"{year}-{month}-sensors.csv")
    sensors = parse_sensors_csv(sensor_file)

    return (events, cycles, sensors)


def graph_data(events, cycles, sensors):
    data = []
    shapes = []

    sensor_time = [x["time"] for x in sensors]
    sensor_temp = [x["temp"] for x in sensors]
    x = np.array(sensor_time)
    y = np.array(sensor_temp)
    p = np.argsort(x)  # sort array by time
    data.append(go.Scatter(x=x[p], y=y[p]))

    # sensor_time = [x["time"] for x in events]
    # sensor_temp = [x["value"] for x in events]
    # x = np.array(sensor_time)
    # y = np.array(sensor_temp)
    # p = np.argsort(x)  # sort array by time
    # data.append(go.Scatter(x=x[p], y=y[p]))

    for x in cycles:
        shapes.append(
            {
                "type": "rect",
                # x-reference is assigned to the x-values
                "xref": "x",
                # y-reference is assigned to the plot paper [0,1]
                "yref": "paper",
                "x0": x["time"],
                "y0": 0,
                "x1": x["endtime"],
                "y1": 1,
                "fillcolor": "orange",
                "opacity": 0.2,
                "line": {"width": 0},
            }
        )

    for x in events:
        shapes.append(
            {
                "type": "line",
                "x0": x["time"],
                "y0": x["value"],
                "x1": x["endtime"],
                "y1": x["value"],
                "line": {"color": "red", "width": 1},
            }
        )

    layout = {
        "shapes": shapes,
        "title": "Nest Data",
        "xaxis": {
            "rangeselector": {
                "buttons": [
                    {"count": 1, "label": "1d", "step": "day", "stepmode": "backward"},
                    {"count": 7, "label": "1w", "step": "day", "stepmode": "backward"},
                    {"count": 14, "label": "2w", "step": "day", "stepmode": "backward"},
                    {
                        "count": 1,
                        "label": "1m",
                        "step": "month",
                        "stepmode": "backward",
                    },
                    {"count": 1, "label": "1y", "step": "year", "stepmode": "backward"},
                    {"step": "all"},
                ]
            },
            "rangeslider": {"visible": True},
            "type": "date",
        },
    }

    fig = dict(data=data, layout=layout)
    plotly.offline.plot(fig)


@click.command()
@click.version_option()
@click.option("--archive", help="Nest Data archive", required=True)
@click.option("--extract-to", help="Extract to folder", default="archive")
@click.option("--thermostat-id", help="Extract to folder", default=None)
@click.option("--date", help="date year,month", nargs=2, default=None)
def main(archive, extract_to, thermostat_id, date):
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

    graph_data(events, cycles, sensors)


if __name__ == "__main__":
    main()
