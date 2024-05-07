THE MLB PROP BET TRACKER

This web application keeps track of all prop bets made by users.

Users sign in and can place 1 wager a day (under -300 odds) on any MLB player to record a Hit. 

Users can view all the pending wagers for the day, and even parlay it if they choose on the respective sportsbook site.

Users can also view a leaderboard of how well they, and others, have been betting throughout the MLB season and even view all the history bets players have made.
The beauty of this web app is that it is a system of checks and balances where any one person can update the pending bets page, and anyone can see all the history of bets and report if an error has been made.
This app can dynamically grow to scale because it utilizes AWS.


AWS resources used: 
 - IAM user and roles
 - Multiple Dynamo DB tables with additional GSI indexes
 - S3 buckets to hold static data
 - EC2 instances to host this Python application (and set with custom SGs, NACLs, VPC settings)
 - Lambda to send periodic emails about reminders/promotions
 - Everything VPC related for networking



Leaderboard

![image](https://github.com/Daniel-Higgins/mlb_prop-b_tracker/assets/32625437/3089f681-1866-423f-923b-3c819217f023)




Place bet
![image](https://github.com/Daniel-Higgins/mlb_prop-b_tracker/assets/32625437/1f1e7294-d2b2-4f0d-95ea-0372ed08a0ca)



Pending wagers
![image](https://github.com/Daniel-Higgins/mlb_prop-b_tracker/assets/32625437/c5f9c603-fecf-4e23-b062-e3eda6a3a5a3)
