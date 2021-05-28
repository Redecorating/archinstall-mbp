# archinstall-mbp

A profile for [python-archinstall](https://github.com/archlinux/archinstall), that installs drivers and packages for t2 Macs.

This branch just has pkgbuilds, the archinstall profile is on the [main branch](https://github.com/Redecorating/archinstall-mbp).

This branch has:

- DKMS 'apple-ibridge' driver (touchbar)

- Alsa card profile for the t2 audio device (including alternate ones for
16 inch MacBooks, which have 6 speakers)

- Installs WiFi firmware (Mojave, BigSur), but you need to select the firmware files by symlinking them:
  
  My output of ioreg:
  
  ```json
  "RequestedFiles" = ({
    "Firmware"="C-4364__s-B3/bali.trx",
    "TxCap"="C-4364__s-B3/bali-X3.txcb",
    "Regulatory"="C-4364__s-B3/bali-X3.clmb",
    "NVRAM"="C-4364__s-B3/P-bali-X3_M-HRPN_V-u__m-7.7.txt"
  })
  ```
  
  Symlinks I have to make:
  
  
  ```
  ln -s bigSurFW/C-4364__s-B3/bali.trx FIRMWARE
  ln -s bigSurFW/C-4364__s-B3/P-bali-X3_M-HRPN_V-u__m-7.7.txt NVRAM 
  ln -s bigSurFW/C-4364__s-B3/bali-X3.clmb REGULATORY 
  ```
  
  The `archinstall` profile will guide you through this. Use the `bigsurFW` if your computer came with MacOS Catalina.
