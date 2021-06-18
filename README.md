# Paper Review App

This app is used to extract relevant information from papers to answer research questions in the systematic literature review. 

In this application, there are two types of accounts: user and admin. The admin account can check/edit the database in the admin panel, while the user account can only answer questions for the corresponding paper in the literatrue review. More information about users can be found in the "Initialize the data" section. 

After login, the user accounts can see the list of papers they are assigned to. By clicking the title, the users will enter read-only mode to read the answers they input. To answer the questions for the papers, the users need to click the "Add Review" button. After submitting, the button will become "Edit Review" and they can edit their input. 

This app was developed to support the following paper:

Bin Lin, Nathan Cassee, Alexander Serebrenik, Gabriele Bavota, Nicole Novielli, Michele Lanza, *"Opinion Mining for Software Development: A Systematic Literature Review"*, 2021


## Setup

### Requirements

This application is developed with Python 3. To test the project, you can first create a virtual environment and then install the third party dependencies with the following commands in the root directory of the app:

```
$ python3 -m venv ./venv
$ source ./venv/bin/activate
(venv)$ pip3 install -r requirements.txt
```

Then you can set the ``FLASK_APP`` and ``FLASK_ENV`` environment variables to point to the application and enable the development mode:

```
(venv)$ export FLASK_APP=slr_label;
(venv)$ export FLASK_ENV=development
```

### Initialize the database

To initialize the database, you can run the following command:

```
(venv)$ flask init-db
```

The database is generated based on the models defined in two modules (``auth/models.py`` and ``slr/models.py``). 
The ``auth`` module is responsible for user management, while the ``slr`` module is responsible for the questions and answers proposed by users for the literature review.
After the initialization, the database have no records. Thus, you need to dump your data into the database located in ``instance/slr_label.sqlite``.

### Initialize the data

To initialize the data, you can run the following command:

```
(venv)$ flask insert-data
```

This command will execute the method ``def insert_db_data_command()`` in the file ``slr_label/__init__.py``. More specifically, it will run ``insert_users, insert_papers, insert_questions and insert_assignments``, which are all located in the file ``slr_label/init_data.py`` and will be explained in the following subsections. 

#### Initialize Users

This is implemented in the ``insert_users`` function in the file ``slr_label/init_data.py``. By default, it creates two roles: ``user`` and ``admin``. The users with the admin role have access to admin panel, whether they can modify the data in a graphical interface. The users with a user role instead can only answer the questions specified for the literature review. 

The default user account information can be changed in this function. All the users will go to their corresponding interface after login.  
They can also modify their initial passwords. The user accounts can be also added/modified/removed with an admin account. 

#### Initialize Papers

This is implemented in the ``insert_papers`` function in the file ``slr_label/init_data.py``. By default, it loads the csv file ``sample_data/papers.csv`` to the database. We have provided a sample data file for demonstration purposes. 

#### Initialize Questions

This is implemented in the ``insert_questions`` function in the file ``slr_label/init_data.py``. The questions to be answered by users can be added here. The number in the question tuple stands for the question type: 0 stands for a True/False question, while 1 stands for an open-ended question.

#### Initialize Assignments

This is implemented in the ``insert_assignments`` function in the file ``slr_label/init_data.py``. By default, it randomly assigns equal number of papers to each non-admin user. 

### Run the application locally

To run the application locally, you can execute the following command:

```
(venv)$ flask run
```

By default, the application will be run on the port 5000. You can visit the application on ``http://127.0.0.1:5000``. 

## Deployment

To simplify the deployment, we have dockerized the application. That is, on a server supporting Docker, you can deploy the application by simply running the following command on the root directory of the project:

```
docker-compose up -d
```

The default host port is 5051, which can be changed in the ``docker-compose.yml`` file.