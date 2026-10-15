Using the development buildout
------------------------------

Create a virtualenv in the package::

    $ virtualenv --clear .

Install requirements with pip::

    $ ./bin/pip install -r requirements.txt

Run buildout::

    $ ./bin/buildout

Start Plone in foreground:

    $ ./bin/instance fg

Run the browser tests
---------------------

The browser tests use Robot Framework and Selenium. They open the site in a
real web browser. At this time, there is one browser test:
``src/bibliotheca/core/tests/robot/test_faceted_map.robot``.

Requirements:

- Run buildout first (see above).
- Install Google Chrome.
- Make sure that you have network access for the first run. Selenium
  downloads the correct ``chromedriver`` for your Chrome version.

Run the test::

    $ ROBOT_BROWSER=headlesschrome ./bin/test -t test_faceted_map.robot --all

What the command does:

1. It starts a test Plone site on a local web server.
2. It creates a ``map`` folder with the faceted map view, and three
   ``patrimoine`` items in this folder: two items with coordinates and one
   item without coordinates.
3. It opens the ``map`` folder in Chrome. You do not see the browser window.
4. It makes sure that the map shows two markers: one marker for each item
   with coordinates. This test prevents the BIBLI-100 bug (no markers on the
   faceted map) from occurring again.

The test takes approximately 15 seconds.

The parts of the command:

- ``ROBOT_BROWSER=headlesschrome`` sets the browser. The default browser is
  Firefox. Selenium does not accept Firefox when you install it as a snap
  package (the default on Ubuntu). To see the browser window, use
  ``ROBOT_BROWSER=chrome``.
- ``-t test_faceted_map.robot`` runs only this test.
- ``--all`` is necessary. Browser tests have test level 5. ``./bin/test``
  without ``--all`` does not run them. The CI does not run them.

The results are in ``parts/test/test_faceted_map/``. Open ``log.html`` to
see each step. If the test fails, this folder also contains a screenshot
and the HTML source of the page.
