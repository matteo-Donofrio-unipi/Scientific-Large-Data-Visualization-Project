# This is a project realized for the Scientific & Large Data Visualization course, during my Master Degree in Pisa.

The aim of the project is to create a Dashboard allowing to visualize how electricity is produced (but not imported/exported) and consumed in the European Countries.
It is developed using the Flask Framework, involiving languages as: Python, JavaScript, HTML, CSS.

The running site can be found here: http://matteoallenita99.pythonanywhere.com/ 
The site is actually hosted on the PythonAnywhere.com web service hosting. 

The Following are the instructions for running the site locally or on the PythonAnywhere.com platform.


SETUP & INIT
-----------------------
$ mkdir myproject
$ cd myproject
$ python3 -m venv venv
$ pip install flask



EXECUTE ON LINUX
-----------------------

given a folder path like:

myproject/
	app_folder/ project folders & files 
	venv/ configuration files  

run:
myproject$ source venv/bin/activate (activate the virtual environment)
myproject$ export FLASK_APP=app_folder (associate the app_folder to the executable)
myproject$ export FLASK_ENV=development (set the environment as dev => each modification of the code will invoke a restart of the runnable)
myproject$ flask run (activate the local server on the link http://127.0.0.1:5000/ )




EXECUTE ON PYTHONANYWHERE
----------------------------
https://www.youtube.com/watch?v=75-oCKUx3oU&ab_channel=ArditSulce%27sPythonHow

NB:
- in the WSGI-file write -> "from mysite import app as application". Here "mysite" is the name of the Main folder containing the whole application files (py, html, css, ecc...)

- init.py is the file containing the initialization phase & index page where the whole site "starts" 






USEFUL LINKS
---------------------------
how to run plotly graphs on html page (graphs rendering)
https://towardsdatascience.com/web-visualization-with-plotly-and-flask-3660abf9c946



how to define and plot a cloropleth (geo map)
https://www.youtube.com/watch?v=aJmaw3QKMvk&ab_channel=IndianPythonista



