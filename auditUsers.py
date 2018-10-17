##################################################################################################
#
#	Name		: auditUsers.py
#	Creation Date 	: 2018-10-15
#	Version 	: 1.0 
#	
#	Requires Python3
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
#
####################################################################################################

import os
import sys
import time

inputFileName = "audit.user.0.0.log"



totalAttempts = 0
totalSuccesses = 0
totalFailures = 0 
totalSuccessDict = dict() #total successful logins per day
uniqueSuccessArr = [] # unique successful logins per day 
uniqueUserList = [] # holds the date and unique users, gets cleared for each date 
earliestDate = "01/01/1970"
lastDate = "01/01/1970"

try:
	#find OS and create results directory for output files 
	localFolder = os.path.abspath("")
	OSType = sys.platform 
	if str(OSType) != "win32":
		resultsFolder = localFolder+'/results/'
		os.mkdir(resultsFolder)
	else: 
		resultsFolder = localFolder+'\\results\\'
		os.mkdir(resultsFolder)
except:
	print("results directory already created") 

strDateTime = str(time.strftime("%Y%m%d_%H%M%S",time.localtime()))

	
# Output File Names
successList = os.path.join(resultsFolder,"successList-"+strDateTime+".csv") #For each successful Login Print - Date,UserName
usersPerDay = os.path.join(resultsFolder,"uniqueUsersPerDay-"+strDateTime+".txt") #Prints list of unique usernames per day 
uniqueSuccessGraph = os.path.join(resultsFolder,"uniqueSuccessGraph-"+strDateTime+".csv") #prints Date,# of unique logins for that day to be able to graph in excel
failureList = os.path.join(resultsFolder,"failureList-"+strDateTime+".csv") #For each failed login print - Date,UserName 
successGraph = os.path.join(resultsFolder,"successGraph-"+strDateTime+".csv") # prints Date, total # of logins for that day to be able to graph 
summaryFile = os.path.join(resultsFolder,"summary-"+strDateTime+".txt") #Print Summary with totals and list of unique users


with open(inputFileName) as inputFile: #Open & Read in each line of the Audit User Log
	#begin main loop
	for line in inputFile:
		linePieces = line.strip()
		linePieces = linePieces.split() #split the incoming line on a "space" character
		if linePieces[3] == "WebUI" and linePieces[4] == "Login": # If someone tries to login 
			if linePieces[5] != "failed":	# and it sucessful
				totalSuccesses += 1 #Increment Counters
				totalAttempts += 1
				
				#Keep track of total successes for a single day
				#First add one to the count if the date already exists
				if linePieces[0] in totalSuccessDict:
					updatedValue = int(totalSuccessDict[linePieces[0]]) + 1
					strUpdatedValue = str(updatedValue)
					updatedInfo = {linePieces[0]: strUpdatedValue}
					totalSuccessDict.update(updatedInfo)
				#If the date doesn't exist, add it to the dictionary with an initial value of 1
				else:
					totalSuccessDict[linePieces[0]] = "1"
								
				#For each successful Login Print - Date and UserName
				userName = linePieces[7].split(',')
				outputSuccessFile = open(successList, "a")
				outputSuccessFile.write(linePieces[0]+","+userName[0]+"\n") #print success
				
				#need to make sure usernames aren't repeated (John.Doe would be different than john.doe)
				uniqueUser = userName[0].lower()
				if uniqueUser not in uniqueUserList: #keeps a list of unique users to print out later
					uniqueUserList.append(uniqueUser)
				
				# find number of unique logins per day 
				#if date already in list and userName not it list, add user 
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
				
				userName = linePieces[8].split(',')
				outputFailureFile = open(failureList, "a")
				outputFailureFile.write(linePieces[0]+","+userName[0]+"\n") #or write failure
	#end main loop 
				
#print last date for unique user logins
outputUniqueUsersPerDayFile = open(usersPerDay,"a")
outputUniqueUsersPerDayFile.write(str(uniqueSuccessArr)+"\n")
lastDate = uniqueSuccessArr[0]

outputUniqueLoginFile = open(uniqueSuccessGraph,"a")
outputUniqueLoginFile.write(uniqueSuccessArr[0]+","+ str(len(uniqueSuccessArr) - 1)+"\n")
				
# after going through the file, print out number of successful logins per day 
# if you open this up in excel, you can easily make a graph of total logins per day 				
for k, v in totalSuccessDict.items():
	outputSuccessGraphFile = open(successGraph, "a")
	outputSuccessGraphFile.write(k + "," + v + "\n")
	
#Print Summary with totals and list of unique users 
outputSummaryFile = open(summaryFile, "a")
outputSummaryFile.write("Total Attempts   	 : "+str(totalAttempts)+"\n")
outputSummaryFile.write("Total Successful 	 : "+str(totalSuccesses)+"\n")
outputSummaryFile.write("Total Failures   	 : "+str(totalFailures)+"\n\n\n")
outputSummaryFile.write("Earliest Login Date : "+str(earliestDate)+"\n")
outputSummaryFile.write("Last Login Date	 : "+str(lastDate)+"\n\n\n")
outputSummaryFile.write("Unordered List of Unique Users : \n")

for user in uniqueUserList:
	outputSummaryFile.write(user+"\n")

#close all files
outputSuccessFile.close()
outputUniqueUsersPerDayFile.close()
outputUniqueLoginFile.close()
outputFailureFile.close()
outputSuccessGraphFile.close()
outputSummaryFile.close()
