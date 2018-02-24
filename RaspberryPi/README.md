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
* Download [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) and load it onto the SD card using [Etcher](https://etcher.io)
* Copy the iko folder into the /home/pi directory of the SD card if possible (use Linux)
* Copy the wpa_supplicant.conf file into the boot directory of the SD card
* Copy the (empty) ssh file into the boot directory of the SD card

# On Pi
* Enable ssh & change password through `sudo raspi-config` (set password to heinousherbs)
### Setup wifi (only needed if wpa_supplicant not copied into boot earlier)
  * Open config file: `sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`
  * Add network info to the end of the file:
    ```
    network={
        ssid="your-network-ssid-name"
        psk="your-network-password"
    }
    ```
  * Exit and `sudo reboot`
### Transfer iko folder
  * Get ip address through `ifconfig`
  * Transfer the iko folder through [scp](https://www.raspberrypi.org/documentation/remote-access/ssh/scp.md) (use the -r flag to copy a folder)
* Replace /etc/wpa_supplicant/wpa_supplicant.conf with default_networks.txt
### Install libraries
* Make install.sh executable: `chmod +x /home/pi/iko/install.sh`
* Run install.sh `/home/pi/iko/install.sh`
### Boot launch
* Open rc.local: `sudo nano /etc/rc.local`
* In the line before exit 0, write: `cd /home/pi/iko && python /home/pi/iko/automatino_oo.py 1 0 &`
