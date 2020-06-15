This script helps to add timestamps to manually created gpx files, so the file can be uploaded to Strava

---


How to use:

1. Draw your route by hand in GPX editor (e.g. https://www.gpxeditor.co.uk/map)
2. Download generated file
3. Find approximate time of ride (start, end)
4. Run the script: 
```
                                     file_name    start time          end time (d/m/y h:m:s)
python3 gpx_track_timestamp_adder.py Untitled.gpx 15/06/2020T19:30:00 15/06/2020T23:20:00
```
5. Upload the file `output.gpx` to Strava here https://www.strava.com/upload/select

