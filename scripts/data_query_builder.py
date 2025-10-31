   
# https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,1.1/Q.Y.AUT.S1..B1GQ._Z...USD_PPP...T0102?startPeriod=2024-Q1&endPeriod=2025-Q3

HOST_URL = ("https://sdmx.oecd.org/public/rest/data/","")
AGENCY_IDENTIFIER = ("OECD.SDD.NAD", ",")
DATASET_IDENTIFIER = ("DSD_NAMAIN1@DF_QNA", ",")
DATASET_VERSION = ("1.1", "/")
DATA_SELECTION = ("Q.Y.AUT.S1..B1GQ._Z...USD_PPP...T0102", "?")
# E.g. 
start = "2025-Q1"
stop = "2025-Q2"
TIME_PERIOD = (f"startPeriod={start}&endPeriod={stop}", "&")
DATA_FORMAT= ("&format=csvfilewithlabels", "&")