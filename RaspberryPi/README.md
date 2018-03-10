# Setting up a new Pi

Prerequisite: [AWS CLI](https://github.com/aws/aws-cli) Installed and configured (use `aws configure` once installed)

### Create a new iko unit / 'thing'
* Duplicate the src folder and rename it to iko. **Don't make unit specific changes to src. src is the main source code for a generic unit**
* cd into the new iko folder in terminal
* Create a new 'thing' on aws: `aws iot create-thing --thing-name iko<id>` (replace `<id>` with the id of the new thing)
* Generate new keys and certificates `aws iot create-keys-and-certificate --set-as-active --certificate-pem-outfile cert.pem --public-key-outfile publicKey.pem --private-key-outfile privkey.pem`
* Copy the certificate arn printed in your console, including the quotes
* Attach policy to certificate: `aws iot attach-principal-policy --principal <certificate-arn> --policy-name PubSubToAnyTopic` (replace `<certificate-arn>` with the arn you copied)
* Attach certificate to thing: `aws iot attach-thing-principal --thing-name iko<id> --principal <certificate-arn>` (replace `<certificate-arn>` and `<id>`)
* In automatino_oo.py set thingName to iko<id>
* Add whatever wifi networks you need to wpa_supplicant.conf

### Set up Raspbian OS
* Download [Raspbian Lite](https://www.raspberrypi.org/downloads/raspbian/) and load it onto the SD card using [Etcher](https://etcher.io)
* Copy the iko(src) folder into the /home/pi directory of the SD card if possible (use Linux). If not you can do the same through SSH further down in this README
* Optional: Copy the wpa_supplicant.conf file into the boot directory of the SD card
* Optional: Copy the (empty) ssh file into the boot directory of the SD card

# On Pi
* Connect keyboard, power and display to pi 
* Change password through `sudo raspi-config` (set password to heinousherbs) 
* Enable and start SSH: `sudo systemctl enable ssh` followed by `sudo systemctl start ssh`

### Setup wifi (only needed if wpa_supplicant not copied into boot earlier)
  * Open config file: `sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`
  * Add network info to the end of the file. Note: keyboard may be initially set to "gb" so instead of double quotes you get an @. To get double quotes type shift + 2
    ```
    network={
        ssid="your-network-ssid-name"
        psk="your-network-password"
    }
    ```
    * Exit and `sudo reboot`

### Transfer iko folder
  * Get ip address: on pi type  `ifconfig` or `hostname -I`. Alternatively use [adafruit pi finder](https://learn.adafruit.com/the-adafruit-raspberry-pi-finder/overview)
  * Transfer the iko(src) folder (if not done earlier after raspbian setup) to /home/pi directory through terminal using [scp](https://www.raspberrypi.org/documentation/remote-access/ssh/scp.md) with the `-r` flag to recursively copy an entire folder
  example terminal command: `scp -r /Users/Andrea/desktop/src pi@192.168.0.110:/home/pi` 
  Note: Sometimes an error will appear "remote host notification has changed" In this case type `ssh-keygen -R 192.168.1.233` into terminal
  * ssh with pi: type `ssh pi@<IP>`, replace <IP> with real IP address, to exit type `exit`
  * Add default_networks.txt from iko(src) folder to wpa_supplicant folder
  command: `sudo cp /home/pi/src/default_networks.txt /etc/wpa_supplicant` 

### Install libraries
* The install requires a yes input so for safety it is better to not SSH
* Make install.sh executable: `chmod +x /home/pi/iko/install.sh`
* type `cd /etc/wpa_supplicant`
* Run install.sh `/home/pi/iko/install.sh`

### Boot launch
* Open rc.local: `sudo nano /etc/rc.local`
* In the line before exit 0, write: `cd /home/pi/iko && python /home/pi/iko/automatino_oo.py 1 0 &`
