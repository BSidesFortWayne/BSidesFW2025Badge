# Steps to setup registrations stations

This assumes this is a dedicated machine installed for this purpose.  This guide does not go over how to create a bootable Ubuntu usb drive.  A couple things to keep in mind:

- Keep the passwords consistent for ease of those managing the registration area
- Keep machine names consistent, but different (i.e. reg1, reg2, etc.)

## Ubuntu OS Install

1. Place the Ubuntu bootable USB drive into the powered off computer.
2. Power On the machine and boot to the USB Drive.
3. Select Install Ubuntu
4. Follow the prompts keeping the following in mind:
   1. Use Minimal install.
   2. Use "registration" as the username and login name.
   3. The password can be what ever you want, just follow the tip from above.
   4. Select the option to login automatically
   5. The rest of the options are up to you based on your preference.
5. Once the install is completed, select reboot.
6. You will then be asked to remove the USB drive and then press Enter.
7. Skip connecting online accounts.
8. Skip enabling ubuntu pro.
9. Answer how you wish on sending info to improve ubuntu
10. Location services are not needed.
11. No extra apps needed.
12. It will likely ask if you want to install updates. Proceed with doing so and restart when finished.

## Configure OS

1. Open Settings and set preferences as needed.  I do the following:
    1. Appearance - Dark theme
    2. Privacy > Screen
        1. Blank Screen Delay - Never
        2. Automatic Screen lock - off
        3. Lock Screen on Suspend - off
2. Install required components and copy scripts to the machine. This can be done by running the reg_station_setup.sh script from the machine.  So, put that on a usb drive and get it copied onto the machine.
   1. Sometimes, the run_badger_creator.sh file on the Desktop will show a lock on it in File Explorer and be owned by the root user. This will cause it not to work.  To fix that, just create a copy of the file, delete the old one, and rename the copy to the original name.
   2. The same thing happens with the /Documents/Badger_2040_Badge_Creator folder also.  Do the same thing to fix it.  However, after copying it, you can't just move it to trash, you must go to the terminal and run ```sudo rm /home/registration/Documents/Badger_2040_Badge_Creator -r```
3. Need to make the run_badger_creator.sh file be able to run as an application.
   1. Right Click on the file and select Properties.
   2. On the Permissions tab, check the Execute box
   3. Close the Properties box
4. Add Run Badger Creator to Startup Applications
   1. Open Dash (the first icon in the side bar)
   2. Click on Startup Applications
   3. Click the Add button
   4. Type in "Run Badge Creator" in Name
   5. Click the Browse button
   6. Double-click Desktop
   7. Click run_badger_creator.sh
   8. Click the Open button
   9. Click the Add button
   10. Click the Close button
5. Reboot the machine

All the remains now is to test a badge.  If for some reason the badger_gui script didn't run on startup, run it manually from terminal to see if there are errors.
