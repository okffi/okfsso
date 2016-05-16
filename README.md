OKF SSO
=======

Simple Single Sign On service. Uses OAuth2 to authenticate and
provides a data exchange API to allow client apps to publish
information to each other.

Lightweight; operating the service needs some 30 to 40 megabytes of
memory and as such, should run on a Raspberry Pi. Self contained: Does
not need an Internet connection.

Install and Run
---------------

To get running, have Python installed and available on your shell. Then:

    > pip install -r requirements.txt
    > python manage.py migrate
    > python manage.py runserver

Instead of using runserver, you may opt for any WSGI server. Please
follow Django's or that WSGI server's documentation to do so. You may
also want to `python manage.py collectstatic` and point your webserver
to serve the newly created `staticfiles/` directory at `/static/`.

For production use, creating your own settings file that sets a custom
`SECRET_KEY` and disables `DEBUG` is highly recommended. Anything less
is hilariously insecure.

Maintenance
-----------

Use `python manage.py createsuperuser` to create an admin account and
point your browser to the /admin/ path on the running service.
