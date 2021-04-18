# archinstall-mbp

A drop in profile for python-archinstall, that installs stuff for t2 macs
right now it's a profile so if you use it, you won't be able to select the other profiles (desktop enviroments)

## Usage

```shell
curl -L https://bit.ly/3amlr9v > /usr/lib/python3.9/site-packages/archinstall/profiles/apple-t2.py
archinstall
```
If you don't want the shortened link, use `curl https://raw.githubusercontent.com/Redecorating/archinstall-mbp/main/apple-t2.py > /usr/lib/python3.9/site-packages/archinstall/profiles/apple-t2.py`

At the profiles section, you **need** to select the "apple-t2" profile. Selecting multiple profiles doesn't work.

## Post install checklist

-	https://wiki.t2linux.org/guides/wifi/
-	https://wiki.t2linux.org/guides/audio-config/
-	apple-ibridge if you have touchbar:
	```shell
	sudo git clone https://github.com/t2linux/apple-ib-drv /usr/src/apple-ibridge-0.1
	sudo dkms install -m apple-ibridge -v 0.1
	sudo modprobe apple-ib-tb
	sudo sh -c 'echo apple-ib-tb >> /etc/modules-load.d/t2.conf'
	sudo sh -c 'curl https://raw.githubusercontent.com/marcosfad/mbp-ubuntu/master/files/suspend/rmmod_tb.sh > /lib/systemd/system-sleep/rmmod_tb.sh'
	sudo chmod +x /lib/systemd/system-sleep/rmmod_tb.sh
	```

Includes:
-	patched 'linux-mbp' kernel
-	dkms 'apple-bce' driver (keyboard, trackpad, audio) 
-	t2linux repo for updates to kernel
-	nvram remount as read only because t2 likes to panic
-	rmmod suspend fix
-	makes linux-mbp kernel the default

TODO:
-	wifi
-	audio configuration files
-	add `apple_bce hid_apple usbhid` to mkinitpcio modules, for keybaord @ initramfs stage
-	dkms 'apple-ibridge' driver (touchbar), it hangs when installing the module
-	add submenu for selecting other profiles

