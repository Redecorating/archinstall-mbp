# archinstall-mbp

A drop in profile for python-archinstall, that installs stuff for t2 macs
right now it's a profile so if you use it, you won't be able to select the other profiles (desktop enviroments)

## Usage

```shell
pacman -S archinstall curl
curl https://raw.githubusercontent.com/Redecorating/archinstall-mbp/main/apple-t2.py > /usr/lib/python3.9/site-packages/archinstall/profiles/apple-t2.py
archinstall
```
At the profiles section, you **need** to select the "apple-t2" profile. Seletcing multiple profiles doesn't work

Includes:
-	patched 'linux-mbp' kernel
-	dkms 'apple-bce' driver (keyboard, trackpad, audio) 
-	dkms 'apple-ibridge' driver (touchbar)
-	t2linux repo for updates to kernel
-	nvram remount as read only because t2 likes to panic
-	rmmod suspend fix
-	makes linux-mbp kernel the default

TODO:
-	wifi
-	audio configuration files
-	add shortened link because that one is long
-	add `apple_bce hid_apple usbhid` to mkinitpcio modules, for keybaord @ initramfs stage

