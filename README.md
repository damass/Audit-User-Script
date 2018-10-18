# Audit-User-Script
Reads Dynatrace Managed Audit User Logs for Analysis. Requires Python3.

#	Use 
Place auditUsers.py in the same directory as the audit.user.0.0.log and run the script. It will create a results directory with the output files. 

# Output
1. Total User Logins per Day - successList.csv & successGraph.csv
2. Unique User logins per day - uniqueUsersPerDay.txt & uniqueSuccessGraph.csv
3. Failed User Logins by day - failureList.csv
4. List of Unique Users - summary.txt

# Future Enhancements
- Number of Logins per User
- Session Tracking
   - User Login @ HH:MM:ss & User Logout @ HH:MM:ss
