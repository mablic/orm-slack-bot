Project: slack Google Bot read user search result.

Description: This is a python bot to access to slack channel and gether user google search result, 
then storage the searching criterials into database. This bot using ORM(object-relational-mapping)
access to the database. User access to the database by @ the slack bot in the channel.

Prerequisites:

	1.google package
	2.slackclient package
	3.SQLAlchemy package
	4.Datetime package
	5.Logging package

Pre-Run:

	1.Set up token connection to your slack bot.
	2.Create database in your holds server.
		a.Example of create database:
			create table Users (
			`name` varchar(50) not null,
			`keyword` varchar(50) not null,
			`datetime` date not null,
			)
	3.Set up connection to your database.
		a.Example of connection:
			user_connection = {
			'drivername': 'mysql+mysqlconnector',
			'username': 'root',
			'password': '123456789',
			'host': 'localhost',
			'port': '3306',
			'database': 'google_search'
			}

Call:
	
	1.On the slack channel type in "google" follow up with your search criterials.
	2.@ your bot by using following options to look into the database:
		a.@yourbot findAll => find all the data in the database
		b.@yourbot select where criterial => find all the data in the database where '?' equal to '?'.

Authors: Mai He

Acknowledgemetns: https://github.com/mablic/slackGoogleBot