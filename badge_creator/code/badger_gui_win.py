import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
#import time
import subprocess
import argparse
import serial

# Create an ArgumentParser object
parser = argparse.ArgumentParser()

# Add command-line arguments for name, company, and title
parser.add_argument("--conference", help="Enter Conference Name", default="BSides Fort Wayne 2025")
parser.add_argument("--formimage", help="Enter location of form logo", default="images/BadgeLogo.jpg")
parser.add_argument("--localpath", help="Enter location of local files", default="/home/registration/Documents/Badger_2040/")

# Parse the command-line arguments
args = parser.parse_args()

# Set global variables
local_path = args.localpath
conference = args.conference
badge_logo = "/badges/BadgeLogo.jpg"
badge_creator_logo = local_path + "images/BSidesLogo.png"
badge_file = local_path + "code/badge.txt"
badge_image = local_path + args.formimage
serial_port = "/dev/ttyACM0"
status = ['Attendee', 'Sponsor', 'Speaker', 'Volunteer']

class BadgeForm:
    def __init__(self, master):
        self.master = master
        master.title("Badge Creator")
        master.attributes()

        # Add Event Title Label
        self.label_event = tk.Label(master, 
                                    text=conference, 
                                    font=("Ariel",25))
        self.label_event.pack()

        # Add form Title Label
        self.label_title = tk.Label(master, 
                                    text="Badge Creator", 
                                    font=("Ariel",25))
        self.label_title.pack()

        # Load and resize the image
        self.image = ImageTk.PhotoImage(Image.open(badge_creator_logo).resize((446,278)))

        # Create a label for the image
        self.image_label = tk.Label(master, 
                                    image=self.image)
        self.image_label.pack()

        # Create a container frame for the fields
        self.field_container = tk.Frame(master)
        self.field_container.pack(padx=10, 
                                  pady=10)

        # Create a frame for the labels
        self.label_container = tk.Frame(self.field_container)
        self.label_container.pack(side=tk.LEFT)

        # Add Name Label
        self.label_firstname = tk.Label(self.label_container, 
                                   text="First Name:", 
                                   font=("Ariel, 18"))
        self.label_firstname.grid(row=0, 
                             sticky='e')
        
        # Add Name Label
        self.label_lastname = tk.Label(self.label_container, 
                                   text="Last Name:", 
                                   font=("Ariel, 18"))
        self.label_lastname.grid(row=1, 
                             sticky='e')

        # Add Company Label
        self.label_company = tk.Label(self.label_container, 
                                      text="Company:", 
                                      font=("Ariel, 18"))
        self.label_company.grid(row=2, 
                                sticky='e')

        # Add Status Label
        self.label_status = tk.Label(self.label_container, 
                                     text="Status:", 
                                     font=("Ariel, 18"))
        self.label_status.grid(row=3, 
                               sticky='e')

        # Create a frame for the entry widgets
        self.entry_container = tk.Frame(self.field_container)
        self.entry_container.pack(side=tk.LEFT)

        # Add Entry for First Name
        self.entry_firstname = tk.Entry(self.entry_container, 
                                   bd = 5)
        self.entry_firstname.grid(row=0, 
                             column=1)
        
        # Add Entry for Full Name
        self.entry_lastname = tk.Entry(self.entry_container, 
                                   bd = 5)
        self.entry_lastname.grid(row=1, 
                             column=1)

        # Add Entry for Company
        self.entry_company = tk.Entry(self.entry_container, 
                                      bd = 5)
        self.entry_company.grid(row=2, 
                                column=1)

        # Add Dropdown for Status
        self.options = status
        self.status_var = tk.StringVar()
        self.status_var.set(self.options[0])
        self.status_dropdown = tk.OptionMenu(self.entry_container, 
                                             self.status_var, 
                                             *self.options)
        self.status_dropdown.config(font=("Ariel",16))
        self.status_dropdown.grid(row=3, 
                                  column=1, 
                                  sticky='ew')
        
        # Set font for the Status dropdown
        self.status_menu = root.nametowidget(self.status_dropdown.menuname)
        self.status_menu.config(font=("Ariel",18))

        self.submit_button = tk.Button(master, 
                                       text="Create Badge", 
                                       command=self.create_badge, 
                                       width=30, 
                                       height=5, 
                                       bd=5, 
                                       font=("Ariel",18))
        self.submit_button.pack(pady=10)

    # Function to reboot Badger 2040 using machine.reset()
    def reboot_badger(self):
        # Establish a connection to the Badger 2040 board
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

        # Send the machine.reset() command to reboot the Badger 2040
        ser.write(b'import machine\r\n')
        ser.write(b'machine.reset()\r\n')

        # Close the serial connection
        ser.close()

    def create_badge(self):
        # Get the user input
        firstname = self.entry_firstname.get().strip()
        lastname = self.entry_lastname.get().strip()
        company = self.entry_company.get().strip()
        status = self.status_var.get()

        # Write the information to a file called badge.txt
        with open(badge_file, "w") as f:
            f.write(f"{status}\n{firstname}\n{firstname} {lastname}\n\n{company}\n\n{badge_logo}")

        # Wait for the Badger 2040 board to be ready
        # time.sleep(2)

        # Transfer the files to the Badger 2040 board
        subprocess.run(['rshell', '--timing', '-p', 
                  serial_port, 
                  'cp', 
                  badge_file, 
                  badge_image, 
                  '/badges'])
        self.reboot_badger()

        # Show a message box to confirm the badge was created
        messagebox.showinfo("Badge Created", 
                            "Badge has been created.")

        # Clear the form
        self.entry_firstname.delete(0, tk.END)
        self.entry_lastname.delete(0, tk.END)
        self.entry_company.delete(0, tk.END)
        self.status_var.set(self.options[0])

root = tk.Tk()

# Center grid
root.grid_rowconfigure(0, 
                       weight=1)
root.grid_columnconfigure(0, 
                          weight=1)
root.grid_rowconfigure(1, 
                       weight=1)
root.grid_columnconfigure(1, 
                          weight=1)
root.grid_rowconfigure(2, 
                       weight=1)
root.grid_rowconfigure(3, 
                       weight=1)

my_gui = BadgeForm(root)

# Run form until closed
root.mainloop()
