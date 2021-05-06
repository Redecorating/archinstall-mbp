# archinstall-mbp

A profile for [python-archinstall](https://github.com/archlinux/archinstall), that installs drivers and packages for t2 Macs.

## Usage
1. If you are not on a MacBookPro15,4 (13-inch, 2019, Two Thunderbolt 3 ports), in MacOS, run `ioreg -l | grep RequestedFiles`. Make sure you can refer to the output of this command while your Mac is booted into the Arch Install iso.
2. If you are on a MacBookPro16,X or MacBookAir9,1 (2020 models and 16 inch models), you can (but you can do it later) do the first step [here](https://github.com/Redecorating/archinstall-mbp/blob/testing/apple-t2-wifi-firmware/M1/README.md).
3. Use a T2 Mac specific ISO from [here](https://dl.t2linux.org/archlinux/iso/index.html).
4. Boot the install iso, and connect to internet.
5. Run this:
```shell
wget https://bit.ly/3amlr9v -O apple-t2.py
sh apple-t2.py
archinstall
```

At the profiles section, you **need** to select the "apple-t2" profile. The apple-t2 profile will ask you if you want a second profile.

Includes:
-	installes archinstall to the live session if it's missing (as the latest mbp iso was made before archinstall was a thing)
-	patched 'linux-mbp' kernel
-	dkms 'apple-bce' driver (keyboard, trackpad, audio) 
-	dkms 'apple-ibridge' driver (touchbar)
-	t2 audio card profile (including alternate ones for 16 inch MacBooks, which have 6 speakers)
-	t2linux repo for updates to kernel
-	downloads and installs wifi firmware for models that came with macOS Mojave
-	on MacBookPro16,X and MacBookAir9,1 models, downloads the source and patches for using an alternate WiFi patch that was made for M1 Macs that works on those models. This can be built and installed as described [here](https://github.com/Redecorating/archinstall-mbp/blob/testing/apple-t2-wifi-firmware/M1/README.md).
-	nvram remount as read only because t2 likes to panic
-	unload touchbar driver before suspend to fix suspend/resume
-	makes linux-mbp kernel the default kernel to boot with
-	submenu for selecting a second profile (i.e. a desktop enviroment)

TODO:
-	install mbpfan?
-	configure apple-ib-tb and apple-bce options
-	hybrid graphics?

