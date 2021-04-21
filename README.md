# archinstall-mbp

A drop in profile for python-archinstall, that installs stuff for t2 macs
right now it's a profile so if you use it, you won't be able to select the other profiles (desktop enviroments)

## Usage

```shell
curl https://raw.githubusercontent.com/Redecorating/archinstall-mbp/testing/apple-t2.py > /lib/python3.9/site-packages/archinstall/profiles/apple-t2.py
archinstall
```

At the profiles section, you **need** to select the "apple-t2" profile. Selecting multiple profiles doesn't work.

## Post install checklist

-	https://wiki.t2linux.org/guides/wifi/
	your firmware files will be in /usr/local/src/t2linux if you selected download

Includes:
-	patched 'linux-mbp' kernel
-	dkms 'apple-bce' driver (keyboard, trackpad, audio) 
-	dkms 'apple-ibridge' driver (touchbar)
-	audio configuration files
-	t2linux repo for updates to kernel
-	wifi firmware install (no 15,4, 16,X)
-	nvram remount as read only because t2 likes to panic
-	rmmod suspend fix
-	makes linux-mbp kernel the default kernel to boot with

TODO:
-	add submenu for selecting other profiles

