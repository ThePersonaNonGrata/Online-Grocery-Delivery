README3.txt — Integration Testing

Purpose:
  This folder contains integration tests that verify an end-to-end flow:
    - add items / change quantities
    - checkout creates an order
    - track order progresses through delivery statuses

How to run (no server needed):
  1) Open a terminal in this folder (3_integration_testing)
  2) Run:
       python -m unittest -v

Expected output:
  Tests should pass with an OK message.

Notes:
  These are simulation-based integration tests designed to be easy to run for grading.
