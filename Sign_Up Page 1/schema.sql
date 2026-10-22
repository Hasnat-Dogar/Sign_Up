create database Sign_Up;
Use Sign_Up;
Create Table Users(
Id int auto_increment primary key,
user_name varchar(30) Unique Not Null,
email varchar(50) Unique Not Null,
Constraint chk_gmail Check (email like '%@gmail.%'),
Password_hash varchar(30),
created_at Timestamp Default Current_Timestamp
);
