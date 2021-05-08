# archinstall-mbp

A profile for [python-archinstall](https://github.com/archlinux/archinstall), that installs drivers and packages for t2 Macs.

## Usage
1. If you are not on a MacBookPro15,4 (13-inch, 2019, Two Thunderbolt 3 ports), in MacOS, run `ioreg -l | grep RequestedFiles`. Make sure you can refer to the output of this command while your Mac is booted into the Arch Install iso.
2. Use a T2 Mac specific ISO from [here](https://dl.t2linux.org/archlinux/iso/index.html).
3. Boot the install iso, and connect to internet.
4. Run this:
```shell
wget https://raw.githubusercontent.com/Redecorating/archinstall-mbp/testing/apple-t2.py
sh apple-t2.py
archinstall
```
5. Enable bluetooth with `systemctl enable bluetooth` if you want it.

At the profiles section, you **need** to select the "apple-t2" profile. The
apple-t2 profile will ask you if you want a second profile.

## What does it install?

Installes Archinstall to the live session if it's missing (as the latest
mbp iso was made before archinstall was included)

Patched 'linux-mbp' kernel

DKMS 'apple-bce' driver (keyboard, trackpad, audio) 

DKMS 'apple-ibridge' driver (touchbar)

Alsa card profile for the t2 audio device (including alternate ones for
16 inch MacBooks, which have 6 speakers)

t2linux repo for updates to kernel

Installs wifi firmware (Mojave, BigSur)

On MacBookPro16,X and MacBookAir9,1 models, downloads the source and patches
for using an alternate WiFi patch that was made for M1 Macs that works on
those models. This can be built and installed as described [here](#here).

NVRAM remount as read only because t2 likes to panic

Unload touchbar driver before suspend to fix suspend/resume

Makes linux-mbp kernel the default kernel to boot with

Submenu for selecting a second profile (i.e. a desktop environment)

Installs `iwd` and sets it as NetworkManager's WiFi backend

TODO:
-	install mbpfan?
-	configure apple-ib-tb and apple-bce options
-	hybrid graphics?
-	only show top level profiles as chainload options
-	make into a plugin when they are implemented into archinstall.

## here

### Compile and Install Kernel

1.	`sudo chown -R $USER:$USER /usr/local/src/t2linux/` 
2.	`cd /usr/local/src/t2linux/mbp-16.1-linux-wifi`
3.	`MAKEFLAGS=-j12 makepkg -ei` (Takes a few hours) Replace 12 with the number of threads your cpu has. You will need about 20GB of space to compile, but you can delete the "src" directory after you are done to get this space back.

### Add Kernel to Systemd-Boot

1.	Open `/boot/loader/loader.conf` with a text editor
2.	Remove the `#` before `default mbp-16.1-linux-wifi` and put a `#` before `default linux-mbp`
3.	Reboot

