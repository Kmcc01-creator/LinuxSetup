sudo apt install tlp tlp-rdw smartmontools
sudo systemctl enable --now tlp

sudo systemctl stop bluetooth
sudo systemctl disable bluetooth
