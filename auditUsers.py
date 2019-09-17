##################################################################################################
#
#	Name		: auditUsers.py
#	Creation Date 	: 2018-10-15
#	Update : 2019-08-10
#	Version 	: 2.1 
#	
#	Requires : Python3
#			   Dynatrace Managed v158+
#
#	Use : Place auditUsers.py in the same directory as the audit.user.0.0.log 
#		 and run the script. It will create a results directory with the 
#		 output files. 
#
#	Purpose : Read through the Dynatrace Managed audit.user.0.0.log file to find :
#		1.) Total User Logins per Day - successList.csv & successGraph.csv
#		2.) Unique User logins per day - uniqueUsersPerDay.txt & uniqueSuccessGraph.csv
#		3.) Failed User Logins by day - failureList.csv
#		4.) List of Unique Users - summary.txt
#		5.) Lists number of logins per user - loginsPerUser.csv
#
####################################################################################################

import os
import sys
import time
import json
import logging

inputFileName = "full.audit.user.0.0.log"

totalAttempts = 0
totalSuccesses = 0
totalFailures = 0 
totalSuccessDict = dict() #total successful logins per day
uniqueSuccessArr = [] # unique successful logins per day 
uniqueUserList = [] # holds the date and unique users, gets cleared for each date 
loginsPerUser = dict() # holds number of logins for each user 
earliestDate = "01/01/1970"
lastDate = "01/01/1970"
strDateTime = str(time.strftime("%Y%m%d_%H%M%S",time.localtime())) #date&time for output files
isDevOps = True # used to remove DevOps access to the Web UI through Mission Control 

#set up logging 
logFileName = "audit-user-logs-log."+strDateTime+".log"
#logging.basicConfig(filename=logFileName,level=logging.DEBUG)
logging.basicConfig(filename=logFileName,level=logging.INFO)
logging.info('Log File Open')

logging.info('Create Results Folder/Directory')
try:
	#find OS and create results directory for output files 
	localFolder = os.path.abspath("")
	OSType = sys.platform 
	if str(OSType) != "win32":
		resultsFolder = localFolder+'/audit-user-results/'
		os.mkdir(resultsFolder)
	else: 
		resultsFolder = localFolder+'\\audit-user-results\\'
		os.mkdir(resultsFolder)
except:
	logging.info("results directory already created") 


logging.info('Defining Output File Names')
# Output File Names
successList = os.path.join(resultsFolder,"successList-"+strDateTime+".csv") #For each successful Login Print - Date,UserName
usersPerDay = os.path.join(resultsFolder,"uniqueUsersPerDay-"+strDateTime+".txt") #Prints list of unique usernames per day 
uniqueSuccessGraph = os.path.join(resultsFolder,"uniqueSuccessGraph-"+strDateTime+".csv") #prints Date,# of unique logins for that day to be able to graph in excel
failureList = os.path.join(resultsFolder,"failureList-"+strDateTime+".csv") #For each failed login print - Date,UserName 
successGraph = os.path.join(resultsFolder,"successGraph-"+strDateTime+".csv") # prints Date, total # of logins for that day to be able to graph 
summaryFile = os.path.join(resultsFolder,"summary-"+strDateTime+".txt") #Print Summary with totals and list of unique users
loginsPerUserFile = os.path.join(resultsFolder,"loginsPerUser-"+strDateTime+".csv") #Print # of Logins for each user over course of Audit log file 


logging.info('Main Loop Begin')
with open(inputFileName) as inputFile: #Open & Read in each line of the Audit User Log
	#begin main loop
	logging.debug('Audit Log File Open')
	for line in inputFile:
		linePieces = line.strip()
		logging.debug('Splitting Line')
		linePieces = linePieces.split(" ", 3) #split the incoming line on a "space" character 3 times to keep full JSON string
		
		logging.debug('Testing to see if Audit Logs contains non JSON Lines')
		try:
			json_object = json.loads(linePieces[3])
		except ValueError as e:
			logging.warning('Not all log lines are JSON Formatted')
			sys.exit()
		
		#JSON Specific Log Lines 
		logging.debug('Pulling out JSON String')
		fullJSONString=linePieces[3] #capture full JSON string from split out line pieces
		logging.debug(fullJSONString)
		JSONLogDict = json.loads(fullJSONString) #turn FullJSONString into Python Dictionary
		logging.debug('JSON Converted to Dictionary')
		
		#check if user is a DevOps user from Dynatrace
		if "DevOpsToken" in JSONLogDict["userId"]:
			isDevOps = True
		else: 
			isDevOps = False

		if JSONLogDict["identityCategory"] == "WEB_UI" and JSONLogDict["eventType"] == "LOGIN" and JSONLogDict["userIdType"] == "USER_NAME" and isDevOps is False: # If a real user not using Mission Control logins in  
			logging.debug('WebUI Login Attempt')
			if JSONLogDict["success"] is True:	# and it sucessful
				logging.debug('Successful WebUI Login')
				totalSuccesses += 1 #Increment Counters
				totalAttempts += 1
				
				#Keep track of total successes for a single day
				#First add one to the count if the date already exists
				if linePieces[0] in totalSuccessDict:
					updatedValue = int(totalSuccessDict[linePieces[0]]) + 1
					strUpdatedValue = str(updatedValue)
					updatedInfo = {linePieces[0]: strUpdatedValue}
					totalSuccessDict.update(updatedInfo)
					logging.debug('Subsquent Login for the day - '+linePieces[0])
				#If the date doesn't exist, add it to the dictionary with an initial value of 1
				else:
					totalSuccessDict[linePieces[0]] = "1"
					logging.debug('First login of the day - '+linePieces[0])
				#For each successful Login Print - Date and UserName
				userName = JSONLogDict["userId"]
				outputSuccessFile = open(successList, "a")
				outputSuccessFile.write(linePieces[0]+","+userName+"\n") #print success
				
				logging.debug('Adding user to Unique User List')
				#need to make sure usernames aren't repeated (John.Doe would be different than john.doe)
				uniqueUser = userName.lower()
				if uniqueUser not in uniqueUserList: #keeps a list of unique users to print out later
					uniqueUserList.append(uniqueUser)
				
				logging.debug('Counting number of logins for each uniqueUser')
				#keeps track of number of logins for each user over course of Audit Log File 
				if uniqueUser in loginsPerUser:
					updatedValue = int(loginsPerUser[uniqueUser]) + 1
					strUpdatedValue = str(updatedValue)
					updatedInfo = {uniqueUser: strUpdatedValue}
					loginsPerUser.update(updatedInfo)
					logging.debug('Subsequent Login for User')
				else:
					logging.debug('Adding User ' + uniqueUser + ' for First Login')
					loginsPerUser[uniqueUser] = "1" 
					logging.debug('First Login for User')
					
				# find number of unique logins per day 
				#if date already in list and userName not it list, add user 
				logging.debug('Find Unique Logins Per Day')
				if(linePieces[0].strip() in uniqueSuccessArr) and (uniqueUser not in uniqueSuccessArr):
					uniqueSuccessArr.append(uniqueUser)
				#if the date is the next day, and there is already data in the list, write out the old data
				#clear out the list and begin the next days list 
				elif linePieces[0].strip() not in uniqueSuccessArr:
					if len(uniqueSuccessArr) > 0:
					
						outputUniqueUsersPerDayFile = open(usersPerDay,"a")
						outputUniqueUsersPerDayFile.write(str(uniqueSuccessArr)+"\n")
					
						outputUniqueLoginFile = open(uniqueSuccessGraph,"a")
						outputUniqueLoginFile.write(uniqueSuccessArr[0]+","+ str(len(uniqueSuccessArr) - 1)+"\n")
						uniqueSuccessArr.clear() 
						uniqueSuccessArr.append(linePieces[0].strip())
						uniqueSuccessArr.append(uniqueUser)
					#this else statement controls the first run because the list is empty so there is nothing to write out
					#but the information needs to be added to this list 
					else:
						earliestDate = linePieces[0]
						uniqueSuccessArr.append(linePieces[0].strip())
						uniqueSuccessArr.append(uniqueUser)
				
				
				#if it is a failed log in, keep track of it and add it to the list 
			else:
				totalFailures += 1
				totalAttempts += 1
				
				userName = JSONLogDict["userId"]
				outputFailureFile = open(failureList, "a")
				outputFailureFile.write(linePieces[0]+","+userName+","+JSONLogDict["message"]+"\n") #or write failure
	#end main loop 
				
#print last date for unique user logins
outputUniqueUsersPerDayFile = open(usersPerDay,"a")
outputUniqueUsersPerDayFile.write(str(uniqueSuccessArr)+"\n")
lastDate = uniqueSuccessArr[0]

outputUniqueLoginFile = open(uniqueSuccessGraph,"a")
outputUniqueLoginFile.write(uniqueSuccessArr[0]+","+ str(len(uniqueSuccessArr) - 1)+"\n")
				
# after going through the file, print out number of successful logins per day 
# if you open this up in excel, you can easily make a graph of total logins per day 
logging.info('Writing Successful logins per day to CSV File')				
for k, v in totalSuccessDict.items():
	outputSuccessGraphFile = open(successGraph, "a")
	outputSuccessGraphFile.write(k + "," + v + "\n")
	
#Print Summary with totals and list of unique users 
logging.info('Writing out Summary Output File')
outputSummaryFile = open(summaryFile, "a")
outputSummaryFile.write("Total Attempts   	 : "+str(totalAttempts)+"\n")
outputSummaryFile.write("Total Successful 	 : "+str(totalSuccesses)+"\n")
outputSummaryFile.write("Total Failures   	 : "+str(totalFailures)+"\n\n\n")
outputSummaryFile.write("Earliest Login Date : "+str(earliestDate)+"\n")
outputSummaryFile.write("Last Login Date	 : "+str(lastDate)+"\n\n\n")
outputSummaryFile.write("Unordered List of Unique Users : \n")

logging.info('Writing all unique users to Summary Output File')
for user in uniqueUserList:
	outputSummaryFile.write(user+"\n")

#writing out Logins per UserName to file : 
for k, v in loginsPerUser.items():
	outputloginsPerUserFile = open(loginsPerUserFile, "a")
	outputloginsPerUserFile.write(k + "," + v + "\n")

#close all files
logging.info('Closing Output Files')
outputSuccessFile.close()
outputUniqueUsersPerDayFile.close()
outputUniqueLoginFile.close()
outputFailureFile.close()
outputSuccessGraphFile.close()
outputSummaryFile.close()
outputloginsPerUserFile.close()
logging.info('Script Exit Successfully') 
