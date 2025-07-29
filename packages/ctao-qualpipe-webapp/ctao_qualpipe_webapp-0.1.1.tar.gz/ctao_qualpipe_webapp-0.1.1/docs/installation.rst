Installation
============

User Installation
-----------------

To run the application in the background, from the project folder ``qualpipe-webapp`` simply execute:

.. code-block:: bash

    make up

Then open your browser:

- Frontend: http://localhost/
- API: http://localhost/api/data

To stop everything, execute:

.. code-block:: bash

    make down

If you also want to automatically see the logs, you can run it via Docker Compose.

To run it the first time execute (later on you can remove the ``--build``):

.. code-block:: bash

    docker-compose up --build

To stop it you can soft-kill with :kbd:`CTRL-C` and shut down all the services executing ``make down``.

If you modify the ``config`` while the containers are running, or in case Docker caches wrong stuff, you can restart it by running:

.. code-block:: bash

    make restart

or

.. code-block:: bash

    docker-compose down -v --remove-orphans
    docker-compose up --build

Developer Setup
---------------

For developers, you can build containers that automatically watch file changes, avoiding the need to restart the containers every time. To do so, simply execute:

.. code-block:: bash

    make build-dev
    make up-dev

This will automatically output every log produced.


Makefile info
-------------

Description of all the ``Makefile`` functionalities:

+---------------------+-------------------------------------------------------------+
| Command             | What it does                                                |
+=====================+=============================================================+
| make build          | Build the Docker images                                     |
+---------------------+-------------------------------------------------------------+
| make up             | Build and start services (backend + frontend) in background |
+---------------------+-------------------------------------------------------------+
| make down           | Stop all services                                           |
+---------------------+-------------------------------------------------------------+
| make logs           | View combined logs (both frontend and backend)              |
+---------------------+-------------------------------------------------------------+
| make logs-backend   | View only backend logs                                      |
+---------------------+-------------------------------------------------------------+
| make logs-frontend  | View only frontend logs                                     |
+---------------------+-------------------------------------------------------------+
| make restart        | Restart the containers                                      |
+---------------------+-------------------------------------------------------------+
| make prune          | Clean up unused Docker containers/images                    |
+---------------------+-------------------------------------------------------------+
| make build-dev      | Build the Docker images (development)                       |
+---------------------+-------------------------------------------------------------+
| make up-dev         | Build and start services (backend + frontend) in background |
+---------------------+-------------------------------------------------------------+
