##VS CODE
echo "code code/add-microsoft-repo boolean true" | sudo debconf-set-selections

sudo apt-get install wget gpg
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" |sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
rm -f packages.microsoft.gpg

sudo apt install apt-transport-https
sudo apt update
sudo apt install code # or code-insiders

##NPM
sudo apt install npm

##build system: bazel for cpp
npm install -g @bazel/bazelisk 

sudo apt install apt-transport-https curl gnupg -y
curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor >bazel-archive-keyring.gpg
sudo mv bazel-archive-keyring.gpg /usr/share/keyrings
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list

sudo apt update && sudo apt install bazel

sudo apt update && sudo apt full-upgrade

sudo apt install python3-pip
sudo apt install python3.12-venv

##Python build systems  ##Poetry, hatch, and/or meson - meson is multi-language support
sudo apt install pipx
python3 -m pip install meson
python3 -m pip install ninja

pipx install poetry

#$speechfire server
python3 -m venv speechfire
source speechfire/bin/activate  # On Windows: speechfire\Scripts\activate
pip install -r requirements-lock.txt # confirmed working
# or
#pip install -r requirements.txt # latest versions, may break
