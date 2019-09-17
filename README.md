# Audit-User-Script
Reads Dynatrace Managed Audit User Logs in JSON Format for Analysis. Use in conjunction with CombineAuditLogs.py. Requires Python3.

# Use 
Place auditUsers.py in the same directory as the full.audit.user.0.0.log and run the script. It will create a results directory with the output files. 

# Output
1. Total User Logins per Day - successList.csv & successGraph.csv
2. Unique User logins per day - uniqueUsersPerDay.txt & uniqueSuccessGraph.csv
3. Failed User Logins by day - failureList.csv
4. List of Unique Users - summary.txt
5. Logins Per User - loginsPerUser.csv

# Future Enhancements
- Add filtering for SaaS Audit User Logs (per Tenant)
