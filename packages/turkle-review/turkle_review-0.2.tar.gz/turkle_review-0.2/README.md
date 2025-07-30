# Turkle Review
Adds the ability to review completed task assignments in the admin UI.

This turkle plugin adds a button to the Batch listing page to view completed results.
It displays the username, input from the CSV, and the answers from the form.
It does its best to guess which columns have json and renders that as a tree.

## Install
Install the Python package using pip:
```
pip install turkle-review
```
Then add this as an app in local_settings.py:
```
INSTALLED_APPS.append('turkle_review')
```
Your IDE will complain about this line but it works.

Finally, you will need to restart the webserver.