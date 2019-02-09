#!/usr/bin/env python
"""
"""
import click


@click.command()
@click.version_option()
def main():
    print("todo")

if __name__ == "__main__":
    main()