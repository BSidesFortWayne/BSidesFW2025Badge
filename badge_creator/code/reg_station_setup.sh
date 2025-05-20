sudo apt update && sudo apt upgrade -y

sudo apt install python3-pip python3-pil python3-pil.imagetk python3-tk git -y

pip3 install rshell

sudo usermod -a -G dialout registration

cd /home/registration/Documents

sudo git clone "https://github.com/commputethis/Badger_2040_Badge_Creator.git"

echo 'python3 "/home/registration/Documents/Badger_2040_Badge_Creator/code/badger_gui.py" --localpath "/home/registration/Documents/Badger_2040_Badge_Creator/"' > "/home/registration/Desktop/run_badger_creator.sh"
