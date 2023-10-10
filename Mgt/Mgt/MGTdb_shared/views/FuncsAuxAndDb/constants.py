TOTAL_ISO_PER_PAGE = 100 # total number of isolates to display per page.
TOTAL_ISO_PER_DOWNLOAD = 1000000 # total number of isolates to download at the moment effectively all.
TOTAL_ISO_MICROREACT = 2000 # total number of isolates to download at the moment effectively all.
TOTAL_MGT9_ISO_DOWNLOAD = 10000 # TOTAL isolates and mgt9ap to download currently.


IsolateId = 0
IsolateName = 1
IsolateSrvStatus = 2
IsolatePrivStatus = 3 # ??

ApStart = 4
ApEnd = 27 # 30
CcStart = 28 # 31
CcEnd = 43 # 48
EpiStart = 44 # 49
EpiEnd = 51 # 56
HgtId = 3

LocId = 52 # 57
LocStart = 53 # 58
LocEnd = 56 # 61

IsolnId = 57 # 62
IsolnStart = 58 # 63
IsolnEnd = 64 #63 # 67

IsoFields = ['identifier', 'status']
IsoColsPu = [{ 'isolateId': 0,
					'isolateName': 1,
					'isolateServerStatus': 2,
					'isolateAssignStatus': 3,
					'serovar': 4,
					'mgt1': 5,
					}]

IsoColsPv = [{ 'isolateId': 0,
					'isolateName': 1,
					'isolateServerStatus': 2,
					'isolateAssignStatus': 3,
					'isolatePrivStatus': 4,
					'serovar': 5,
					'mgt1': 6,
					}]

MgtColsPu = [{ 'mgtId': 6,
                'apStart': 7,
                'apEnd': 30,
                'ccStart': 31,
                'ccEnd': 46,
                'epiStart': 47,
                'epiEnd': 54, }]

MgtColsPv = [{ 'mgtId': 8,
                'apStart': 9,
                'apEnd': 32,
                'ccStart': 33,
                'ccEnd': 48,
                'epiStart': 49,
                'epiEnd': 56, }]




# IsoLocFields = ['continent', 'country', 'state', 'postcode']
# IsoLocCols = [{ 'locId': 52, 'locStart': 53, 'locEnd': 56, }]


# IsoIslnFields = ['source', 'type', 'host', 'disease', 'date', 'year']
# IsoIslnCols = [{ 'isolnId': 57, 'isolnStart': 58, 'isolnEnd': 63, }]

ProjHeaderPv = [{"table_name": "project", "display_name": "Project", "db_col": 4}]

IsolateHeaderPu = [{"table_name": "identifier", "display_name": "Isolate", "db_col": 1}, {"table_name": "server_status", "display_name": "Server status", "db_col": 2}, {"table_name": "assignment_status", "display_name": "Assignment status", "db_col": 3}, {"table_name": "serovar", "display_name": "Serovar", "db_col":4}, {"table_name": "mgt1", "display_name": "MGT1-ST", "db_col":5}]

IsolateHeaderPv = [{"table_name": "identifier", "display_name": "Isolate", "db_col": 1}, {"table_name": "server_status", "display_name": "Server status", "db_col": 2}, {"table_name": "assignment_status", "display_name": "Assignment status", "db_col": 3}, {"table_name": "project", "display_name": "Project", "db_col": 4}, {"table_name": "privacy_status", "display_name": "Privacy", "db_col": 5}, {"table_name": "serovar", "display_name": "Serovar", "db_col":6}, {"table_name": "mgt1", "display_name": "MGT1-ST", "db_col":7}]

# , {"table_name": "privacy_status", "display_name": "Privacy status"}

# IsolateHeader = [{"table_name": "identifier", "display_name": "Isolate"}, {"table_name": "status", "display_name": "Server status"}, {"table_name": "privacy_status", "display_name": "Privacy status"}]

IsoMetaLocInfoPu = [{"table_name": "continent", "display_name": "Continent", "db_col": 56}, {"table_name": "country", "display_name": "Country", "db_col": 57}, {"table_name": "state", "display_name": "State", "db_col": 58}, {"table_name": "postcode", "display_name": "Postcode", "db_col": 59}]

IsoMetaIslnInfoPu = [{"table_name": "source", "display_name": "Source", "db_col": 61}, {"table_name": "type", "display_name": "Type", "db_col": 62}, {"table_name": "host", "display_name": "Host", "db_col": 63}, {"table_name": "disease", "display_name": "Disease", "db_col": 64}, {"table_name": "date", "display_name": "Date", "db_col": 65}, {"table_name": "year", "display_name": "Year", "db_col": 66}, {"table_name": "month", "display_name": "Month", "db_col": 67}]


IsoMetaLocInfoPv = [{"table_name": "continent", "display_name": "Continent", "db_col": 58}, {"table_name": "country", "display_name": "Country", "db_col": 59}, {"table_name": "state", "display_name": "State", "db_col": 60}, {"table_name": "postcode", "display_name": "Postcode", "db_col": 61}]

IsoMetaIslnInfoPv = [{"table_name": "source", "display_name": "Source", "db_col": 63}, {"table_name": "type", "display_name": "Type", "db_col": 64}, {"table_name": "host", "display_name": "Host", "db_col": 65}, {"table_name": "disease", "display_name": "Disease", "db_col": 66}, {"table_name": "date", "display_name": "Date", "db_col": 67}, {"table_name": "year", "display_name": "Year", "db_col": 68}, {"table_name": "month", "display_name": "Month", "db_col": 69}]
