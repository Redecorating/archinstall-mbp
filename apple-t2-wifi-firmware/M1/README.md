This page assumes you used the archinstall-mbp profile. The build process for the firmware package also expects to be run on the computer it's making the package for. Also be aware that firmware taken form BigSur is known to work but firmware from Catalina might not (so update).

# Get Firmware
1.	In macOS, get the files listed in `ioreg -l | grep RequestedFiles` from `/usr/share/firmware/wifi`, and put them somewhere you can access from Linux.
2.	In Linux, run `sudo chown -R $USER:$USER /usr/local/src/t2linux/` 
2.	Move the files you got from macOS to `/usr/local/src/t2linux/apple-t2-wifi-firmware/M1/` (so transfer them to Linux with a USB or your EFI partition)
3.	In that folder, run `makepkg -i`.

# Compile Kernel

1.	`cd /usr/local/src/t2linux/mbp-16.1-linux-wifi`
2.	Build and instll the kernel (takes a few hours) with `makepkg -ei`.

# Add Kernel to Systemd-Boot

1.	Open `/boot/loader/loader.conf` with a text editor
2.	Remove the `#` before `default mbp-16.1-linux-wifi` and put a `#` before `default linux-mbp`
3.	Reboot
