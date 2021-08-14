# archinstall-mbp

A profile for [python-archinstall](https://github.com/archlinux/archinstall), that installs drivers and packages for T2 Macs.

Currently you must choose systemd-boot as your bootloader, grub will not work. See [#3](https://github.com/Redecorating/archinstall-mbp/issues/3)

## Usage
1. In MacOS, run `ioreg -l | grep RequestedFiles`. Make sure you can refer to the
   output of this command while your Mac is booted into the Arch Install ISO.
2. Use a T2 Mac specific ISO from [here](https://dl.t2linux.org/archlinux/iso/index.html).
3. Boot the install ISO, and connect to internet.
4. Run the code block below, but first, there are a few options in archinstall that you must select or it won't work:
   1. When prompted by archinstall, do NOT use grub as the bootloader, it isn't yet working with this script.
   2. When prompted by archinstall, select "apple-t2" as your profile. You will be able to select a second profile later.

   ```shell
   wget https://bit.ly/3amlr9v -O apple-t2.py
   sh apple-t2.py
   python -m archinstall
   ```
5. Enable Bluetooth with `systemctl enable bluetooth` if you want it.

## What does it install?

Installs Archinstall to the live session if it's missing (as the latest
MBP ISO was made before archinstall was included)

Patched 'linux-mbp' kernel

DKMS 'apple-bce' driver (keyboard, trackpad, audio) 

DKMS 'apple-ibridge' driver (touchbar)

ALSA card profile for the T2 audio device (including alternate ones for
16 inch MacBooks, which have 6 speakers)

t2linux repo for updates to kernel

Installs WiFi firmware, walks you through selection

On MacBookPro15,4/16,X and MacBookAir9,1 models, installs a different version
of the `brcmfmac` driver that was made for M1 Macs and works on those models.

NVRAM remount as read only because T2 likes to panic

Unload Touchbar driver before suspend to fix resume

Makes linux-mbp kernel the default kernel to boot with.

Installs `iwd` and sets it as NetworkManager's WiFi backend.

TODO:
- install mbpfan
- configure apple-ib-tb and apple-bce options
- hybrid graphics?
- only show top level profiles as chainload options
- make into a plugin when they are implemented into archinstall.
- get github ci to test it
