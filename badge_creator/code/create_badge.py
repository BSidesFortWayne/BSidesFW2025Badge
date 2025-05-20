import argparse
import os
import time
import subprocess

# Create an ArgumentParser object
parser = argparse.ArgumentParser()

# Add command-line arguments for name, company, and title
parser.add_argument("--firstname", help="Your first name", default=" ")
parser.add_argument("--fullname", help="Your full name", default=" ")
parser.add_argument("--company", help="Your company", default=" ")
parser.add_argument("--status", help="Your conference status", default="Attendee")

# Parse the command-line arguments
args = parser.parse_args()

# Set other variables
local_path = "/home/user/Documents/Badger_2040/"
badge_logo = "/badges/BadgeLogo.jpg"
badge_file = local_path + "code/badge.txt"
badge_image = local_path + "images/BadgeLogo.jpg"
serial_port = "/dev/ttyACM0"


# Write the information to a file called badge.txt
with open(badge_file, "w") as f:
    f.write(f"{args.status}\n{args.firstname}\n{args.fullname}\n\n{args.company}\n\n{badge_logo}")

# Wait for the Badger 2040 board to be ready
time.sleep(2)

# Transfer the files to the Badger 2040 board
subprocess.run(['rshell', '-p', 
                  serial_port, 
                  'cp', 
                  badge_file, 
                  badge_image, 
                  '/badges'])
