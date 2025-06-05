sudo apt update && sudo apt upgrade -y

sudo apt install python3-pip python3-pil python3-pil.imagetk python3-tk pipx pyboard-rshell -y

wget -qO- https://astral.sh/uv/install.sh | sh

pipx install mpremote

sudo usermod -a -G dialout registration

echo 'python3 "/home/registration/Documents/badge_creator/code/badger_gui.py" --localpath "/home/registration/Documents/badge_creator/"' > "/home/registration/Desktop/run_badger_creator.sh"
