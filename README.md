# archinstall-mbp

A drop in profile for [python-archinstall](https://github.com/archlinux/archinstall), that installs stuff for t2 macs
right now it's a profile so if you use it, you won't be able to select the other profiles (desktop enviroments)

## Usage
1. Connect to internet
2. Partition disk if you need (for archinstall, if you want to have it on your internal ssd, make a 512mb boot partition and put the rest as the root partition. You don't need to do mkfs.foo, archinstall does it).
3. Run this:
```shell
wget https://raw.githubusercontent.com/Redecorating/archinstall-mbp/testing/apple-t2.py
sh apple-t2.py
archinstall
```


At the profiles section, you **need** to select the "apple-t2" profile. Selecting multiple profiles doesn't work.

Includes:
- installes archinstall to the live session if it's missing (as the latest mbp iso was made before archinstall was a thing)
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

