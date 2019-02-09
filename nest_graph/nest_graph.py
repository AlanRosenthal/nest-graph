#!/usr/bin/env python
"""
"""
import click
import zipfile
import os
import json


NEST_THERMOSTATS_FOLDER = os.path.join("NEST_DATA", "Nest", "thermostats")


def parse_summary_json(data):
    output = {"events": [], "cycles": []}

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

            output["events"].append(
                {
                    "start": x["startTs"],
                    "duration": x["duration"],
                    "type": x["eventType"],
                    "value": value,
                }
            )

        # Save each cycle
        for x in data[day]["cycles"]:
            output["cycles"].append({"start": x["startTs"], "duration": x["duration"]})

    return output


def print_summary_data(data):
    print("Events:")
    for x in data["events"]:
        print(
            f"\tstart: {x['start']} duration: {x['duration']} type: {x['type']} value: {x['value']}"
        )

    print("Cycles:")
    for x in data["cycles"]:
        print(f"\tstart: {x['start']} duration: {x['duration']}")


def parse_data(folder, year, month):
    summary_file = os.path.join(folder, year, month, f"{year}-{month}-summary.json")
    print(f"Reading from: {summary_file}")
    with open(summary_file) as f:
        json_data = json.load(f)
        summary_data = parse_summary_json(json_data)

    print_summary_data(summary_data)


@click.command()
@click.version_option()
@click.option("--archive", help="Nest Data archive", required=True)
@click.option("--extract-to", help="Extract to folder", default="archive")
@click.option("--thermostat-id", help="Extract to folder", default=None)
@click.option("--date", help="date year,month", nargs=2, default=None)
def main(archive, extract_to, thermostat_id, date):
    with zipfile.ZipFile(archive, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    thermostats_folder = os.path.join(extract_to, NEST_THERMOSTATS_FOLDER)
    if thermostat_id is None:
        print("Must use the --thermostat-id flag")
        print("List of available thermostats:")
        for x in os.listdir(thermostats_folder):
            print(f"Thermostat ID: {x}")
        exit(1)

    selected_thermostat_folder = os.path.join(thermostats_folder, thermostat_id)

    available_months = []
    if date is None:
        for year in os.listdir(selected_thermostat_folder):
            for month in os.listdir(os.path.join(selected_thermostat_folder, year)):
                available_months.append((year, month))
    else:
        available_months.append(date)

    for year, month in available_months:
        parse_data(selected_thermostat_folder, year, month)


if __name__ == "__main__":
    main()
