# ============================================================================
# FACETED MAP ROBOT TESTS (BIBLI-100)
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ ROBOT_BROWSER=headlesschrome bin/test -t test_faceted_map.robot --all
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run keywords  Open test browser  AND  Enable autologin as  Manager
Test Teardown  Run keywords
...  Run keyword if test failed  Capture page screenshot and log source
...  AND  Close all browsers


*** Variables ****************************************************************

${MARKERS}  css=#faceted-map-container .leaflet-marker-pane .awesome-marker


*** Test Cases ***************************************************************

Scenario: The faceted map shows a marker for each geolocated result
  Go to  ${PLONE_URL}/map
  Wait until page contains element  css=.faceted-map-item.geolocated
  Wait until keyword succeeds  10s  0.5s
  ...  Page should contain element  ${MARKERS}  limit=2
