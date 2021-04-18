import archinstall, requests, os

# Profile for installing on Mac computer that have the T2 security chip
# By Redecorating
#
# Includes:
#	patched 'linux-mbp' kernel
#	dkms 'apple-bce' driver (keyboard, trackpad, audio) TODO: add apple-bce to mkinitpcio
#	dkms 'apple-ibridge' driver (touchbar)
#	TODO audio configuration files
#	t2linux repo for updates to kernel
#	TODO wifi
#	nvram read only because t2 likes to panic

# https://wiki.t2linux.org/distributions/arch/installation/ 


def _prep_function(*args, **kwargs):
	"""
	Magic function called by the importing installer
	before continuing any further. It also avoids executing any
	other code in this stage. So it's a safe way to ask the user
	for more input before any other installer steps start.
	"""
	return True

if __name__ == 'apple-t2':

	## t2linux repo

	print('Adding t2linux repo to /etc/pacman.conf in install')
	with open(f'{installation.mountpoint}/etc/pacman.conf', 'a') as pacmanconf:
		pacmanconf.write("\n[mbp]\n")
		pacmanconf.write("Server = https://dl.t2linux.org/archlinux/$repo/$arch\n")

	# add package signing key

	t2linuxKey = requests.get("https://dl.t2linux.org/archlinux/key.asc")
	open(f"{installation.mountpoint}/t2key.asc", 'wb').write(t2linuxKey.content)
	installation.arch_chroot("pacman-key --add /t2key.asc")
	installation.arch_chroot("pacman-key --lsign 7F9B8FC29F78B339") # aunali1's key
	os.remove(f"{installation.mountpoint}/t2key.asc")

	## Kernel and apple-bce

	print('Installing patched kernel and apple-bce')
	installation.arch_chroot("pacman -S --noconfirm linux-mbp git linux-mbp-headers apple-bce-dkms-git")
	with open(f"{installation.mountpoint}/etc/modules-load.d/t2.conf", 'a') as modulesConf:
		modulesConf.write("apple-bce\n")

	## add kernel to systemd-boot as default

	print("Adding linux-mbp to systemd-boot menu as default")
	normalBootFileName = os.listdir(f"{installation.mountpoint}/boot/loader/entries")[0]
	normalBoot = open(f"{installation.mountpoint}/boot/loader/entries/{normalBootFileName}", 'r').readlines()
	bootOptions = normalBoot[5] #get line with uuid
	bootOptions = bootOptions[:-1] + " pcie_ports=compat intel_iommu=on\n" # take off \n and add arguments

	with open(f"{installation.mountpoint}/boot/loader/entries/linux-mbp.conf", 'w') as entry:
		entry.write(f"# Created by: archinstall's apple-t2 module\n")
		entry.write(f'title Arch Linux with linux-mbp\n')
		entry.write(f'linux /vmlinuz-linux-mbp\n')
		entry.write(f'initrd /initramfs-linux-mbp.img\n')
		entry.write(bootOptions)
	
	with open(f"{installation.mountpoint}/boot/loader/entries/linux-mbp-fallback.conf", 'w') as entry:
		entry.write(f"# Created by: archinstall's apple-t2 module\n")
		entry.write(f'title Arch Linux with linux-mbp and fallback initramfs\n')
		entry.write(f'linux /vmlinuz-linux-mbp\n')
		entry.write(f'initrd /initramfs-linux-mbp-fallback.img\n')
		entry.write(bootOptions)

	with open(f"{installation.mountpoint}/boot/loader/loader.conf", 'a') as loaderConf:
		loaderConf.write("\ndefault  linux-mbp.conf\n")
		loaderConf.write("timeout  1\n")


	## apple-ibridge (touchbar)
	
	model = open(f'/sys/devices/virtual/dmi/id/product_name', 'r').read()
	if "MacBookPro" in model:
		# TODO: make this a package
		print("Installing apple-ibridge (Touchbar driver).")
		installation.arch_chroot("git clone https://github.com/t2linux/apple-ib-drv /usr/src/apple-ibridge-0.1")
		installation.arch_chroot("sh -c 'dkms install -m apple-ibridge -v 0.1 -k $(pacman -Q linux-mbp|cut -d\\  -f2)-mbp'")

		with open(f"{installation.mountpoint}/etc/modules-load.d/t2.conf", 'a') as modulesConf:
			modulesConf.write("apple-ib-tb\n")
			modulesConf.write("apple-ib-als\n")

		with open(f"{installation.mountpoint}/lib/systemd/system-sleep/rmmod.sh", 'w') as rmmodScript:
			rmmodScript.write('#!/bin/sh\n')
			rmmodScript.write('if [ "${1}" == "pre" ];\n')
			rmmodScript.write('then rmmod apple_ib_tb\n')
			rmmodScript.write('elif [ "${1}" == "post" ];\n')
			rmmodScript.write('then modprobe apple_ib_tb\n')
			rmmodScript.write('fi\n')
		os.chmod(f"{installation.mountpoint}/lib/systemd/system-sleep/rmmod.sh", 755)

	
	# TODO: audio conf
	if model == "MacBookPro16,1" or model == "MacBookPro16,4":
		print("You'll need the alternate audio config files,", end=' ')
	else:
		print("You'll need the normal audio config files,", end=' ')
	print("once you've booted into your install, check the t2linux wiki for instructions on how to get them, as this script doesn't yet install them.")
	
	# TODO: wifi
	# loaded firmware for current chip should be copied to the install with:
	#	cp -n /lib/firmware/$(journalctl -b --grep=brcmf_fw_alloc_request|tail -n1|rev|cut -d\  -f4|rev)* {installation.mountpoint}/lib/firmware/brcm/
	# this needs need to check that we aren't overwriteing firmware, as in
	# the future this will be all automatic and we don't want to break that
	# then. `-n` might do this, `-u` might be good. also need to check that
	# wifi is working. would be good to also be able to fetch firmware from
	# https://packages.aunali1.com/apple/wifi-fw/18G2022/ if ethernet is being
	# used

	print("Wifi is not yet set up by this script.")

	# nvram ro

	print('Setting nvram to remount at boot as readonly, as writing to it panics the t2 chip')
	with open(f"{installation.mountpoint}/etc/fstab", 'a') as fstab:
		fstab.write("\nefivarfs /sys/firmware/efi/efivars efivarfs ro,remount 0 0\n")
