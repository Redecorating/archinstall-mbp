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

	
	## WiFi Functions (aka bloat) ##

	def checkWifiSupport(model):
	
		if False: # TODO: if no t2
			model = input("What model do you want wifi for, if any") # TODO: implement 'if any'
			return checkWifiSupport(model)
		if "o16,1" in model or "o16,4" in model:
			print("Currently WiFi only works on this model with Corellium's wifi patch for M1 Macs. To get this working, you need to compile a custom kernel (this one https://github.com/jamlam/mbp-16.1-linux-wifi). You will need to use firmware files from macOS bigsur.")
			M1wifiKernelDL = archinstall.generic_select(['Yes', 'No'], "Would you like to have the source for this kernel downloaded (to /usr/local/src/t2linux in the Arch Installation)? You can then compile it later without internet. ")
			return "M1 " + M1wifiKernelDL
		elif "o16," in model or "o15,4" in model:
			print("Currently there is no wifi support for this model.")
			return "No"
		else: 
			return "Yes"

	def checkLocalFirmware():

		# these return >0 if it isn't in dmesg.
		brcmChipPresent = os.system("journalctl -b '--grep=brcmfmac: brcmf_fw_alloc_request: using brcm/brcmfmac.*-pcie for chip BCM' >/dev/null")
		brcmHostWorkingFW = os.system("journalctl -b '--grep=brcmfmac: brcmf_c_preinit_dcmds: Firmware: BCM.* version .* FWID' > /dev/null")
	
		if brcmChipPresent != 0:
			return "No Chip"
		else:
			if brcmHostWorkingFW == 0:
				return "Copy"
			else:
				return "No copy"

	def selectFirmwareMethod(LocalFirmware):
		if LocalFirmware == "Copy asdkljfsda;kf": # TODO: implement this
			print("WiFi firmware is loaded currently. If you put the firmware listed by `ioreg -l | grep RequestedFiles` in /lib/firmware/brcm and renamed the files, this will be the correct firmware for your chip, and it should be copied to the install. If WiFi worked without you having to put your firmware in, then the default firmware might not be ideal for your WiFi chip. If you have the output of the ioreg commend with you, this script can download the right firmware for you. If you don't have the output of ioreg, just select copy and get the right firmware later.")
			method = archinstall.generic_select(['Download', 'Copy'], "Do you want to copy the WiFi firmware that's currently being used, or download firmware? ")
		else:
			method = 'Download'
		return method

	def select_download_firmware():
		hawaii = ["P-hawaii-ID_M-YSBC_V-m__m-2.3.txt", "P-hawaii-ID_M-YSBC_V-m__m-2.5.txt", "P-hawaii-ID_M-YSBC_V-u__m-4.1.txt", "P-hawaii-ID_M-YSBC_V-u__m-4.3.txt", "P-hawaii-X0_M-YSBC_V-m__m-2.3.txt", "P-hawaii-X0_M-YSBC_V-m__m-2.5.txt", "P-hawaii-X0_M-YSBC_V-u__m-4.1.txt", "P-hawaii-X0_M-YSBC_V-u__m-4.3.txt", "P-hawaii-X2_M-YSBC_V-m__m-2.3.txt", "P-hawaii-X2_M-YSBC_V-m__m-2.5.txt", "P-hawaii-X2_M-YSBC_V-u__m-4.1.txt", "P-hawaii-X2_M-YSBC_V-u__m-4.3.txt", "P-hawaii-X3_M-YSBC_V-m__m-2.3.txt", "P-hawaii-X3_M-YSBC_V-m__m-2.5.txt", "P-hawaii-X3_M-YSBC_V-u__m-4.1.txt", "P-hawaii-X3_M-YSBC_V-u__m-4.3.txt", "P-hawaii_M-YSBC_V-m__m-2.3.txt", "P-hawaii_M-YSBC_V-m__m-2.5.txt", "P-hawaii_M-YSBC_V-u__m-4.1.txt", "P-hawaii_M-YSBC_V-u__m-4.3.txt", "hawaii-ID.clmb", "hawaii-ID.trx", "hawaii-ID.txcb", "hawaii-X0.clmb", "hawaii-X0.trx", "hawaii-X0.txcb", "hawaii-X2.clmb", "hawaii-X2.trx", "hawaii-X2.txcb", "hawaii-X3.clmb", "hawaii-X3.trx", "hawaii-X3.txcb", "hawaii.clmb", "hawaii.trx", "hawaii.txcb"]

		ekans = ["P-ekans-ID_M-HRPN_V-m__m-5.1.txt", "P-ekans-ID_M-HRPN_V-m__m-6.1.txt", "P-ekans-ID_M-HRPN_V-m__m-6.3.txt", "P-ekans-ID_M-HRPN_V-m__m-7.1.txt", "P-ekans-ID_M-HRPN_V-m__m-7.3.txt", "P-ekans-ID_M-HRPN_V-m__m-7.5.txt", "P-ekans-ID_M-HRPN_V-m__m-7.7.txt", "P-ekans-ID_M-HRPN_V-u__m-1.1.txt", "P-ekans-ID_M-HRPN_V-u__m-6.1.txt", "P-ekans-ID_M-HRPN_V-u__m-7.1.txt", "P-ekans-ID_M-HRPN_V-u__m-7.3.txt", "P-ekans-ID_M-HRPN_V-u__m-7.5.txt", "P-ekans-X0_M-HRPN_V-m__m-5.1.txt", "P-ekans-X0_M-HRPN_V-m__m-6.1.txt", "P-ekans-X0_M-HRPN_V-m__m-6.3.txt", "P-ekans-X0_M-HRPN_V-m__m-7.1.txt", "P-ekans-X0_M-HRPN_V-m__m-7.3.txt", "P-ekans-X0_M-HRPN_V-m__m-7.5.txt", "P-ekans-X0_M-HRPN_V-m__m-7.7.txt", "P-ekans-X0_M-HRPN_V-u__m-1.1.txt", "P-ekans-X0_M-HRPN_V-u__m-6.1.txt", "P-ekans-X0_M-HRPN_V-u__m-7.1.txt", "P-ekans-X0_M-HRPN_V-u__m-7.3.txt", "P-ekans-X0_M-HRPN_V-u__m-7.5.txt", "P-ekans-X2_M-HRPN_V-m__m-5.1.txt", "P-ekans-X2_M-HRPN_V-m__m-6.1.txt", "P-ekans-X2_M-HRPN_V-m__m-6.3.txt", "P-ekans-X2_M-HRPN_V-m__m-7.1.txt", "P-ekans-X2_M-HRPN_V-m__m-7.3.txt", "P-ekans-X2_M-HRPN_V-m__m-7.5.txt", "P-ekans-X2_M-HRPN_V-m__m-7.7.txt", "P-ekans-X2_M-HRPN_V-u__m-1.1.txt", "P-ekans-X2_M-HRPN_V-u__m-6.1.txt", "P-ekans-X2_M-HRPN_V-u__m-7.1.txt", "P-ekans-X2_M-HRPN_V-u__m-7.3.txt", "P-ekans-X2_M-HRPN_V-u__m-7.5.txt", "P-ekans-X3_M-HRPN_V-m__m-5.1.txt", "P-ekans-X3_M-HRPN_V-m__m-6.1.txt", "P-ekans-X3_M-HRPN_V-m__m-6.3.txt", "P-ekans-X3_M-HRPN_V-m__m-7.1.txt", "P-ekans-X3_M-HRPN_V-m__m-7.3.txt", "P-ekans-X3_M-HRPN_V-m__m-7.5.txt", "P-ekans-X3_M-HRPN_V-m__m-7.7.txt", "P-ekans-X3_M-HRPN_V-u__m-1.1.txt", "P-ekans-X3_M-HRPN_V-u__m-6.1.txt", "P-ekans-X3_M-HRPN_V-u__m-7.1.txt", "P-ekans-X3_M-HRPN_V-u__m-7.3.txt", "P-ekans-X3_M-HRPN_V-u__m-7.5.txt", "P-ekans_M-HRPN_V-m__m-5.1.txt", "P-ekans_M-HRPN_V-m__m-6.1.txt", "P-ekans_M-HRPN_V-m__m-6.3.txt", "P-ekans_M-HRPN_V-m__m-7.1.txt", "P-ekans_M-HRPN_V-m__m-7.3.txt", "P-ekans_M-HRPN_V-m__m-7.5.txt", "P-ekans_M-HRPN_V-m__m-7.7.txt", "P-ekans_M-HRPN_V-u__m-1.1.txt", "P-ekans_M-HRPN_V-u__m-6.1.txt", "P-ekans_M-HRPN_V-u__m-7.1.txt", "P-ekans_M-HRPN_V-u__m-7.3.txt", "P-ekans_M-HRPN_V-u__m-7.5.txt", "ekans-ID.clmb", "ekans-ID.trx", "ekans-ID.txcb", "ekans-X0.clmb", "ekans-X0.trx", "ekans-X0.txcb", "ekans-X2.clmb", "ekans-X2.trx", "ekans-X2.txcb", "ekans-X3.clmb", "ekans-X3.trx", "ekans-X3.txcb", "ekans.clmb", "ekans.trx", "ekans.txcb"]

		kahana = ["P-kahana-ID_M-HRPN_V-m__m-7.7.txt", "P-kahana-ID_M-HRPN_V-u__m-7.5.txt", "P-kahana-X0_M-HRPN_V-m__m-7.7.txt", "P-kahana-X0_M-HRPN_V-u__m-7.5.txt", "P-kahana-X2_M-HRPN_V-m__m-7.7.txt", "P-kahana-X2_M-HRPN_V-u__m-7.5.txt", "P-kahana-X3_M-HRPN_V-m__m-7.7.txt", "P-kahana-X3_M-HRPN_V-u__m-7.5.txt", "P-kahana_M-HRPN_V-m__m-7.7.txt", "P-kahana_M-HRPN_V-u__m-7.5.txt", "kahana-ID.clmb", "kahana-ID.trx", "kahana-ID.txcb", "kahana-X0.clmb", "kahana-X0.trx", "kahana-X0.txcb", "kahana-X2.clmb", "kahana-X2.trx", "kahana-X2.txcb", "kahana-X3.clmb", "kahana-X3.trx", "kahana-X3.txcb", "kahana.clmb", "kahana.trx", "kahana.txcb"]

		kauai = ["P-kauai-ID_M-HRPN_V-m__m-6.1.txt", "P-kauai-ID_M-HRPN_V-m__m-6.3.txt", "P-kauai-ID_M-HRPN_V-m__m-7.1.txt", "P-kauai-ID_M-HRPN_V-m__m-7.3.txt", "P-kauai-ID_M-HRPN_V-m__m-7.5.txt", "P-kauai-ID_M-HRPN_V-m__m-7.7.txt", "P-kauai-ID_M-HRPN_V-u__m-6.1.txt", "P-kauai-ID_M-HRPN_V-u__m-7.1.txt", "P-kauai-ID_M-HRPN_V-u__m-7.3.txt", "P-kauai-ID_M-HRPN_V-u__m-7.5.txt", "P-kauai-X0_M-HRPN_V-m__m-6.1.txt", "P-kauai-X0_M-HRPN_V-m__m-6.3.txt", "P-kauai-X0_M-HRPN_V-m__m-7.1.txt", "P-kauai-X0_M-HRPN_V-m__m-7.3.txt", "P-kauai-X0_M-HRPN_V-m__m-7.5.txt", "P-kauai-X0_M-HRPN_V-m__m-7.7.txt", "P-kauai-X0_M-HRPN_V-u__m-6.1.txt", "P-kauai-X0_M-HRPN_V-u__m-7.1.txt", "P-kauai-X0_M-HRPN_V-u__m-7.3.txt", "P-kauai-X0_M-HRPN_V-u__m-7.5.txt", "P-kauai-X2_M-HRPN_V-m__m-6.1.txt", "P-kauai-X2_M-HRPN_V-m__m-6.3.txt", "P-kauai-X2_M-HRPN_V-m__m-7.1.txt", "P-kauai-X2_M-HRPN_V-m__m-7.3.txt", "P-kauai-X2_M-HRPN_V-m__m-7.5.txt", "P-kauai-X2_M-HRPN_V-m__m-7.7.txt", "P-kauai-X2_M-HRPN_V-u__m-6.1.txt", "P-kauai-X2_M-HRPN_V-u__m-7.1.txt", "P-kauai-X2_M-HRPN_V-u__m-7.3.txt", "P-kauai-X2_M-HRPN_V-u__m-7.5.txt", "P-kauai-X3_M-HRPN_V-m__m-6.1.txt", "P-kauai-X3_M-HRPN_V-m__m-6.3.txt", "P-kauai-X3_M-HRPN_V-m__m-7.1.txt", "P-kauai-X3_M-HRPN_V-m__m-7.3.txt", "P-kauai-X3_M-HRPN_V-m__m-7.5.txt", "P-kauai-X3_M-HRPN_V-m__m-7.7.txt", "P-kauai-X3_M-HRPN_V-u__m-6.1.txt", "P-kauai-X3_M-HRPN_V-u__m-7.1.txt", "P-kauai-X3_M-HRPN_V-u__m-7.3.txt", "P-kauai-X3_M-HRPN_V-u__m-7.5.txt", "P-kauai_M-HRPN_V-m__m-6.1.txt", "P-kauai_M-HRPN_V-m__m-6.3.txt", "P-kauai_M-HRPN_V-m__m-7.1.txt", "P-kauai_M-HRPN_V-m__m-7.3.txt", "P-kauai_M-HRPN_V-m__m-7.5.txt", "P-kauai_M-HRPN_V-m__m-7.7.txt", "P-kauai_M-HRPN_V-u__m-6.1.txt", "P-kauai_M-HRPN_V-u__m-7.1.txt", "P-kauai_M-HRPN_V-u__m-7.3.txt", "P-kauai_M-HRPN_V-u__m-7.5.txt", "kauai-ID.clmb", "kauai-ID.trx", "kauai-ID.txcb", "kauai-X0.clmb", "kauai-X0.trx", "kauai-X0.txcb", "kauai-X2.clmb", "kauai-X2.trx", "kauai-X2.txcb", "kauai-X3.clmb", "kauai-X3.trx", "kauai-X3.txcb", "kauai.clmb", "kauai.trx", "kauai.txcb"]

		lanai = ["P-lanai-ID_M-HRPN_V-m__m-7.7.txt", "P-lanai-ID_M-HRPN_V-u__m-7.5.txt", "P-lanai-X0_M-HRPN_V-m__m-7.7.txt", "P-lanai-X0_M-HRPN_V-u__m-7.5.txt", "P-lanai-X2_M-HRPN_V-m__m-7.7.txt", "P-lanai-X2_M-HRPN_V-u__m-7.5.txt", "P-lanai-X3_M-HRPN_V-m__m-7.7.txt", "P-lanai-X3_M-HRPN_V-u__m-7.5.txt", "P-lanai_M-HRPN_V-m__m-7.7.txt", "P-lanai_M-HRPN_V-u__m-7.5.txt", "lanai-ID.clmb", "lanai-ID.trx", "lanai-ID.txcb", "lanai-X0.clmb", "lanai-X0.trx", "lanai-X0.txcb", "lanai-X2.clmb", "lanai-X2.trx", "lanai-X2.txcb", "lanai-X3.clmb", "lanai-X3.trx", "lanai-X3.txcb", "lanai.clmb", "lanai.trx", "lanai.txcb"]

		maui = ["P-maui-ID_M-HRPN_V-m__m-6.1.txt", "P-maui-ID_M-HRPN_V-m__m-6.3.txt", "P-maui-ID_M-HRPN_V-m__m-7.1.txt", "P-maui-ID_M-HRPN_V-m__m-7.3.txt", "P-maui-ID_M-HRPN_V-m__m-7.5.txt", "P-maui-ID_M-HRPN_V-m__m-7.7.txt", "P-maui-ID_M-HRPN_V-u__m-6.1.txt", "P-maui-ID_M-HRPN_V-u__m-7.1.txt", "P-maui-ID_M-HRPN_V-u__m-7.3.txt", "P-maui-ID_M-HRPN_V-u__m-7.5.txt", "P-maui-X0_M-HRPN_V-m__m-6.1.txt", "P-maui-X0_M-HRPN_V-m__m-6.3.txt", "P-maui-X0_M-HRPN_V-m__m-7.1.txt", "P-maui-X0_M-HRPN_V-m__m-7.3.txt", "P-maui-X0_M-HRPN_V-m__m-7.5.txt", "P-maui-X0_M-HRPN_V-m__m-7.7.txt", "P-maui-X0_M-HRPN_V-u__m-6.1.txt", "P-maui-X0_M-HRPN_V-u__m-7.1.txt", "P-maui-X0_M-HRPN_V-u__m-7.3.txt", "P-maui-X0_M-HRPN_V-u__m-7.5.txt", "P-maui-X2_M-HRPN_V-m__m-6.1.txt", "P-maui-X2_M-HRPN_V-m__m-6.3.txt", "P-maui-X2_M-HRPN_V-m__m-7.1.txt", "P-maui-X2_M-HRPN_V-m__m-7.3.txt", "P-maui-X2_M-HRPN_V-m__m-7.5.txt", "P-maui-X2_M-HRPN_V-m__m-7.7.txt", "P-maui-X2_M-HRPN_V-u__m-6.1.txt", "P-maui-X2_M-HRPN_V-u__m-7.1.txt", "P-maui-X2_M-HRPN_V-u__m-7.3.txt", "P-maui-X2_M-HRPN_V-u__m-7.5.txt", "P-maui-X3_M-HRPN_V-m__m-6.1.txt", "P-maui-X3_M-HRPN_V-m__m-6.3.txt", "P-maui-X3_M-HRPN_V-m__m-7.1.txt", "P-maui-X3_M-HRPN_V-m__m-7.3.txt", "P-maui-X3_M-HRPN_V-m__m-7.5.txt", "P-maui-X3_M-HRPN_V-m__m-7.7.txt", "P-maui-X3_M-HRPN_V-u__m-6.1.txt", "P-maui-X3_M-HRPN_V-u__m-7.1.txt", "P-maui-X3_M-HRPN_V-u__m-7.3.txt", "P-maui-X3_M-HRPN_V-u__m-7.5.txt", "P-maui_M-HRPN_V-m__m-6.1.txt", "P-maui_M-HRPN_V-m__m-6.3.txt", "P-maui_M-HRPN_V-m__m-7.1.txt", "P-maui_M-HRPN_V-m__m-7.3.txt", "P-maui_M-HRPN_V-m__m-7.5.txt", "P-maui_M-HRPN_V-m__m-7.7.txt", "P-maui_M-HRPN_V-u__m-6.1.txt", "P-maui_M-HRPN_V-u__m-7.1.txt", "P-maui_M-HRPN_V-u__m-7.3.txt", "P-maui_M-HRPN_V-u__m-7.5.txt", "maui-ID.clmb", "maui-ID.trx", "maui-ID.txcb", "maui-X0.clmb", "maui-X0.trx", "maui-X0.txcb", "maui-X2.clmb", "maui-X2.trx", "maui-X2.txcb", "maui-X3.clmb", "maui-X3.trx", "maui-X3.txcb", "maui.clmb", "maui.trx", "maui.txcb"]

		midway = ["P-midway-ID_M-HRPN_V-m__m-7.7.txt", "P-midway-ID_M-HRPN_V-u__m-7.5.txt", "P-midway-X0_M-HRPN_V-m__m-7.7.txt", "P-midway-X0_M-HRPN_V-u__m-7.5.txt", "P-midway-X2_M-HRPN_V-m__m-7.7.txt", "P-midway-X2_M-HRPN_V-u__m-7.5.txt", "P-midway-X3_M-HRPN_V-m__m-7.7.txt", "P-midway-X3_M-HRPN_V-u__m-7.5.txt", "P-midway_M-HRPN_V-m__m-7.7.txt", "P-midway_M-HRPN_V-u__m-7.5.txt", "midway-ID.clmb", "midway-ID.trx", "midway-ID.txcb", "midway-X0.clmb", "midway-X0.trx", "midway-X0.txcb", "midway-X2.clmb", "midway-X2.trx", "midway-X2.txcb", "midway-X3.clmb", "midway-X3.trx", "midway-X3.txcb", "midway.clmb", "midway.trx", "midway.txcb"]

		nihau = ["P-nihau-ID_M-HRPN_V-m__m-7.7.txt", "P-nihau-ID_M-HRPN_V-u__m-7.5.txt", "P-nihau-X0_M-HRPN_V-m__m-7.7.txt", "P-nihau-X0_M-HRPN_V-u__m-7.5.txt", "P-nihau-X2_M-HRPN_V-m__m-7.7.txt", "P-nihau-X2_M-HRPN_V-u__m-7.5.txt", "P-nihau-X3_M-HRPN_V-m__m-7.7.txt", "P-nihau-X3_M-HRPN_V-u__m-7.5.txt", "P-nihau_M-HRPN_V-m__m-7.7.txt", "P-nihau_M-HRPN_V-u__m-7.5.txt", "nihau-ID.clmb", "nihau-ID.trx", "nihau-ID.txcb", "nihau-X0.clmb", "nihau-X0.trx", "nihau-X0.txcb", "nihau-X2.clmb", "nihau-X2.trx", "nihau-X2.txcb", "nihau-X3.clmb", "nihau-X3.trx", "nihau-X3.txcb", "nihau.clmb", "nihau.trx", "nihau.txcb"]

		sid = ["P-sid-ID_M-HRPN_V-m__m-2.3.txt", "P-sid-ID_M-HRPN_V-m__m-3.1.txt", "P-sid-ID_M-HRPN_V-m__m-5.1.txt", "P-sid-ID_M-HRPN_V-m__m-6.1.txt", "P-sid-ID_M-HRPN_V-m__m-6.3.txt", "P-sid-ID_M-HRPN_V-m__m-7.1.txt", "P-sid-ID_M-HRPN_V-m__m-7.3.txt", "P-sid-ID_M-HRPN_V-m__m-7.5.txt", "P-sid-ID_M-HRPN_V-m__m-7.7.txt", "P-sid-ID_M-HRPN_V-u__m-1.1.txt", "P-sid-ID_M-HRPN_V-u__m-6.1.txt", "P-sid-ID_M-HRPN_V-u__m-7.1.txt", "P-sid-ID_M-HRPN_V-u__m-7.3.txt", "P-sid-ID_M-HRPN_V-u__m-7.5.txt", "P-sid-X0_M-HRPN_V-m__m-2.3.txt", "P-sid-X0_M-HRPN_V-m__m-3.1.txt", "P-sid-X0_M-HRPN_V-m__m-5.1.txt", "P-sid-X0_M-HRPN_V-m__m-6.1.txt", "P-sid-X0_M-HRPN_V-m__m-6.3.txt", "P-sid-X0_M-HRPN_V-m__m-7.1.txt", "P-sid-X0_M-HRPN_V-m__m-7.3.txt", "P-sid-X0_M-HRPN_V-m__m-7.5.txt", "P-sid-X0_M-HRPN_V-m__m-7.7.txt", "P-sid-X0_M-HRPN_V-u__m-1.1.txt", "P-sid-X0_M-HRPN_V-u__m-6.1.txt", "P-sid-X0_M-HRPN_V-u__m-7.1.txt", "P-sid-X0_M-HRPN_V-u__m-7.3.txt", "P-sid-X0_M-HRPN_V-u__m-7.5.txt", "P-sid-X2_M-HRPN_V-m__m-2.3.txt", "P-sid-X2_M-HRPN_V-m__m-3.1.txt", "P-sid-X2_M-HRPN_V-m__m-5.1.txt", "P-sid-X2_M-HRPN_V-m__m-6.1.txt", "P-sid-X2_M-HRPN_V-m__m-6.3.txt", "P-sid-X2_M-HRPN_V-m__m-7.1.txt", "P-sid-X2_M-HRPN_V-m__m-7.3.txt", "P-sid-X2_M-HRPN_V-m__m-7.5.txt", "P-sid-X2_M-HRPN_V-m__m-7.7.txt", "P-sid-X2_M-HRPN_V-u__m-1.1.txt", "P-sid-X2_M-HRPN_V-u__m-6.1.txt", "P-sid-X2_M-HRPN_V-u__m-7.1.txt", "P-sid-X2_M-HRPN_V-u__m-7.3.txt", "P-sid-X2_M-HRPN_V-u__m-7.5.txt", "P-sid-X3_M-HRPN_V-m__m-2.3.txt", "P-sid-X3_M-HRPN_V-m__m-3.1.txt", "P-sid-X3_M-HRPN_V-m__m-5.1.txt", "P-sid-X3_M-HRPN_V-m__m-6.1.txt", "P-sid-X3_M-HRPN_V-m__m-6.3.txt", "P-sid-X3_M-HRPN_V-m__m-7.1.txt", "P-sid-X3_M-HRPN_V-m__m-7.3.txt", "P-sid-X3_M-HRPN_V-m__m-7.5.txt", "P-sid-X3_M-HRPN_V-m__m-7.7.txt", "P-sid-X3_M-HRPN_V-u__m-1.1.txt", "P-sid-X3_M-HRPN_V-u__m-6.1.txt", "P-sid-X3_M-HRPN_V-u__m-7.1.txt", "P-sid-X3_M-HRPN_V-u__m-7.3.txt", "P-sid-X3_M-HRPN_V-u__m-7.5.txt", "P-sid_M-HRPN_V-m__m-2.3.txt", "P-sid_M-HRPN_V-m__m-3.1.txt", "P-sid_M-HRPN_V-m__m-5.1.txt", "P-sid_M-HRPN_V-m__m-6.1.txt", "P-sid_M-HRPN_V-m__m-6.3.txt", "P-sid_M-HRPN_V-m__m-7.1.txt", "P-sid_M-HRPN_V-m__m-7.3.txt", "P-sid_M-HRPN_V-m__m-7.5.txt", "P-sid_M-HRPN_V-m__m-7.7.txt", "P-sid_M-HRPN_V-u__m-1.1.txt", "P-sid_M-HRPN_V-u__m-6.1.txt", "P-sid_M-HRPN_V-u__m-7.1.txt", "P-sid_M-HRPN_V-u__m-7.3.txt", "P-sid_M-HRPN_V-u__m-7.5.txt", "sid-ID.clmb", "sid-ID.trx", "sid-ID.txcb", "sid-X0.clmb", "sid-X0.trx", "sid-X0.txcb", "sid-X2.clmb", "sid-X2.trx", "sid-X2.txcb", "sid-X3.clmb", "sid-X3.trx", "sid-X3.txcb", "sid.clmb", "sid.trx", "sid.txcb"]

		Kahana = ["P-kahana-ID_M-HRPN_V-m__m-7.9.txt", "P-kahana-ID_M-HRPN_V-u__m-7.7.txt", "P-kahana-X0_M-HRPN_V-m__m-7.9.txt", "P-kahana-X0_M-HRPN_V-u__m-7.7.txt", "P-kahana-X2_M-HRPN_V-m__m-7.9.txt", "P-kahana-X2_M-HRPN_V-u__m-7.7.txt", "P-kahana-X3_M-HRPN_V-m__m-7.9.txt", "P-kahana-X3_M-HRPN_V-u__m-7.7.txt", "P-kahana_M-HRPN_V-m__m-7.9.txt", "P-kahana_M-HRPN_V-u__m-7.7.txt", "kahana-ID.clmb", "kahana-ID.trx", "kahana-ID.txcb", "kahana-X0.clmb", "kahana-X0.trx", "kahana-X0.txcb", "kahana-X2.clmb", "kahana-X2.trx", "kahana-X2.txcb", "kahana-X3.clmb", "kahana-X3.trx", "kahana-X3.txcb", "kahana.clmb", "kahana.trx", "kahana.txcb"]

		Sid = ["P-sid-ID_M-HRPN_V-m__m-7.9.txt", "P-sid-ID_M-HRPN_V-u__m-7.7.txt", "P-sid-X0_M-HRPN_V-m__m-7.9.txt", "P-sid-X0_M-HRPN_V-u__m-7.7.txt", "P-sid-X2_M-HRPN_V-m__m-7.9.txt", "P-sid-X2_M-HRPN_V-u__m-7.7.txt", "P-sid-X3_M-HRPN_V-m__m-7.9.txt", "P-sid-X3_M-HRPN_V-u__m-7.7.txt", "P-sid_M-HRPN_V-m__m-7.9.txt", "P-sid_M-HRPN_V-u__m-7.7.txt", "sid-ID.clmb", "sid-ID.trx", "sid-ID.txcb", "sid-X0.clmb", "sid-X0.trx", "sid-X0.txcb", "sid-X2.clmb", "sid-X2.trx", "sid-X2.txcb", "sid-X3.clmb", "sid-X3.trx", "sid-X3.txcb", "sid.clmb", "sid.trx", "sid.txcb"]

		formosa = ["P-formosa-ID_M-SPPR_V-m__m-2.0.txt", "P-formosa-ID_M-SPPR_V-m__m-2.1.txt", "P-formosa-ID_M-SPPR_V-m__m-2.3.txt", "P-formosa-ID_M-SPPR_V-m__m-2.5.txt", "P-formosa-ID_M-SPPR_V-m__m-3.1.txt", "P-formosa-ID_M-SPPR_V-m__m-3.3.txt", "P-formosa-ID_M-SPPR_V-m__m-3.5.txt", "P-formosa-ID_M-SPPR_V-m__m-4.1.txt", "P-formosa-ID_M-SPPR_V-m__m-4.3.txt", "P-formosa-ID_M-SPPR_V-m__m-4.5.txt", "P-formosa-ID_M-SPPR_V-u__m-2.0.txt", "P-formosa-ID_M-SPPR_V-u__m-2.1.txt", "P-formosa-ID_M-SPPR_V-u__m-2.3.txt", "P-formosa-ID_M-SPPR_V-u__m-2.5.txt", "P-formosa-ID_M-SPPR_V-u__m-3.1.txt", "P-formosa-ID_M-SPPR_V-u__m-3.3.txt", "P-formosa-ID_M-SPPR_V-u__m-3.5.txt", "P-formosa-ID_M-SPPR_V-u__m-4.1.txt", "P-formosa-ID_M-SPPR_V-u__m-4.3.txt", "P-formosa-ID_M-SPPR_V-u__m-4.5.txt", "P-formosa-X0_M-SPPR_V-m__m-2.0.txt", "P-formosa-X0_M-SPPR_V-m__m-2.1.txt", "P-formosa-X0_M-SPPR_V-m__m-2.3.txt", "P-formosa-X0_M-SPPR_V-m__m-2.5.txt", "P-formosa-X0_M-SPPR_V-m__m-3.1.txt", "P-formosa-X0_M-SPPR_V-m__m-3.3.txt", "P-formosa-X0_M-SPPR_V-m__m-3.5.txt", "P-formosa-X0_M-SPPR_V-m__m-4.1.txt", "P-formosa-X0_M-SPPR_V-m__m-4.3.txt", "P-formosa-X0_M-SPPR_V-m__m-4.5.txt", "P-formosa-X0_M-SPPR_V-u__m-2.0.txt", "P-formosa-X0_M-SPPR_V-u__m-2.1.txt", "P-formosa-X0_M-SPPR_V-u__m-2.3.txt", "P-formosa-X0_M-SPPR_V-u__m-2.5.txt", "P-formosa-X0_M-SPPR_V-u__m-3.1.txt", "P-formosa-X0_M-SPPR_V-u__m-3.3.txt", "P-formosa-X0_M-SPPR_V-u__m-3.5.txt", "P-formosa-X0_M-SPPR_V-u__m-4.1.txt", "P-formosa-X0_M-SPPR_V-u__m-4.3.txt", "P-formosa-X0_M-SPPR_V-u__m-4.5.txt", "P-formosa-X2_M-SPPR_V-m__m-2.0.txt", "P-formosa-X2_M-SPPR_V-m__m-2.1.txt", "P-formosa-X2_M-SPPR_V-m__m-2.3.txt", "P-formosa-X2_M-SPPR_V-m__m-2.5.txt", "P-formosa-X2_M-SPPR_V-m__m-3.1.txt", "P-formosa-X2_M-SPPR_V-m__m-3.3.txt", "P-formosa-X2_M-SPPR_V-m__m-3.5.txt", "P-formosa-X2_M-SPPR_V-m__m-4.1.txt", "P-formosa-X2_M-SPPR_V-m__m-4.3.txt", "P-formosa-X2_M-SPPR_V-m__m-4.5.txt", "P-formosa-X2_M-SPPR_V-u__m-2.0.txt", "P-formosa-X2_M-SPPR_V-u__m-2.1.txt", "P-formosa-X2_M-SPPR_V-u__m-2.3.txt", "P-formosa-X2_M-SPPR_V-u__m-2.5.txt", "P-formosa-X2_M-SPPR_V-u__m-3.1.txt", "P-formosa-X2_M-SPPR_V-u__m-3.3.txt", "P-formosa-X2_M-SPPR_V-u__m-3.5.txt", "P-formosa-X2_M-SPPR_V-u__m-4.1.txt", "P-formosa-X2_M-SPPR_V-u__m-4.3.txt", "P-formosa-X2_M-SPPR_V-u__m-4.5.txt", "P-formosa-X3_M-SPPR_V-m__m-2.0.txt", "P-formosa-X3_M-SPPR_V-m__m-2.1.txt", "P-formosa-X3_M-SPPR_V-m__m-2.3.txt", "P-formosa-X3_M-SPPR_V-m__m-2.5.txt", "P-formosa-X3_M-SPPR_V-m__m-3.1.txt", "P-formosa-X3_M-SPPR_V-m__m-3.3.txt", "P-formosa-X3_M-SPPR_V-m__m-3.5.txt", "P-formosa-X3_M-SPPR_V-m__m-4.1.txt", "P-formosa-X3_M-SPPR_V-m__m-4.3.txt", "P-formosa-X3_M-SPPR_V-m__m-4.5.txt", "P-formosa-X3_M-SPPR_V-u__m-2.0.txt", "P-formosa-X3_M-SPPR_V-u__m-2.1.txt", "P-formosa-X3_M-SPPR_V-u__m-2.3.txt", "P-formosa-X3_M-SPPR_V-u__m-2.5.txt", "P-formosa-X3_M-SPPR_V-u__m-3.1.txt", "P-formosa-X3_M-SPPR_V-u__m-3.3.txt", "P-formosa-X3_M-SPPR_V-u__m-3.5.txt", "P-formosa-X3_M-SPPR_V-u__m-4.1.txt", "P-formosa-X3_M-SPPR_V-u__m-4.3.txt", "P-formosa-X3_M-SPPR_V-u__m-4.5.txt", "P-formosa_M-SPPR_V-m__m-2.0.txt", "P-formosa_M-SPPR_V-m__m-2.1.txt", "P-formosa_M-SPPR_V-m__m-2.3.txt", "P-formosa_M-SPPR_V-m__m-2.5.txt", "P-formosa_M-SPPR_V-m__m-3.1.txt", "P-formosa_M-SPPR_V-m__m-3.3.txt", "P-formosa_M-SPPR_V-m__m-3.5.txt", "P-formosa_M-SPPR_V-m__m-4.1.txt", "P-formosa_M-SPPR_V-m__m-4.3.txt", "P-formosa_M-SPPR_V-m__m-4.5.txt", "P-formosa_M-SPPR_V-u__m-2.0.txt", "P-formosa_M-SPPR_V-u__m-2.1.txt", "P-formosa_M-SPPR_V-u__m-2.3.txt", "P-formosa_M-SPPR_V-u__m-2.5.txt", "P-formosa_M-SPPR_V-u__m-3.1.txt", "P-formosa_M-SPPR_V-u__m-3.3.txt", "P-formosa_M-SPPR_V-u__m-3.5.txt", "P-formosa_M-SPPR_V-u__m-4.1.txt", "P-formosa_M-SPPR_V-u__m-4.3.txt", "P-formosa_M-SPPR_V-u__m-4.5.txt", "formosa-ID.clmb", "formosa-ID.trx", "formosa-ID.txcb", "formosa-X0.clmb", "formosa-X0.trx", "formosa-X0.txcb", "formosa-X2.clmb", "formosa-X2.trx", "formosa-X2.txcb", "formosa-X3.clmb", "formosa-X3.trx", "formosa-X3.txcb", "formosa.clmb", "formosa.trx", "formosa.txcb"]
		""""
		"""
		# Chip
		C_4355__s_C1 = [hawaii]
		C_4364__s_B2 = [ekans, kahana, kauai, lanai, maui, midway, nihau, sid]
		C_4364__s_B3 = [Kahana, Sid] # capitalisation intentional
		C_4377__s_B3 = [formosa]
		C_4355__s_C1_names = ["hawaii"]
		C_4364__s_B2_names = ["ekans", "kahana", "kauai", "lanai", "maui", "midway", "nihau", "sid"]
		C_4364__s_B3_names = ["Kahana", "Sid"]
		C_4377__s_B3_names = ["formosa"]
		chips = [C_4355__s_C1, C_4364__s_B2, C_4364__s_B3, C_4377__s_B3]

		chip_name = archinstall.generic_select(["C-4355__s-C1", "C-4364__s-B2", "C-4364__s-B3", "C-4377__s-B3"], "Which folder? ")
		chip_dict = {"C-4355__s-C1": C_4355__s_C1_names, "C-4364__s-B2": C_4364__s_B2_names, "C-4364__s-B3": C_4364__s_B3_names, "C-4377__s-B3": C_4377__s_B3_names}
		chip = chip_dict[chip_name]
		island_name = archinstall.generic_select(chip, "Which is in the filename? ")
		island_dict = {"hawaii": hawaii, "ekans": ekans, "kahana": kahana, "kauai": kauai, "lanai": lanai, "maui": maui, "midway": midway, "nihau": nihau, "sid": sid, "Kahana": Kahana, "Sid": Sid, "formosa": formosa}
		island = island_dict[island_name]
		
		def filter(List, filterText):
			filtered = []
			print(filterText)
			for item in List:
				if filterText in item:
					filtered.append(item)
			return filtered

		trxList = filter(island, ".trx")
		trxFile = archinstall.generic_select(trxList, "Which Firmware file? ")

		clmbList = filter(island, ".clmb")
		clmbFile = archinstall.generic_select(clmbList, "Which Regulatory file? ")

		txtList = filter(island, ".txt")
		txtFile = archinstall.generic_select(txtList, "Which Firmware file? ")
		# formosa has 99 options here. this doesn't work well

		firmwareFiles = [chip_name + "/" + trxFile, chip_name + "/" + clmbFile, chip_name + "/" + txtFile]
		
		return firmwareFiles
		

	## Check for t2
	global model 
	if os.system("lspci |grep 'Apple Inc. T2' > /dev/null") == 10:
		model = open(f'/sys/devices/virtual/dmi/id/product_name', 'r').read()
	else:
		model = input("This computer does not have a t2 chip. Enter the model identifier of the t2 Mac you intend to use (i.e. MacBookPro16,1 or MacBookAir9,1): ")

	## WiFi ##

	WifiSupport = checkWifiSupport(model)
	archinstall.storage['_apple-t2-wifi'] = "None"
	if 'No' not in WifiSupport:
		if "M1" in WifiSupport:
			archinstall.storage['_apple-t2-wifi'] = "M1"
		else:
			LocalFirmwareStatus = checkLocalFirmware()
			wifiFWsource = selectFirmwareMethod(LocalFirmwareStatus)
			archinstall.storage['_apple-t2-wifi'] = wifiFWsource


	if archinstall.storage['_apple-t2-wifi'] == "Download":
		archinstall.storage['_apple-t2-wifiFW'] = select_download_firmware()



	## Touchbar ##

	archinstall.storage['_apple-t2-touchbar'] = False
	if "MacBookPro" in model:
		archinstall.storage['_apple-t2-touchbar'] = True
	else:
		tb = archinstall.generic_select(["Yes", 'No'], "This computer does not have a touchbar. Would you like the touchbar driver anyway?")
		if tb == "Yes":
			archinstall.storage['_apple-t2-touchbar'] = True
		
	## Audio Conf ##
	
	if model == "MacBookPro16,1" or model == "MacBookPro16,4":
		archinstall.storage['_apple-t2-altAudioConf'] = True	
	else:
		archinstall.storage['_apple-t2-altAudioConf'] = False

	print(archinstall.storage)
	return True
	
	"""
	Stored Vars:
	'_apple-t2-wifi': Download/M1/None/Copy
	'_apple-t2-wifiFW': ['C-4364__s-B3/sid-X3.trx', 'C-4364__s-B3/sid-X2.clmb', 'C-4364__s-B3/P-sid-X0_M-HRPN_V-u__m-7.7.txt'],
	'_apple-t2-touchbar': True/False
	'_apple-t2-altAudioConf': True/False
	"""



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
	
	# add modules to mkinitpcio before mbp initramfs are generated
	installation.arch_chroot("sed -i s/^MODULES=\(/MODULES=\(apple_bce\ hid_apple\ usbhid\ /gm /etc/mkinitcpio.conf")

	installation.arch_chroot("pacman -Syu --noconfirm linux-mbp git linux-mbp-headers apple-bce-dkms-git")
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

	installation.arch_chroot("git clone https://github.com/Redecorating/archinstall-mbp /usr/local/src/t2linux")
	installation.arch_chroot("cd /usr/local/src/t2linux && git checkout -b testing")

	## apple-ibridge (touchbar)
	touchbarWanted = archinstall.storage['_apple-t2-touchbar']
	if touchbarWanted == True:
		installation.arch_chroot("cd /usr/local/src/t2linux/apple-ibridge-dkms-git && makepkg")
		installation.arch_chroot("cd /usr/local/src/t2linux/apple-ibridge-dkms-git && pacman -U apple-ibridge-dkms-git-*-x86_64.pkg*")
	
	## audio conf ##
	altAudioConf = archinstall.storage["_apple-t2-altAudioConf"]
	if altAudioConf == True:
		installation.arch_chroot("cd /usr/local/src/t2linux/apple-t2-audio-config/alt && makepkg")
		installation.arch_chroot("cd /usr/local/src/t2linux/apple-t2-audio-config/alt && pacman -U apple-t2-audio-config-alt-*-any.pkg*")
	else:
		installation.arch_chroot("cd /usr/local/src/t2linux/apple-t2-audio-config/normal && makepkg")
		installation.arch_chroot("cd /usr/local/src/t2linux/apple-t2-audio-config/normal && pacman -U apple-t2-audio-config-*-any.pkg*")

	## wifi ##
	# TODO: wifi as package also what's a case /s
	if archinstall.storage['_apple-t2-wifi'] = "Download":
		requestedFiles = archinstall.storage["_apple-t2-wifiFW"]
		for link in requestedFiles:
			file = requests.get(f"https://dl.t2linux.org/archlinux/apple/wifi-fw/18G2022/{link}")
			link = link[13:]
			open(f"{installation.mountpoint}/usr/local/src/t2linux/{link}", 'wb').write(file.content)
		print("Wifi is not yet set up by this script, but the firmware files you selected have been downloaded to /usr/local/src/t2linux.")
	elif archinstall.storage['_apple-t2-wifi'] = "M1":
		installation.arch_chroot("git clone https://github.com/jamlam/mbp-16.1-linux-wifi /usr/local/src/t2linux/mbp-16.1-linux-wifi")
		installation.arch_chroot("cd /usr/local/src/t2linux/mbp-16.1-linux-wifi && makepkg -o") # don't build it
		print("The kernel with the M1 wifi patches is ready in /usr/local/src/t2linux/mbp-16.1-linux-wifi for you to build later.")
	else:
		print("Nothing is being done for WiFi.")


	# nvram ro

	print('Setting nvram to remount at boot as readonly, as writing to it panics the t2 chip')
	with open(f"{installation.mountpoint}/etc/fstab", 'a') as fstab:
		fstab.write("\nefivarfs /sys/firmware/efi/efivars efivarfs ro,remount 0 0\n")

# vim: autoindent tabstop=4 shiftwidth=4 noexpandtab number
