# profile that installs needed drivers for archlinux on Mac computers with the T2 chip.
# install archinstall if needed and also move this file into the profiles
# folder. exits before it gets to the python code.
""":"
if [ -e /bin/archinstall ]
then :
else pacman -Sy --noconfirm archinstall
ln -vs /lib/python3.9/site-packages/archinstall /lib/python3.8/site-packages/archinstall
fi
mount efivarfs /sys/firmware/efi/efivars/ -o ro,remount -t efivarfs
cp -v apple-t2.py /lib/python3.9/site-packages/archinstall/profiles/apple-t2.py
exit 0
"""
# Profile for installing on Mac computers that have the T2 security chip
# By Redecorating
#
# Installs:
#	* patched 'linux-mbp' kernel
#	* dkms 'apple-bce' driver (keyboard, trackpad, audio)
#	* dkms 'apple-ibridge' driver (touchbar)
#	* audio configuration files
#	* t2linux repo for updates to kernel
#	* installs wifi firmware for pre catalina models, and can download source
#	  for kernel with M1 wifi patches for 16,X models
#	* nvram read only because t2 likes to panic

# https://wiki.t2linux.org/distributions/arch/installation/ 

import archinstall, os

is_top_level_profile = True

def select_download_firmware():

	## Selection ##

	print("Please get the output of running")
	print()
	print("\t`ioreg -l | grep RequestedFiles`")
	print()
	print("in Terminal on macOS, and use it to answer the next few questions.")


	# TODO: Should be able to get this from the model

	chip_name = select(["C-4355__s-C1",
						"C-4364__s-B2",
						"C-4364__s-B3",
						"C-4377__s-B3"],
						"Which folder are the listed files in? ")

	chip = chip_dict[chip_name]

	island_name = select(chip, "Which one of island is in the filenames? ")

	island = island_dict[island_name]

	trxFile = (island_name.lower() + '.trx')
	clmbFile = (island_name.lower() + '.clmb')

	__m = select(["u__m", "m__m"],
				  "Which is in the name of the NVRAM file? ")

	txtList = filter(filter(island, ".txt"), __m)
	# get all version numbers
	txtVerList = []
	for i in txtList:
		ver = i[-7:-4]
		if ver not in txtVerList:
			txtVerList.append(ver)

	ver = select(txtVerList,
				 "Which version number is in the NVRAM file's name? ")


	txtFile = filter(txtList, ver)[0]

	firmwareFiles = {"FIRMWARE": (chip_name + "/" + trxFile),
					 "REGULATORY": (chip_name + "/" + clmbFile),
					 "NVRAM": (chip_name + "/" + txtFile)}

	# https://packages.aunali1.com/apple/wifi-fw/18G2022/C-4364__s-B3/ seems 
	# to have symlinks for it's .trx files. C-4364__s-B2 has files of the same
	# name so use them instead? This probably doesn't work.

	if 'C-4364__s-B3' in firmwareFiles["FIRMWARE"]:
		firmwareFiles["FIRMWARE"] = "C-4364__s-B2/" + trxFile
		# TODO: Rewrite this message
		print("The trx file needed is missing (probably because it's a symlink), so one from the other 4364 folder is being used. This may not work but it might.")

	return firmwareFiles

def checkWifiSupport(model):
	if "MacBookPro16," in model or "MacBookAir9,1" in model:
		return "M1"
	elif "MacBookPro15,4" in model:
		return "None"
	else: 
		return "Download"

def filter(List, filterText):
	filtered = []
	#print(filterText)
	for item in List:
		if filterText in item:
			filtered.append(item)
	return filtered

def select(List, Message):
	if len(List) == 1:
		return List[0]
	else:
		ret = ''
		while bool(ret) == False:
			try:
				ret = archinstall.generic_select(List, Message)
			except:
				pass
		return ret

def _prep_function(*args, **kwargs):

	apple_t2 = {}


	## Get Model ##

	# XXX revert before merge with main
	if os.system("lspci |grep 'Apple Inc. T2' > /dev/null") == 10: 
		model = open(f'/sys/devices/virtual/dmi/id/product_name', 'r').read()
	else:
		print("This computer does not have a t2 chip.")
		model = select(t2models,
					   "Which is the model identifier of the t2 Mac you intend to use? ")

	apple_t2["model"] = model

	## WiFi ##

	apple_t2['wifi'] = checkWifiSupport(model)

	if apple_t2['wifi'] == "Download":

		apple_t2['wifiFW'] = select_download_firmware()


	## Touchbar ##

	if "MacBookPro" in model:
		apple_t2['touchbar'] = True
	else:
		apple_t2['touchbar'] = False


	## Audio Conf ##

	# TODO: Do MacMinis and iMacs and MacPros need different config?
	if model == "MacBookPro16,1" or model == "MacBookPro16,4":
		apple_t2['altAudioConf'] = True
	else:
		apple_t2['altAudioConf'] = False

	## chainload profile select ##

	try:
		list_view = archinstall.list_profiles()
		profiles = [*list_view]
		profiles.remove("apple-t2")

		chainProfile = archinstall.generic_select(profiles,
							  "Pick a second profile (or leave blank): ")

		apple_t2['chainProfile'] = chainProfile

		if chainProfile != None:
			profile = archinstall.Profile(None, chainProfile)

			with profile.load_instructions(namespace=f"{chainProfile}.py") as imported:
				if hasattr(imported, '_prep_function'):
					ret = imported._prep_function()
					if ret == False:
						return False
				else:
					print(f"Deprecated (??): {chainProfile} profile has no _prep_function() anymore")
	except:
		print("Couldn't select second profile, probably because this is being run as a test")

	## repeat user's selections ##

	print("Your selected options for the apple-t2 profile:", end="\n\t")
	print(apple_t2)

	archinstall.storage["apple_t2"] = apple_t2

	return True

	"""
	Stored Vars:
	'wifi': Download/M1/None
	'wifiFW': {'FIRMWARE': 'C-4377__s-B3/formosa-X0.trx',
			   'REGULATORY': 'C-4377__s-B3/formosa-X0.clmb',
			   'NVRAM': 'C-4377__s-B3/P-formosa-ID_M-SPPR_V-m__m-2.1.txt'}
	'touchbar': True/False
	'altAudioConf': True/False
	'model': 'MacBookPro15,1'
	"""



if __name__ == 'apple-t2':

	apple_t2 = archinstall.storage["apple_t2"]

	## t2linux repo ##

	print('Adding t2linux repo to /etc/pacman.conf in install')
	with open(f'/mnt/etc/pacman.conf', 'a') as pacmanconf:
		pacmanconf.write("\n[mbp]\n")
		pacmanconf.write("Server = https://dl.t2linux.org/archlinux/$repo/$arch\n")

	# add package signing key #

	installation.arch_chroot("sh -c 'curl https://dl.t2linux.org/archlinux/key.asc > /t2key.asc'")
	installation.arch_chroot("pacman-key --add /t2key.asc")
	installation.arch_chroot("pacman-key --lsign 7F9B8FC29F78B339") # aunali1's key
	os.remove(f"/mnt/t2key.asc")

	## Kernel and apple-bce ##

	print('Installing patched kernel and apple-bce')

	# add modules to mkinitpcio before the mbp initramfs' are generated
	installation.arch_chroot("sed -i s/^MODULES=\(/MODULES=\(apple_bce\ hid_apple\ usbhid\ /gm /etc/mkinitcpio.conf")

	installation.arch_chroot("pacman -Syu --noconfirm linux-mbp git linux-mbp-headers apple-bce-dkms-git")
	with open(f"/mnt/etc/modules-load.d/t2.conf", 'a') as modulesConf:
		modulesConf.write("apple-bce\n")

	## add kernel to systemd-boot as default ##

	print("Adding linux-mbp to systemd-boot menu as default")

	try:
		# work around https://github.com/archlinux/archinstall/issues/322
		confFiles = []
		for file in os.listdir(f"/mnt/boot/loader/entries"):
			if "mbp" not in file:
				confFiles.append(file)
		normalBootFileName = sorted(confFiles)[-1]
		normalBoot = open(f"/mnt/boot/loader/entries/{normalBootFileName}", 'r').readlines()
		bootOptions = normalBoot[5] #get line with uuid
		bootOptions = bootOptions[:-1] + " pcie_ports=compat intel_iommu=on\n" # take off \n and add arguments

		kernels = ["linux-mbp"]

		with open(f"/mnt/boot/loader/loader.conf", 'a') as loaderConf:
			loaderConf.write("\ndefault  linux-mbp.conf\n")
			if apple_t2["wifi"] == "M1":
				kernels.append("mbp-16.1-linux-wifi")
				loderConf.write("#default mbp-16.1-linux-wifi.conf")
			loaderConf.write("timeout  1\n")

		for kernel in kernels:
			with open(f"/mnt/boot/loader/entries/{kernel}.conf", 'w') as entry:
				entry.write(f"# Created by: archinstall's apple-t2 module\n")
				entry.write(f'title Arch Linux with {kernel}\n')
				entry.write(f'linux /vmlinuz-{kernel}\n')
				entry.write(f'initrd /initramfs-{kernel}.img\n')
				entry.write(bootOptions)

			with open(f"/mnt/boot/loader/entries/{kernel}-fallback.conf", 'w') as entry:
				entry.write(f"# Created by: archinstall's apple-t2 module\n")
				entry.write(f'title Arch Linux with {kernel} and fallback initramfs\n')
				entry.write(f'linux /vmlinuz-{kernel}\n')
				entry.write(f'initrd /initramfs-{kernel}-fallback.img\n')
				entry.write(bootOptions)

	except:
		print("Failed to set linux-mbp as the default kernel.")

	### build packages ###

	def nobody(command):
		# gpg and git need a home directory
		installation.arch_chroot(f"sh -c \"HOME=/usr/local/src/t2linux runuser nobody -m -s /bin/sh -c \\\"{command}\\\"\"")

	try:
		installation.arch_chroot("mkdir /usr/local/src/t2linux")
		installation.arch_chroot("chown nobody:nobody /usr/local/src/t2linux") # makepkg doesn't run as root
		nobody('git clone -b testing https://github.com/Redecorating/archinstall-mbp /usr/local/src/t2linux')
	except:
		print("Failed to clone Redecorating/archinstall-mbp, the next few steps will most likely also fail.")

	## apple-ibridge (touchbar)
	if apple_t2["touchbar"] == True:
		try:
			print("Building apple-ibridge-dkms-git")
			nobody('cd /usr/local/src/t2linux/apple-ibridge-dkms-git && makepkg')
			print("Installing apple-ibridge-dkms-git")
			installation.arch_chroot("sh -c 'pacman -U --noconfirm /usr/local/src/t2linux/apple-ibridge-dkms-git/apple-ibridge-dkms-git-*-x86_64.pkg*'")
		except:
			print("An error occured when installing the touchbar driver.")

	## audio conf ##
	try:
		if apple_t2["altAudioConf"] == True:
			print("Installing alternate t2 alsa card profile files for 16 inch MacBookPro")
			nobody('cd /usr/local/src/t2linux/apple-t2-audio-config/alt && makepkg')
			installation.arch_chroot("sh -c 'pacman -U --noconfirm  /usr/local/src/t2linux/apple-t2-audio-config/alt/apple-t2-audio-config-alt-*-any.pkg*'")
		else:
			print("Installing t2 alsa card profile files")
			nobody('cd /usr/local/src/t2linux/apple-t2-audio-config/normal && makepkg')
			installation.arch_chroot("sh -c 'pacman -U --noconfirm /usr/local/src/t2linux/apple-t2-audio-config/normal/apple-t2-audio-config-*-any.pkg*'")
	except:
		print("An error occured when installing the alsa card profiles for t2 audio")

	## wifi ##

	if apple_t2["wifi"] == "Download":
		try:
			print("Configuring WiFi PKGBUILD to use the selected firmware")

			model = apple_t2["model"]

			for key in ["FIRMWARE", "REGULATORY", "NVRAM"]:
				link = apple_t2["wifiFW"][key]
				folder = '/usr/local/src/t2linux/apple-t2-wifi-firmware/normal'
				#installation.arch_chroot(f"sed -i 's#{key}#{link}#g' /usr/local/src/t2linux/apple-t2-wifi-firmware/normal/PKGBUILD")
				nobody(f"ln -sr {folder}/wifi-fw/{link} {folder}/{key}")
			installation.arch_chroot(f"sed -i 's#MODEL#{model}#g' {folder}/PKGBUILD")

			print("Making package")
			nobody('cd /usr/local/src/t2linux/apple-t2-wifi-firmware/normal && makepkg')

			print("Installing WiFi firmware package")
			installation.arch_chroot("sh -c 'pacman -U --noconfirm /usr/local/src/t2linux/apple-t2-wifi-firmware/apple-t2-wifi-*-any.pkg*'")
		except:
			print("An error occured when installing WiFi firmware.")
	elif apple_t2["wifi"] == "M1":
		try:
			print("Cloning patches from https://github.com/jamlam/mbp-16.1-linux-wifi")
			nobody('git clone https://github.com/jamlam/mbp-16.1-linux-wifi /usr/local/src/t2linux/mbp-16.1-linux-wifi')
			print("Installing kernel build dependencies")
			installation.arch_chroot("pacman -S --needed --noconfirm bc kmod libelf pahole cpio perl tar xz xmlto python-sphinx python-sphinx_rtd_theme graphviz imagemagick git")
			print("Downloading kernel source")
			nobody('gpg --recv-key 38DBBDC86092693E')
			nobody('cd /usr/local/src/t2linux/mbp-16.1-linux-wifi && makepkg -o')
			print("The custom kernel patches are ready in /usr/local/src/t2linux/mbp-16.1-linux-wifi for you to build later, by running `makepkg -ie` in `/usr/local/src/t2linux/mbp-16.1-linux-wifi` (this takes a few hours to compile). You will also need firmware from /usr/share/firmware in macOS (Read the WiFi guide at wiki.t2linux.org).")
		except:
			print("An error occured while preparing the kernel with M1 wifi patches.")
	else:
		print("Nothing is being done for WiFi.")

	# TODO: chown -r it to not nobody


	# nvram ro
	try:
		print('Setting nvram to remount at boot as readonly, as writing to it panics the t2 chip')
		with open(f"/mnt/etc/fstab", 'a') as fstab:
			fstab.write("\nefivarfs /sys/firmware/efi/efivars efivarfs ro,remount 0 0\n")
	except:
		print("Failed to set nvram to remount.")

	## chainloaded profile ##

	if apple_t2["chainProfile"] != None:
		installation.install_profile(apple_t2['chainProfile'])

### Lists ###

## Model List ##

t2models = ["MacBookPro16,3", "MacBookPro16,2", "MacBookPro16,1",
			"MacBookPro16,4", "MacBookPro15,4", "MacBookPro15,1",
			"MacBookPro15,3", "MacBookPro15,2", "MacBookAir9,1",
			"MacBookAir8,2", "MacBookAir8,1", "Macmini8,1",
			"MacPro7,1", "iMac20,1", "iMac20,2", "iMacPro1,1"]

## WIFI FIRMWARE FILES ##

## NVRAM ##

# These are the NVRAM files. Many are exactly the same, so only one of any
# identical ones have been included. The needed file can be determined by the
# chip name, i.e. "sid", the version number at the end, i.e. "2.5", and which
# of "u__m" and "m__m" is present.

# The .trx and .clmb files only need the island name, "-X3" etc ones are
# identical to the ones without "-X3", so island.trx and island.txcb can be
# used.

hawaii = [
			"P-hawaii-ID_M-YSBC_V-m__m-2.3.txt",
			"P-hawaii-ID_M-YSBC_V-m__m-2.5.txt",
			"P-hawaii-ID_M-YSBC_V-u__m-4.1.txt",
			"P-hawaii-ID_M-YSBC_V-u__m-4.3.txt"
		 ]

ekans =	[
			"P-ekans-ID_M-HRPN_V-m__m-5.1.txt",
			"P-ekans-ID_M-HRPN_V-m__m-6.1.txt",
			"P-ekans-ID_M-HRPN_V-m__m-6.3.txt",
			"P-ekans-ID_M-HRPN_V-m__m-7.1.txt",
			"P-ekans-ID_M-HRPN_V-m__m-7.5.txt",
			"P-ekans-ID_M-HRPN_V-m__m-7.7.txt",
			"P-ekans-ID_M-HRPN_V-u__m-1.1.txt",
			"P-ekans-ID_M-HRPN_V-u__m-6.1.txt",
			"P-ekans-ID_M-HRPN_V-u__m-7.5.txt"
		 ]

kahana = [
			"P-kahana-ID_M-HRPN_V-m__m-7.7.txt",
			"P-kahana-ID_M-HRPN_V-u__m-7.5.txt"
		 ]

kauai =	[
			"P-kauai-ID_M-HRPN_V-m__m-6.1.txt",
			"P-kauai-ID_M-HRPN_V-m__m-6.3.txt",
			"P-kauai-ID_M-HRPN_V-m__m-7.5.txt",
			"P-kauai-ID_M-HRPN_V-m__m-7.7.txt",
			"P-kauai-ID_M-HRPN_V-u__m-6.1.txt",
			"P-kauai-ID_M-HRPN_V-u__m-7.5.txt"
		 ]

lanai =	[
			"P-lanai-ID_M-HRPN_V-m__m-7.7.txt",
			"P-lanai-ID_M-HRPN_V-u__m-7.5.txt"
		]

maui = [
			"P-maui-ID_M-HRPN_V-m__m-7.7.txt",
			"P-maui-ID_M-HRPN_V-u__m-7.5.txt" ]

midway = [
			"P-midway-ID_M-HRPN_V-m__m-7.7.txt",
			"P-midway-ID_M-HRPN_V-u__m-7.5.txt"
		 ]

nihau =	[
			"P-nihau-ID_M-HRPN_V-m__m-7.7.txt",
			"P-nihau-ID_M-HRPN_V-u__m-7.5.txt"
		]

sid = [
			"P-sid-ID_M-HRPN_V-m__m-2.3.txt",
			"P-sid-ID_M-HRPN_V-m__m-5.1.txt",
			"P-sid-ID_M-HRPN_V-m__m-6.1.txt",
			"P-sid-ID_M-HRPN_V-m__m-6.3.txt",
			"P-sid-ID_M-HRPN_V-m__m-7.1.txt",
			"P-sid-ID_M-HRPN_V-m__m-7.5.txt",
			"P-sid-ID_M-HRPN_V-m__m-7.7.txt",
			"P-sid-ID_M-HRPN_V-u__m-1.1.txt",
			"P-sid-ID_M-HRPN_V-u__m-6.1.txt",
			"P-sid-ID_M-HRPN_V-u__m-7.5.txt"
	  ]

Kahana = [
			"P-kahana-ID_M-HRPN_V-m__m-7.9.txt",
			"P-kahana-ID_M-HRPN_V-u__m-7.7.txt"
		 ]

Sid = [
			"P-sid-ID_M-HRPN_V-m__m-7.9.txt",
			"P-sid-ID_M-HRPN_V-u__m-7.7.txt"
	  ]

formosa = [
			"P-formosa-ID_M-SPPR_V-m__m-2.0.txt",
			"P-formosa-ID_M-SPPR_V-u__m-2.0.txt"
		  ]

## Chips and islands ##

C_4355__s_C1 = [hawaii]
C_4355__s_C1_names = ["hawaii"]

C_4364__s_B2 = [ekans, kahana, kauai, lanai,
				maui, midway, nihau, sid]
C_4364__s_B2_names = ["ekans", "kahana", "kauai", "lanai",
					  "maui", "midway", "nihau", "sid"]

C_4364__s_B3 = [Kahana, Sid] # capitalisation intentional
C_4364__s_B3_names = ["Kahana", "Sid"]

C_4377__s_B3 = [formosa]
C_4377__s_B3_names = ["formosa"]

chips = [C_4355__s_C1, C_4364__s_B2, C_4364__s_B3, C_4377__s_B3]

chip_dict = {"C-4355__s-C1": C_4355__s_C1_names,
			 "C-4364__s-B2": C_4364__s_B2_names,
			 "C-4364__s-B3": C_4364__s_B3_names,
			 "C-4377__s-B3": C_4377__s_B3_names}

island_dict = {"hawaii": hawaii, "ekans": ekans,
			   "kahana": kahana, "kauai": kauai,
			   "lanai": lanai, "maui": maui,
			   "midway": midway, "nihau": nihau,
			   "sid": sid, "Kahana": Kahana,
			   "Sid": Sid, "formosa": formosa}

# vim: autoindent tabstop=4 shiftwidth=4 noexpandtab number
