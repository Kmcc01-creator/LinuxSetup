ssh-keygen -t ed25519 -C "175071455+Kmcc01-creator@users.noreply.github.com" ##check authent with ssh-keygen

## git config --global user.email "YOUR_EMAIL"
## git config --global user.email


eval "$(ssh-agent -s)" ##did it work? 

ssh-add ~/.ssh/id_ed25519 ##add from default ssh generated file the sshh key

cat ~/.ssh/id_ed25519.pub ##copy key to clipboard

ssh -T git@github.com  ##test if ssh working
