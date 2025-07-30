## DRAINAGE DISCHARGE EVENT ANALYSIS

Catches *EVENTS* separating the event flow from base flow

 
## Instructions 

'''
pip install EVENT_PACKAGE - This allows you install the package in shells like anaconda and powershell
'''

There are two such categories to this package

a. You have the daily event data that can be called when the discharge data is in the daily data resolution 'from EVENT_PACKAGE import daily_event'

b. You have the hourly event data that can be called when the discharge data is in the hourly data resolution 'from EVENT_PACKAGE import hourly_event'

## DATA TYPES

This code would require that you input at least Three (3) data sets

## DATA A - Discharge data

The Date in the first column of the CSV file


## DATA B - DATES

The discharge data should be saved in a in the second column of the CSV file


## DATA C - DATES

The concentration on the third column of the CSV file. if you do not have the concentration, fill up the column with '1's.

## Hourly Date Format

hourly data should be of the form mm/dd/yy hh:mm   example: 10/03/2025 2:00 (for October 3rd 2025 second hour (2nd hour)))

Note the time resolution is in the 24 hours scale 0:00 - 23:00


## Daily Date Format

daily date should be in the form dd/mm/yy   example: 10/01/2023 (for 10th January 2023)


## Files names

The program asks for the name of the CSV file. Note!! - the file type ".csv" is important
Example:
if the file name is data.csv the code input should be 'data.csv' (Including the file type)

## DATA ORGANIZATION IN THE CSV FILE

# Daily

for daily data analysis, the data should be arranged in the format  below

| Date | Drainage Discharge | Concentration | Water Table | Water Temp |

Note: You might not input all the date if for example you do not have Water table depth and/or Water Temp. 

However, you must input the first 3 data columns must be filled.

If you do not have the Concentration data, fill up the column with '1'.

Example:
Concentration
1
1
1
...

b. event_data.txt for the daily drainage discharge TXT file

# hourly data

for hourly data analysis, the data should be arranged in the format  below

| Date | Drainage Discharge | Concentration | Water Table | Water Temp |

Note: You might not input all the date if for example you do not have Water table depth and/or Water Temp. 

However, you must input the first 3 data columns must be filled.

If you do not have the Concentration data, fill up the column with '1'.

Example:
Concentration
1
1
1
...

# Location of txt file

The CSV files should be save in the same folder as the code (Running script)

## EXCUTE THE CODE

To excute the code you need to just call the package depending on what data you want to analyse

# For Daily Event Analysis

from EVENT_PACKAGE import daily_event

# hourly Event Analysis

from EVENT_PACKAGE import hourly_event

## NOTES!!!!

1. MISSING DATA DOES NOT AFFECT THE PLOT SO DO NOT WORRY ABOUT CLEANING MISSING DATA.