# profile that installs needed drivers for archlinux on Mac computers with the T2 chip.
# install archinstall if needed and also move this file into the profiles
# folder. exits before it gets to the python code.
""":"
if ! [ -e /bin/archinstall ]; then
	pacman -Sy --noconfirm archinstall
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
#	* installs wifi firmware
#	* installs kernel with M1 wifi patches for MBP16,1/2 and MBA9,1 models
#	* nvram read only because t2 likes to panic

# https://wiki.t2linux.org/distributions/arch/installation/

import archinstall, os

is_top_level_profile = True

def select_download_firmware(FW):

	## Selection ##

	print("Please get the output of running")
	print()
	print("\t`ioreg -l | grep RequestedFiles`")
	print()
	print("in Terminal on macOS, and use it to answer the next few questions.")

	# TODO: Should be able to get this from the model

	chip_name = select(FW["chips"],
						"Which folder are the listed files in? ")

	chip = FW[chip_name]

	island_name = select(chip, "Which island is in the filenames? ")

	island = FW[island_name]

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
				 "Which version number is in the name of the NVRAM file? ")


	txtFile = filter(txtList, ver)[0]

	firmwareFiles = {"FIRMWARE": (chip_name + "/" + trxFile),
					 "REGULATORY": (chip_name + "/" + clmbFile),
					 "NVRAM": (chip_name + "/" + txtFile),
					 "release": FW["release"]}

	# https://packages.aunali1.com/apple/wifi-fw/18G2022/C-4364__s-B3/ seems
	# to have symlinks for it's .trx files. C-4364__s-B2 has files of the same
	# name. They are present on bigSur.

	return firmwareFiles

def checkWifiSupport(model):
	if "MacBookPro15,4" == model or "MacBookPro16," in model or "MacBookAir9,1" == model:
		return "bigSur"
	else:
		return "mojave"

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
		ret = archinstall.generic_select(List, Message, allow_empty_input=False)
		return ret

def _prep_function(*args, **kwargs):

	apple_t2 = {}


	## Get Model ##

	if os.system("lspci |grep 'Apple Inc. T2' > /dev/null") == 0: 
		model = open(f'/sys/devices/virtual/dmi/id/product_name', 'r').read()
		model = model[:-1] #strip trailing \n
	else:
		print("This computer does not have a t2 chip.")
		model = select(t2models,
					   "Which is the model identifier of the t2 Mac you intend to use? ")

	apple_t2["model"] = model

	## WiFi ##

	apple_t2['wifi'] = checkWifiSupport(model)

	if apple_t2['wifi'] == "mojave":
		apple_t2['wifiFW'] = select_download_firmware(mojaveFW)
	elif apple_t2['wifi'] == "bigSur":
		apple_t2['wifiFW'] = select_download_firmware(bigSurFW)

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

	archinstall.arguments["apple_t2"] = apple_t2

	return True

	"""
	Stored Vars:
	'wifi': ""/"mojave"/"bigSur"
	'wifiFW': {'FIRMWARE': 'C-4377__s-B3/formosa-X0.trx',
			   'REGULATORY': 'C-4377__s-B3/formosa-X0.clmb',
			   'NVRAM': 'C-4377__s-B3/P-formosa-ID_M-SPPR_V-m__m-2.1.txt',
			   'release': 'mojaveFW'}
	'touchbar': True/False
	'altAudioConf': True/False
	'model': 'MacBookPro15,1'
	"""



if __name__ == 'apple-t2':

	apple_t2 = archinstall.arguments["apple_t2"]

	installation = archinstall.storage['installation_session']

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

	installation.arch_chroot("pacman -Syu --noconfirm linux-mbp git linux-mbp-headers apple-bce-dkms-git iwd unzip")

	## add kernel to systemd-boot as default ##

	print("Adding linux-mbp to systemd-boot menu as default")

	kernel = "linux-mbp"

	folder = "/boot/loader/entries"
	installation.arch_chroot(f"sh -c 'cp {folder}/????-??-??_??-??-??.conf {folder}/{kernel}.conf'")
	installation.arch_chroot(f"sed -i -e s/-linux/-{kernel}/g -e s/options/options\ pcie_ports=compat\ intel_iommu=on/g {folder}/{kernel}.conf")

	with open(f"/mnt/boot/loader/loader.conf", 'a') as loaderConf:
		loaderConf.write("\ndefault linux-mbp.conf\ntimeout 1\n")

	### build packages ###

	def nobody(command):
		# gpg and git need a home directory
		installation.arch_chroot(f"sh -c \"HOME=/usr/local/src/t2linux runuser nobody -m -s /bin/sh -c \\\"{command}\\\"\"")

	installation.arch_chroot("mkdir /usr/local/src/t2linux")
	installation.arch_chroot("chown nobody:nobody /usr/local/src/t2linux") # makepkg doesn't run as root
	nobody('git clone https://github.com/Redecorating/archinstall-mbp -b packages /usr/local/src/t2linux')

	## apple-ibridge (touchbar)
	if apple_t2["touchbar"] == True:
		print("Building apple-ibridge-dkms-git")
		nobody('cd /usr/local/src/t2linux/apple-ibridge-dkms-git && makepkg')
		print("Installing apple-ibridge-dkms-git")
		installation.arch_chroot("sh -c 'pacman -U --noconfirm /usr/local/src/t2linux/apple-ibridge-dkms-git/apple-ibridge-dkms-git-*-x86_64.pkg*'")

	## audio conf ##
	nobody('cd /usr/local/src/t2linux/apple-t2-audio-config && makepkg')
	if apple_t2["altAudioConf"] == True:
		print("Installing alternate t2 alsa card profile files for 16 inch MacBookPro")
		installation.arch_chroot("sh -c 'pacman -U --noconfirm  /usr/local/src/t2linux/apple-t2-audio-config/apple-t2-audio-config-alt-*-any.pkg*'")
	else:
		print("Installing t2 alsa card profile files")
		installation.arch_chroot("sh -c 'pacman -U --noconfirm /usr/local/src/t2linux/apple-t2-audio-config/apple-t2-audio-config-?.?-?-any.pkg*'")

	## wifi ##

	print("Seting NetworkManager backend to iwd")
	installation.arch_chroot(r"echo [device]\nwifi.backend=iwd >> /etc/NetworkManager/NetworkManager.conf")
	installation.enable_service('iwd')

	print("Configuring WiFi PKGBUILD to use the selected firmware")

	model = apple_t2["model"]
	release = apple_t2["wifiFW"]["release"]

	for key in ["FIRMWARE", "REGULATORY", "NVRAM"]:
		link = apple_t2["wifiFW"][key]
		folder = '/usr/local/src/t2linux/apple-t2-wifi-firmware'
		nobody(f"ln -sr {folder}/{release}/{link} {folder}/{key}")
	installation.arch_chroot(f"sed -i 's#MODEL#{model}#g' {folder}/PKGBUILD")

	print("Making package")
	nobody('cd /usr/local/src/t2linux/apple-t2-wifi-firmware && makepkg')

	print("Installing WiFi firmware package")
	installation.arch_chroot("sh -c 'pacman -U --noconfirm /usr/local/src/t2linux/apple-t2-wifi-firmware/*.pkg.tar.zst'")

	if apple_t2["wifi"] == "bigSur":
		link = "https://gist.github.com/hexchain/22932a13a892e240d71cb98fad62a6a0/archive/50ce4513d2865b1081a972bc09e8da639f94a755.zip"
		nobody(f"wget {link} -O /usr/local/src/t2linux/corellium-wifi.zip")
		nobody("cd /usr/local/src/t2linux && unzip corellium-wifi.zip")
		nobody("mv /usr/local/src/t2linux/22932a13a892e240d71cb98fad62a6a0-50ce4513d2865b1081a972bc09e8da639f94a755 /usr/local/src/t2linux/corellium-wifi")
		nobody('cd /usr/local/src/t2linux/corellium-wifi && makepkg')

		installation.arch_chroot("pacman -U --noconfirm /usr/local/src/t2linux/corellium-wifi/brcm80211-mbp16x-dkms-5.13.9-2-x86_64.pkg.tar.zst")

	# nvram ro
	print('Setting nvram to remount at boot as readonly, as writing to it panics the t2 chip')
	with open(f"/mnt/etc/fstab", 'a') as fstab:
		fstab.write("\nefivarfs /sys/firmware/efi/efivars efivarfs ro,remount 0 0\n")

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

# With the NVRAM files. Many are exactly the same, so only one of any identical
# ones have been included. The needed file can be determined by the chip name,
# i.e. "sid", the version number at the end, i.e. "2.5", and which of "u__m"
# and "m__m" is present.

# The .trx and .clmb files only need the island name, "-X3" etc ones are
# identical to the ones without "-X3", so island.trx and island.clmb can be
# used.

# Mojave #

mojaveFW = {

"release": "mojaveFW",

## Chips and islands ##

"chips": ["C-4355__s-C1", "C-4364__s-B2", "C-4364__s-B3", "C-4377__s-B3"],

"C-4355__s-C1": ["hawaii"],

"C-4364__s-B2": ["ekans", "kahana", "kauai", "lanai",
				  "maui", "midway", "nihau", "sid"],

"C-4364__s-B3": ["Kahana", "Sid"],

"C-4377__s-B3": ["formosa"],

## Nvram ##

"hawaii": [	"P-hawaii-ID_M-YSBC_V-m__m-2.3.txt",
			"P-hawaii-ID_M-YSBC_V-m__m-2.5.txt",
			"P-hawaii-ID_M-YSBC_V-u__m-4.1.txt",
			"P-hawaii-ID_M-YSBC_V-u__m-4.3.txt"],

"ekans": [	"P-ekans-ID_M-HRPN_V-m__m-5.1.txt",
			"P-ekans-ID_M-HRPN_V-m__m-6.1.txt",
			"P-ekans-ID_M-HRPN_V-m__m-6.3.txt",
			"P-ekans-ID_M-HRPN_V-m__m-7.1.txt",
			"P-ekans-ID_M-HRPN_V-m__m-7.5.txt",
			"P-ekans-ID_M-HRPN_V-m__m-7.7.txt",
			"P-ekans-ID_M-HRPN_V-u__m-1.1.txt",
			"P-ekans-ID_M-HRPN_V-u__m-6.1.txt",
			"P-ekans-ID_M-HRPN_V-u__m-7.5.txt"],

"kahana": [	"P-kahana-ID_M-HRPN_V-m__m-7.7.txt",
			"P-kahana-ID_M-HRPN_V-u__m-7.5.txt"],

"kauai": [	"P-kauai-ID_M-HRPN_V-m__m-6.1.txt",
			"P-kauai-ID_M-HRPN_V-m__m-6.3.txt",
			"P-kauai-ID_M-HRPN_V-m__m-7.5.txt",
			"P-kauai-ID_M-HRPN_V-m__m-7.7.txt",
			"P-kauai-ID_M-HRPN_V-u__m-6.1.txt",
			"P-kauai-ID_M-HRPN_V-u__m-7.5.txt"],

"lanai": [	"P-lanai-ID_M-HRPN_V-m__m-7.7.txt",
			"P-lanai-ID_M-HRPN_V-u__m-7.5.txt"],

"maui": [	"P-maui-ID_M-HRPN_V-m__m-7.7.txt",
			"P-maui-ID_M-HRPN_V-u__m-7.5.txt"],

"midway": [	"P-midway-ID_M-HRPN_V-m__m-7.7.txt",
			"P-midway-ID_M-HRPN_V-u__m-7.5.txt"],

"nihau": [	"P-nihau-ID_M-HRPN_V-m__m-7.7.txt",
			"P-nihau-ID_M-HRPN_V-u__m-7.5.txt"],

"sid": [	"P-sid-ID_M-HRPN_V-m__m-2.3.txt",
			"P-sid-ID_M-HRPN_V-m__m-5.1.txt",
			"P-sid-ID_M-HRPN_V-m__m-6.1.txt",
			"P-sid-ID_M-HRPN_V-m__m-6.3.txt",
			"P-sid-ID_M-HRPN_V-m__m-7.1.txt",
			"P-sid-ID_M-HRPN_V-m__m-7.5.txt",
			"P-sid-ID_M-HRPN_V-m__m-7.7.txt",
			"P-sid-ID_M-HRPN_V-u__m-1.1.txt",
			"P-sid-ID_M-HRPN_V-u__m-6.1.txt",
			"P-sid-ID_M-HRPN_V-u__m-7.5.txt"],

"Kahana": [	"P-kahana-ID_M-HRPN_V-m__m-7.9.txt",
			"P-kahana-ID_M-HRPN_V-u__m-7.7.txt"],

"Sid": [	"P-sid-ID_M-HRPN_V-m__m-7.9.txt",
			"P-sid-ID_M-HRPN_V-u__m-7.7.txt"],

"formosa": ["P-formosa-ID_M-SPPR_V-m__m-2.0.txt",
			"P-formosa-ID_M-SPPR_V-u__m-2.0.txt"]
}

# bigSur

bigSurFW = {

"release": "bigSurFW",

## Chips and islands ##

"chips": [	"C-4355__s-C1", "C-4364__s-B2",
			"C-4364__s-B3", "C-4377__s-B3"],

"C-4355__s-C1": ["hawaii"],

"C-4364__s-B2": ["ekans", "hanauma", "kahana", "kauai", "lanai",
					  "maui", "midway", "nihau", "sid"],

"C-4364__s-B3": ["Bali", "Borneo", "Hanauma", "Kahana",
				 "Kure", "Sid", "Trinidad"],

"C-4377__s-B3": ["fiji", "formosa", "tahiti"],

## Nvram ##

# 4355 C1

"hawaii": [	"P-hawaii-ID_M-YSBC_V-m__m-2.3.txt",
			"P-hawaii-ID_M-YSBC_V-m__m-2.5.txt",
			"P-hawaii-ID_M-YSBC_V-u__m-4.1.txt",
			"P-hawaii-ID_M-YSBC_V-u__m-4.3.txt"],

# 4364 B2

"ekans": [	"P-ekans_M-HRPN_V-m__m-5.1.txt",
			"P-ekans_M-HRPN_V-m__m-6.1.txt",
			"P-ekans_M-HRPN_V-m__m-6.3.txt",
			"P-ekans_M-HRPN_V-m__m-7.1.txt",
			"P-ekans_M-HRPN_V-m__m-7.5.txt",
			"P-ekans_M-HRPN_V-m__m-7.7.txt",
			"P-ekans_M-HRPN_V-u__m-1.1.txt",
			"P-ekans_M-HRPN_V-u__m-6.1.txt",
			"P-ekans_M-HRPN_V-u__m-7.5.txt"],

"hanauma": ["P-hanauma_M-HRPN_V-m__m-7.7.txt",
			"P-hanauma_M-HRPN_V-u__m-7.5.txt"],

"kahana": [	"P-kahana_M-HRPN_V-m__m-7.7.txt",
			"P-kahana_M-HRPN_V-u__m-7.5.txt"],

"kauai": [	"P-kauai_M-HRPN_V-m__m-6.1.txt",
			"P-kauai_M-HRPN_V-m__m-6.3.txt",
			"P-kauai_M-HRPN_V-m__m-7.5.txt",
			"P-kauai_M-HRPN_V-m__m-7.7.txt",
			"P-kauai_M-HRPN_V-u__m-6.1.txt",
			"P-kauai_M-HRPN_V-u__m-7.5.txt"],

"lanai": [	"P-lanai_M-HRPN_V-m__m-7.7.txt",
			"P-lanai_M-HRPN_V-u__m-7.5.txt"],

"maui": [	"P-maui_M-HRPN_V-m__m-7.7.txt",
			"P-maui_M-HRPN_V-u__m-7.5.txt"],

"midway": [	"P-midway_M-HRPN_V-m__m-7.7.txt",
			"P-midway_M-HRPN_V-u__m-7.5.txt"],

"nihau": [	"P-nihau_M-HRPN_V-m__m-7.7.txt",
			"P-nihau_M-HRPN_V-u__m-7.5.txt"],

"sid": [	"P-sid_M-HRPN_V-m__m-7.5.txt",
			"P-sid_M-HRPN_V-m__m-7.7.txt",
			"P-sid_M-HRPN_V-u__m-7.5.txt"],

# 4364 B3

"Bali": [	"P-bali_M-HRPN_V-m__m-7.9.txt",
			"P-bali_M-HRPN_V-u__m-7.7.txt"],

"Borneo": [	"P-borneo_M-HRPN_V-m__m-7.9.txt",
			"P-borneo_M-HRPN_V-u__m-7.7.txt",
			"P-borneo_M-HRPN_V-u__m-7.9.txt"],

"Hanauma": ["P-hanauma_M-HRPN_V-m__m-7.9.txt",
			"P-hanauma_M-HRPN_V-u__m-7.7.txt"],

"Kahana": [	"P-kahana_M-HRPN_V-m__m-7.9.txt",
			"P-kahana_M-HRPN_V-u__m-7.7.txt"],

"Kure": [	"P-kure_M-HRPN_V-m__m-7.9.txt",
			"P-kure_M-HRPN_V-u__m-7.7.txt"],

"Sid": [	"P-sid_M-HRPN_V-m__m-7.9.txt",
			"P-sid_M-HRPN_V-u__m-7.7.txt"],

"Trinidad":["P-trinidad_M-HRPN_V-m__m-7.9.txt",
			"P-trinidad_M-HRPN_V-u__m-7.7.txt"],

# 4377 B3

"fiji": [	"P-fiji-ID_M-SPPR_V-m__m-2.0.txt",
			"P-fiji-ID_M-SPPR_V-u__m-2.0.txt"],

"formosa": ["P-fiji-ID_M-SPPR_V-m__m-2.0.txt",
			"P-fiji-ID_M-SPPR_V-u__m-2.0.txt"],

"tahiti": [	"P-fiji-ID_M-SPPR_V-m__m-2.0.txt",
			"P-fiji-ID_M-SPPR_V-u__m-2.0.txt"]

}

# vim: autoindent tabstop=4 shiftwidth=4 noexpandtab number
