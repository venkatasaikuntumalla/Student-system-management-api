## Table of Contents
 - [About](#about)
 - [Features](#features)
 - [Installation and Usage](#installation-and-usage)
    - [How to run the app locally (Installation)](#how-to-run-the-app-locally)
    - [Usage](#usage)
 - [Endpoints](#endpoints)
    - [Auth Enpoints](#auth-enpoints)
    - [Student Enpoints](#student-enpoints)
    - [Course Enpoints](#course-enpoints)
 - [Languages and Tools Used](#languages-and-tools-used)
 - [Screenshots](#screenshots)
 - [Acknowledgements](#acknowledgements)


## About
This is a student management REST-API which was built using python Flask and Flask-smorest that enables users to add students,courses and grade the students as well.
The application can be used for the following:

## Features
- Register students into the school's system
- Create new users to manage the application
- Administrators and users can add or register students. Student ID and password will be automatically generated once they are registered
- Students can login with Student ID and password provided upon registeration
- Administrators of the application can add a new course to which students can later login to enroll for the course of thier choice
- Administrators and users of the application can add scores for students based on the courses they are enrolled under. 
- This application automatically calculates the grades and GPA of students once a student is registered and enrolls for a course or courses
- All courses should have a code which students will use to enroll. E.g A Computer Science course can have a course code as CS001
- Once logged in, a student can view all available courses to enroll for, he or she can view all the course enrolled under as well as the grades for each course
- Students can also view thier basic details or information, request for a password change if forgotten, and also be able to change thier passwords.
- All other routes except enrolling for a course can be accessed by an Administrator.
- However, a user who is not an administrator has some restrictions like deleting a student or course.
- This application also enables the user to retrieve all students and all courses. One can also view a student by his or her ID and also view a course by its code
- You can also view all the students enrolled for a particular course as well as all the courses a particular student has enrolled for
- All the grades of each student for a particular course can also be retrieved. A student can also retrieve all the grades for all the courses they have enrolled for
- Students can view thier GPA. However, users and administrators can view the GPA of all students

## Installation and Usage
- To try this application, you can either clone and run it locally on your PC or visit the site [here](https://students-management-system-api.herokuapp.com/) to check it out.

- Follow the steps below to run and test the application locally

## How to run the app locally
1. Clone this app
```
git clone https://github.com/kojosimtema/students-management-system-api.git
``` 
2. cd to the root directorate of the project and create your virtual environment
```
cd student-management-api

python -m venv env_name
``` 
3. Activate your virtual environment
```
source env_name/Scripts/activate "for windows"
``` 
```
source env_name/bin/activate "for linus and MacOS"
``` 
4. Install all packages from the requirements.txt file
```
pip install -r requirements.txt
``` 


## Usage
**Before you run the application locally, do the following:**

**1. In the run.py file remove the *"config=config_dict['prod']"* argument from the create_app function as below to run in development mode**
```
from api import create_app
from api.main.config.config import config_dict

app = create_app(config=config_dict['prod'])

if __name__ == '__main__':
    app.run()
```
```
from api import create_app
from api.main.config.config import config_dict

app = create_app()

if __name__ == '__main__':
    app.run()
```
**2. Navigate to api/main/config and comment line 7 to 9, line 64 to 67 and uncomment line 68 in the config.py file**
```
import os
from decouple import config
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

uri = os.getenv('DATABASE_URL') #or other relevant config var
if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)

```
```
import os
from decouple import config
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

#uri = config('DATABASE_URL') #or other relevant config var
#if uri.startswith('postgres://'):
#    uri = uri.replace('postgres://', 'postgresql://', 1)

```
**3. Create the database using flask shell as follows;**
- Set the flask app

```
export FLASK_APP=api/
```
```
flask shell

db.create_all()
```
**4. Run the application to get started**
```
flask run
``` 
or 
```
python run.py
``` 

Once the application is running, you can start testing it with the following admin credentials
- **username: superadmin**
- **password: password**

- Login as an admin to get a JWT token. Once you add the token to authorization header to can go ahead and create a new user or student.
- You can also view students already added in the system. All other routes can b tested once you are logged in as an admin
- If you need to perform as task as a student (eg. enroll for a course) you'll need to login as a student to do that.
- You can go ahead and create a new student to get the student ID and password.

You can visit the app [here](https://students-management-system-api.herokuapp.com/) as well to test the already hosted application with the same credentials provided above.

## ENDPOINTS
### Auth Enpoints

HTTP METHOD|ENDPOINT|ACTION|RETURN VALUE|PARAMETER|AUTHORIZATION
---|---|---|---|---|---
POST|/auth/user/signup|Create a new User|User|None|Administrator
POST|/auth/user/login|Generate Access Token for User|Access Token & Refresh Token|None|Administrator, User
POST|/auth/student/register|Register a new student|Student ID & password|None|Administrator, User
POST|/auth/student/login|Generate a Access token for student|Access Token & Refresh Token|None|Student
POST|/auth/resetpassword/{email}|Reset a forgotten password|Username and new password; Student ID and new password|User email or Student email|User, Student
PUT|/auth/changepassword|Change a password|Success message|None|User, Student

___
### Student Enpoints

HTTP METHOD|ENDPOINT|ACTION|RETURN VALUE|PARAMETER|AUTHORIZATION
---|---|---|---|---|---
GET|/student|Retrieve or get all students|Students|None|Adminstrator, User
POST|/student/enrollment|Enroll for a course|Student with courses enrolled for|None|Student
GET|/student/enrollment/{student_id}|Retrieve or get all courses of a particular student|Course|Student email|Adminstrator, User, Student
PUT|/student/enrollment/{student_id}/{course_code}|Enter or update a student's score for a course|Enrollment|Student ID and course code|Adminstrator, User
DELETE|/student/enrollment/{student_id}/{course_code}|Delete or unregister course enrollment for a student|Success Message|Student ID and course code|Adminstrator
GET|/student/enrollment/grade/{student_id}|Retrieve or get grades of all courses for a particular student|Enrollment|Student ID|Adminstrator, User, Student
GET|/student/enrollment/gpa|Retrieve or get the GPA of all students|GPA|None|Adminstrator, User
GET|/student/enrollment/gpa/{student_id}|Retrive or get the GPA of a particular student|GPA|Student ID|Adminstrator, User, Student
GET|/student/{student_id}|Retrive or get a student by ID|Student|Student ID|Adminstrator, User, Student
PUT|/student/{student_id}|Update a student's information|Student|Student ID|Adminstrator, User
DELETE|/student/{student_id}|Delete a student from the database|Success Message|Student ID|Adminstrator

___
### Course Enpoints

HTTP METHOD|ENDPOINT|ACTION|RETURN VALUE|PARAMETER|AUTHORIZATION
---|---|---|---|---|---
GET|/course|Retrieve or get all courses|Courses|None|Adminstrator, User, Student
POST|/course|Add a new course|Course|None|Adminstrator, User
GET|/course/{course_code}|Retrieve or get a course by course code|Course|Course code|Adminstrator, User
PUT|/course/{course_code}|Update or edit a course|Course|Course code|Adminstrator, User
DELETE|/course/{course_code}|Delete a course from database|Success message|Course code|Adminstrator
GET|/course/enrollment/{course_code}|Get or retrieve all students registered in a particular course|Students|Course code|Adminstrator, User
GET|/course/enrollment/grade/{course_code}|Get or retrieve grades of all students for a particular course|Enrollments|Course code|Adminstrator, User


___
> **NOTE:** I am returning the student ID and password for testing purposes. Ideally, the student ID and password will be sent directly to the student's email


## Languages and Tools Used
<img align="center" src="https://user-images.githubusercontent.com/53656050/192115605-aebc5f03-6e81-4537-985a-6bdd7c95f83a.png" style="width:70px; height:70px" alt="python" /> <img align="center" src="https://user-images.githubusercontent.com/53656050/192115449-02c26cf0-a2aa-4b45-a5ef-0243ac26f200.png" style="width:70px; height:70px" alt="flask" /> <img align="center" src="https://user-images.githubusercontent.com/53656050/225774036-d7db456d-49be-4b72-9dbb-97f36f005a2a.png" style="width:70px; height:70px" alt="sqlite" /><img align="center" src="https://user-images.githubusercontent.com/53656050/225773399-08e79528-2c33-4a52-962b-7bb54d0bea03.png" style="width:70px; height:70px" alt="postgresql" />

- Python
- Flask
- SQLAlchemy
- SQLite
- Flask Smoorest
- PostgreSQL

## Screenshots

### *Swagger UI for API*

![image](https://user-images.githubusercontent.com/53656050/226096416-3c51f81e-e33c-4b81-90ac-a70cfdf45fd8.png)

### *Endpoints for Authentication*

![image](https://user-images.githubusercontent.com/53656050/226096896-6cfbe106-c0d5-47c4-8036-1734a2643cb6.png)

### *Endpoints for Student*

![image](https://user-images.githubusercontent.com/53656050/226096791-43e5f608-a59b-41ef-a721-6f2549bb7913.png)

### *Endpoints for Course*

![image](https://user-images.githubusercontent.com/53656050/226096635-6cc1c89f-7c07-4437-9f95-933e6b552d81.png)

### *API Schemas*

![image](https://user-images.githubusercontent.com/53656050/226096766-73e5bbbd-1bc8-41e2-b478-9afe2c747e0d.png)


## Acknowledgements
- [AltSchool Africa](https://altschoolafrica.com/schools/engineering)

- [Caleb Emelike](https://github.com/CalebEmelike)
