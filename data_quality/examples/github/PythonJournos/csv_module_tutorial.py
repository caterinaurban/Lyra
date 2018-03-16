#!/usr/bin/env python
# https://github.com/PythonJournos/LearningPython/blob/master/tutorials/textfiles101/csv_module_tutorial.py
"""
This script shows how to read and write data using Python's built-in csv module.
The csv module is smart enough to handle fields that contain apostrophes,
commas and other common field delimiters. In this tutorial, we'll show how to:
 * use csv to read data
 * work with CSV column headers
 * read data as a stream
 * write data back out using csv

The official Python docs for the csv module can be found here:
  http://docs.python.org/library/csv.html

For this tutorial, we're using a subset of the FDIC failed banks list:
  http://www.fdic.gov/bank/individual/failed/banklist.html

"""
import csv
from datetime import datetime

print("\n\nExample 1: Split lines manually\n")

for line in open('data/banklist_sample.csv'):
    clean_line = line.strip()
    data_points = clean_line.split(',')
    print(data_points)

print ("\n\nExample 2: Read file with the CSV module\n")

bank_file = csv.reader(open('data/banklist_sample.csv', 'rb'))

for record in bank_file:
    print(record)

print("\n\nExample 3: Read tab-delimited data\n")

bank_file = csv.reader(open('data/banklist_sample.tsv', 'rb'), delimiter='\t')

for record in bank_file:
    print(record)

print("\n\nExample 4: Extracting Column Headers and Writing Out Data\n")

# Read all lines using a list comprehension
bank_records = [line for line in csv.reader(open('data/banklist_sample.tsv', 'rb'), delimiter='\t')]

# Pop header from the start of the list and save it
header = bank_records.pop(0)
print(header)

# Open a new file object
outfile = open('data/banklist_sample_reformatted_dates.tsv', 'wb')

# Create a writer object
outfileWriter = csv.writer(outfile, delimiter='\t')

# Write out the header row
outfileWriter.writerow(header)

# Now process and output the remaining lines.
for record in bank_records:
    # Do some basic processing and then write the data back out

    # Below, we use Python's built-in datetime library to reformat
    # the Closing and Update dates.

    # First, we use the "strptime" method to parse dates formatted
    # as "23-Feb-11" into a native Python datetime object.

    # Then we apply the "strftime" method to the resulting datetime
    # object to create a date formatted as YYYY-MM-DD.
    record[-1] = datetime.strptime(record[-1], '%d-%b-%y')
    record[-1] = record[-1].strftime('%Y-%m-%d')

    # We can combine the above steps into a single line
    record[-2] = datetime.strptime(record[-2], '%d-%b-%y').strftime('%Y-%m-%d')

    # Print to the shell and write data out to file
    print(record)
    outfileWriter.writerow(record)

# Closing the file ensures your data flushes out of the buffer
# and writes to the output file
outfile.close()

print("\n\nExample 5: Reading Large Files as a Stream\n")

# Create a csv file object
bank_file = csv.reader(open('data/banklist_sample.tsv', 'rb'), delimiter='\t')

# Grab the header line from the file by calling the file object's next method
header = bank_file.next()
print(header)

# Now proceed to process the remaining lines as normal
for record in bank_file:
    print(record)
