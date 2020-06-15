#!/usr/bin/env python3

from sys import argv
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

from math import sin, cos, sqrt, atan2, radians

def diff_lon_lat_in_metters(lat1, lon1, lat2, lon2):
    """
    http://stackoverflow.com/questions/19412462/ddg#19412565
    """
    # approximate radius of earth in m
    R = 6373000.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def trkpt_distance(trkpt1, trkpt2):
    lat_lon = [float(x) for x in [trkpt1.get('lat'), trkpt1.get('lon'), trkpt2.get('lat'), trkpt2.get('lon')]]
    return diff_lon_lat_in_metters(*lat_lon)

def trkpt_add_timestamp(trkpt, timestamp):
    """
    Strava supported time format is from here: https://gist.github.com/cast42/a7df6a4a77a5818c1fc3
    """
    time_element = ET.Element('time')
    time_element.text = str(timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"))
    print('time.text:', time_element.text)
    trkpt.append(time_element)

def gpx_add_time_with_avg_speed(gpx_filename, start_time, end_time):
    tree = ET.parse(gpx_filename)
    root = tree.getroot()

    trk = root[0]
    overall_distance = 0
    for child in trk:
        print(child.tag)
        if child.tag == '{http://www.topografix.com/GPX/1/1}trkseg':
            trkseg = child
            for trkpt in trkseg:
                print("         ", end='')
                print(trkpt.tag, trkpt.attrib)
            trkpt1 = trkseg[0]
            trkpt2 = trkseg[1]
            overall_distance += trkpt_distance(trkpt1, trkpt2)

    overall_timedelta = end_time - start_time
    avg_speed_mps = overall_distance / overall_timedelta.total_seconds()
    current_timestamp = start_time
    for child in trk:
        if child.tag == '{http://www.topografix.com/GPX/1/1}trkseg':
            trkseg = child
            trkpt1 = trkseg[0]
            trkpt2 = trkseg[1]
            trkpt_add_timestamp(trkpt1, current_timestamp)
            distance = trkpt_distance(trkpt1, trkpt2)
            step_timedelta = timedelta(seconds=distance / avg_speed_mps)
            current_timestamp = current_timestamp + step_timedelta
            trkpt_add_timestamp(trkpt2, current_timestamp)

    tree.write('temp.gpx')

def fix_improper_formating(temp_filename, output_filename):
    with open(temp_filename, 'r') as f:
        input_text = f.read()
    cleared_text = input_text.replace('ns0:', '')
    lines = cleared_text.split('\n')
    cleared_text = "\n".join(lines[1:])
    gpx_file_header = """<?xml version="1.0"?>
<gpx xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1" xmlns:gpxedw="http://www.gpxeditor.co.uk/xmlschemas/WaypointExtension/v1" xmlns:gpxedts="http://www.gpxeditor.co.uk/xmlschemas/TrackSegExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" creator="GPXEditor" version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
"""
    output_text = gpx_file_header + cleared_text
    with open(output_filename, 'w') as f:
        f.write(output_text)

def main():
    if len(argv) != 4:
        print('''usage: ./gpx_track_timestamp_adder.py filename.gpx start_time end_time
time format: %d/%m/%YT%H:%M:%S
e.g: ./gpx_track_timestamp_adder.py Untitled.gpx 15/06/2020T19:30:00 15/06/2020T23:20:00''')
        return
    start_time = datetime.strptime(argv[2], "%d/%m/%YT%H:%M:%S")
    end_time = datetime.strptime(argv[3], "%d/%m/%YT%H:%M:%S")

    gpx_add_time_with_avg_speed(argv[1], start_time, end_time)
    fix_improper_formating('temp.gpx', 'output.gpx')


if __name__ == "__main__":
    main()
