# archinstall-mbp

A profile for [python-archinstall](https://github.com/archlinux/archinstall), that installs drivers and packages for t2 Macs.

## Usage
1. If you are not on a MacBookPro15,4 (13-inch, 2019, Two Thunderbolt 3 ports), in MacOS, run `ioreg -l | grep RequestedFiles`. Make sure you can refer to this while your Mac is booted into the Arch Install iso.
2. Use a T2 Mac specific ISO from [here](https://dl.t2linux.org/archlinux/iso/index.html).
3. Boot the install iso, and connect to internet.
4. Run this:
```shell
wget https://raw.githubusercontent.com/Redecorating/archinstall-mbp/testing/apple-t2.py
sh apple-t2.py
archinstall
```

At the profiles section, you **need** to select the "apple-t2" profile. The apple-t2 profile will ask you if you want another one.

Includes:
-	installes archinstall to the live session if it's missing (as the latest mbp iso was made before archinstall was a thing)
-	patched 'linux-mbp' kernel
-	dkms 'apple-bce' driver (keyboard, trackpad, audio) 
-	dkms 'apple-ibridge' driver (touchbar)
-	audio configuration files (including alternate ones for 16 inch MacBooks, which have 6 speakers)
-	t2linux repo for updates to kernel
-	wifi firmware install (no 15,4, 16,X)
-	on MacBookPro16,X and MacBookAir9,1 models, downloads the source and patches for [a version of linux-mbp with wifi patches made for M1 macs](https://github.com/jamlam/mbp-16.1-linux-wifi). This can be compiled offline, but firmware files from macOS bigsur are required, and not installed automatically (Untested on Air9,1).
-	nvram remount as read only because t2 likes to panic
-	unload touchbar driver before suspend to fix suspend/resume
-	makes linux-mbp kernel the default kernel to boot with
-	submenu for selecting a second profile (i.e. a desktop enviroment)

TODO:
-	Fix kernel source verification for kernel with the M1 wifi patch
-	install mbpfan?
-	configure apple-ib-tb and apple-bce options
-	hybrid graphics?

