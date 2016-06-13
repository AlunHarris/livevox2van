#!/usr/local/bin/python

import sys
import csv
import re
import time


# LIVEVOX LOOKUP TABLES

# Mapping of LiveVox export headers to VAN headers
HEADER_LOOKUP = {
  "LivevoxResult": "Result",
  "DateCanvassedCT": "Date"
}

# Mapping of LiveVox results to VAN results
RESULTS_LOOKUP = {
  "AGENT - Busy": "Busy",
  "AGENT - CUST 1": "Spanish",
  "AGENT - CUST 2": "Not Home",
  "AGENT - CUST 3": "Refused",
  "AGENT - CUST 4": "Not Home",
  "AGENT - CUST 5": "Refused",
  "AGENT - CUST 6": "Z No Contact",
  "AGENT - CUST 7": "Deceased",
  "AGENT - CUST 8": "Other Language",
  "AGENT - CUST 9": "Moved",
  "AGENT - CUST 11": "Z No Contact",
  "AGENT - CUST 12": "1 - Strong Sanders",
  "AGENT - CUST 13": "1 - Strong Sanders/Vol Yes",
  "AGENT - CUST 14": "1 - Strong Sanders/NPP Requested Ballot",
  "AGENT - CUST 15": "2 - Lean Sanders/NPP Requested Ballot",
  "AGENT - CUST 18": "1 - Strong Sanders/Re-Registered as Dem/Vol Yes",
  "AGENT - CUST 19": "1 - Strong Sanders/Re-Registered as Dem",
  "AGENT - CUST 20": "1 - Strong Sanders/Re-Registered as Dem",
  "AGENT - CUST 21": "1 - Strong Sanders/Re-Registered as Dem/Vol Yes",
  "AGENT - CUST 22": "1 - Strong Sanders/Re-Registered as Dem",
  "AGENT - CUST 23": "1 - Strong Sanders/NPP Requested Ballot",
  "AGENT - CUST 24": "1 - Strong Sanders/No Ballot Action",
  "AGENT - CUST RPC 1": "1 - Strong Sanders",
  "AGENT - CUST RPC 2": "2 - Lean Sanders",
  "AGENT - CUST RPC 3": "3 - Undecided",
  "AGENT - CUST RPC 4": "4 - Lean Clinton",
  "AGENT - CUST RPC 5": "5 - Strong Clinton",
  "AGENT - CUST RPC 6": "6 - Other",
  "AGENT - CUST RPC 7": "1 - Strong Sanders/Vol Yes",
  "AGENT - CUST RPC 8": "1 - Strong Sanders/In Person EV",
  "AGENT - CUST RPC 9": "1 - Strong Sanders/Send Form EV",
  "AGENT - CUST RPC 10": "7 - Not Voting",
  "AGENT - CUST RPC 11": "6 - Other",
  "AGENT - CUST RPC 12": "2 - Lean Sanders/In Person EV",
  "AGENT - CUST RPC 13": "1 - Strong Sanders/Absentee Vote",
  "AGENT - CUST RPC 14": "2 - Lean Sanders/Absentee Vote",
  "AGENT - CUST RPC 15": "1 - Strong Sanders/Vol Yes",
  "AGENT - CUST RPC 16": "1 - Strong Sanders/Maybe Vote",
  "AGENT - CUST RPC 17": "2 - Lean Sanders/Absentee Vote",
  "AGENT - CUST RPC 18": "1 - Strong Sanders/In Person VR",
  "AGENT - CUST RPC 19": "1 - Strong Sanders/Online VR",
  "AGENT - CUST RPC 20": "1 - Strong Sanders/Need Form VR",
  "AGENT - CUST RPC 21": "1 - Strong Sanders/Print Own Form EV",
  "AGENT - CUST RPC 22": "1 - Strong Sanders/Email Request EV",
  "AGENT - CUST RPC 23": "1 - Strong Sanders/In Person Vote",
  "AGENT - CUST RPC 24": "1 - Strong Sanders/Absentee Vote",
  "AGENT - CUST RPC 25": "1 - Strong Sanders/In Person Vote",
  "AGENT - CUST RPC 26": "1 - Strong Sanders/In Person Vote",
  "AGENT - CUST RPC 27": "1 - Strong Sanders/Not Voting/Not Registering",
  "AGENT - CUST RPC 28": "1 - Strong Sanders/Not Voting",
  "AGENT - CUST RPC 29": "1 - Strong Sanders/In Person Vote",
  "AGENT - CUST RPC 30": "1 - Strong Sanders",
  "AGENT - CUST WPC 1": "1 - Strong Sanders/Vol Yes",
  "AGENT - CUST WPC 2": "1 - Strong Sanders/Vol Yes",
  "AGENT - CUST WPC 3": "1 - Strong Sanders/Vol No",
  "AGENT - CUST WPC 4": "1 - Strong Sanders/Vol Yes",
  "AGENT - CUST WPC 5": "1 - Strong Sanders/Vol No",
  "AGENT - CUST WPC 6": "1 - Strong Sanders/Vol Yes",
  "AGENT - CUST WPC 8": "2 - Lean Sanders/Vol Yes",
  "AGENT - CUST WPC 9": "1 - Strong Sanders/Vol Yes",
  "AGENT - CUST WPC 10": "6 - Other/Republican",
  "Answering Machine (Hung Up)": "Not home",
  "Busy": "Busy",
  "Duplicate Call (Not Made)": "Z No Contact",
  "Excluded via Compliance Policy (Not Made)": "Z No Contact",
  "Excluded via Dialing Sequence (Not Made)": "Z No Contact",
  "Fax": "Out of Order",
  "Hung Up Immediately": "Z No Contact",
  "Hung Up in Opening": "Z No Contact",
  "Invalid Phone Number": "Disconnected",
  "Invalid Phone Number (Not Made)": "Z No Contact",
  "Listened": "Z No Contact",
  "Machine Left Message": "Not Home",
  "Maximum Account Attempts Reached (Not Made)": "Z No Contact",
  "No Answer": "Not Home",
  "No Patient Home (Not Made)": "Z No Contact",
  "Not Attempted (Not Made)": "Z No Contact",
  "Operator Transfer": "Z No Contact",
  "Operator Transfer (Abandoned Max Hold Time)": "Z No Contact",
  "Operator Transfer (Agent Abandoned)": "Z No Contact",
  "Operator Transfer (Agent Terminated Call)": "Z No Contact",  
  "Operator Transfer (Caller Abandoned Before Connect)": "Z No Contact",
  "Operator Transfer (Caller Abandoned)": "Z No Contact",
  "Operator Transfer (Unidentified Party)": "Z No Contact",
  "Operator Transfer Failed (No Answer)": "Z No Contact",
  "Operator Transfer Failed (Other)": "Z No Contact",
  "Partial Message Left": "Z No Contact",
  "Specified Do Not Call (Not Made)": "Z No Contact",
  "Wireless Call Suppressed (Not Made)": "Z No Contact",
  "Account or Phone in Other File (Not Made)": "Z No Contact",
  "Do Not Call": "Refused",
}


# HELPER FUNCTIONS

# Map the LiveVox export header to the VAN import header
def map_export_header(header):
  return HEADER_LOOKUP[header] if header in HEADER_LOOKUP else header

# Map the LiveVox export result to the VAN import result
def map_export_val(value):
  return RESULTS_LOOKUP[value] if value in RESULTS_LOOKUP else value

# Write one row of data to a VAN import file
def write_import_row(file, values):
  row = "\t".join( values + ["Z"] ) + "\r\n"
  file.write( row )


# AUTOMATION SCRIPT

# Make sure LiveVox export file specified
if len(sys.argv) < 2:
  print "Please specify a LiveVox export file to parse"
  sys.exit(2)

# Read in LiveVox export file
with open(sys.argv[1], 'rb') as csvfile:
  reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
  headers = reader.next()
  state_headers = map(map_export_header, headers)
  state_files = {}

  # Go through rows in export file, translate into VAN format, and write to correct VAN import file
  for row in reader:
    # DEBUG Only
    print "DEBUG: Processing Line = " + ",".join(row)
    # Pull out state (assumes first column has format "XX-..." where XX is state code)
    if re.match("^MY[CV]", row[0]):
      state_regex = re.compile('\A(?:MY.-)?(\w\w)-(\d+)')
      state_match = re.match( state_regex, row[0] )
      state = state_match.group(1)
      vanid = state_match.group(2)
      type = "MYC" if int(vanid) >= 100000000 else "MYV"
      row[0] = vanid
    elif re.match("^\d{1,20}$", row[0]):
      state_regex = re.compile('\A([A-Za-z]{2})(?:[^A-Za-z].+)')
      state_match = re.match( state_regex, row[7] )
      state = state_match.group(1)
      vanid = row[0]
      type = "MYC" if int(vanid) >= 100000000 else "MYV"
    else:
      # If any state identification errors, skip row
      print "Unable to identify state for row: " + ",".join(row)
      continue

    # If new state, create new record and output file for state (include state and date in name)
    key = state + type
    if key not in state_files:
      filename = "_".join( [state, type, time.strftime("%Y%m%d"), "Results.txt"] )
      state_files[key] = open(filename, 'w')
      write_import_row( state_files[key], state_headers )

    # Map row to correct VAN format and write out
    import_row = []
    for i in range(len(row)):
      # Map value to VAN format if looking at results column, otherwise use value directly
      if headers[i] == 'LivevoxResult':
        import_row.append( map_export_val(row[i]) )
      else:
        import_row.append( row[i] )
    write_import_row( state_files[key], import_row )

# At end of export file, close all import files and export file
for key in state_files:
  state_files[key].close()
csvfile.close()
