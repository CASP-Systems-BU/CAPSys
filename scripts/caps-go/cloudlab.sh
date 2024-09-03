#!/bin/bash

sudo apt update
sudo apt install git python3-pip unzip p7zip-full -y
sudo pip3 install matplotlib

wget https://go.dev/dl/go1.22.2.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.22.2.linux-amd64.tar.gz

echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.profile

rm -rf go1.22.2.linux-amd64.tar.gz
