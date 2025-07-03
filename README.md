# Site Block Checker

A Python script to check if known gaming websites are accessible from a network (like a school firewall), with multithreaded scanning, user-agent rotation, and detailed output.

## Features
- Reads list of sites and user agents from CSV and TXT files
- Sends HTTP GET requests with random user agents
- Multithreaded requests for faster scanning
- Outputs detailed and summary CSV reports with timestamps
- Colour-coded terminal output

## Installation
Requires Python 3.7+ and the `requests` library.
