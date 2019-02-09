#!/usr/bin/env python
"""
"""
import click
import zipfile
import os


NEST_THERMOSTATS_FOLDER = os.path.join("NEST_DATA", "Nest", "thermostats")


@click.command()
@click.version_option()
@click.option("--archive", help="Nest Data archive", required=True)
@click.option("--extract-to", help="Extract to folder", default="archive")
@click.option("--thermostat-id", help="Extract to folder", default="")
def main(archive, extract_to, thermostat_id):
    with zipfile.ZipFile(archive, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    thermostats_folder = os.path.join(extract_to, NEST_THERMOSTATS_FOLDER)
    if thermostat_id is "":
        print("Must use the --thermostat-id flag")
        print("List of available thermostats:")
        for x in os.listdir(thermostats_folder):
            print(f"Thermostat ID: {x}")
        exit(-1)

    available_months = []
    selected_thermostat_folder = os.path.join(thermostats_folder, thermostat_id)
    for year in os.listdir(selected_thermostat_folder):
        for month in os.listdir(os.path.join(selected_thermostat_folder, year)):
            available_months.append((year, month))

    print("Available data:")
    for year, month in available_months:
        # print(x)
        print(f"Year {year} Month {month}")


if __name__ == "__main__":
    main()
