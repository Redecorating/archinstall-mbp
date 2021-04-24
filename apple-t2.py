# install archinstall if needed and also move this file into the profiles folder. exits before it gets to the python code.
""":"
if [ -e /bin/archinstall ]
then :
else pacman -Sy --noconfirm archinstall
ln -vs /lib/python3.9/site-packages/archinstall /lib/python3.8/site-packages/archinstall
fi
cp -v apple-t2.py /lib/python3.9/site-packages/archinstall/profiles/apple-t2.py
exit 0
"""

import archinstall, os

# Profile for installing on Mac computers that have the T2 security chip
# By Redecorating
#
# Installs:
#	patched 'linux-mbp' kernel
#	dkms 'apple-bce' driver (keyboard, trackpad, audio)
#	dkms 'apple-ibridge' driver (touchbar)
#	audio configuration files
#	t2linux repo for updates to kernel
#	installs wifi firmware for pre catalina models, and can download source for kernel with M1 wifi patches for 16,X models
#	nvram read only because t2 likes to panic

# https://wiki.t2linux.org/distributions/arch/installation/ 


def _prep_function(*args, **kwargs):


	## WiFi Functions ##

	def checkWifiSupport(model):
		if "MacBookPro16," in model:
			print("Currently WiFi only works on this model with Corellium's wifi patch for M1 Macs. To get this working, you need to compile a custom kernel (this one https://github.com/jamlam/mbp-16.1-linux-wifi). You will need to use firmware files from macOS bigsur.")
			M1 = None
			while M1 == None:
				try:
					M1 = archinstall.generic_select(['Yes', 'No'], "Would you like to have the source for this kernel downloaded (to /usr/local/src/t2linux/mbp-16.1-linux-wifi/ in the Arch Installation)? You can then compile it later by running `makepkg -ie` in that directory, without internet. ")
					if M1 == "Yes":
						return "M1"
					elif M1 == "No":
						return "None"
				except:
					print("Invalid input")
		elif "MacBookPro15,4" in model:
			print("Currently there is no wifi support for this model.")
			return "None"
		else: 
			return "Download"

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
		this just fixes that line breaking syntax highlighting due to it's length
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

		chip_name = archinstall.generic_select(["C-4355__s-C1", "C-4364__s-B2", "C-4364__s-B3", "C-4377__s-B3"], "Which folder are the firmware files in? ")
		chip_dict = {"C-4355__s-C1": C_4355__s_C1_names, "C-4364__s-B2": C_4364__s_B2_names, "C-4364__s-B3": C_4364__s_B3_names, "C-4377__s-B3": C_4377__s_B3_names}
		chip = chip_dict[chip_name]
		island_name = archinstall.generic_select(chip, "Which one of these is in the filenames? ")
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
		
		archinstall.print_large_list(txtList, margin_bottom=1)
		index = eval(input("Which NVRAM file? "))
		txtFile = txtList[index] # needs 100x90 ish terminal size at the most
		# TODO handle bad input

		firmwareFiles = {"FIRMWARE": (chip_name + "/" + trxFile), "REGULATORY": (chip_name + "/" + clmbFile), "NVRAM": (chip_name + "/" + txtFile)}
		# https://packages.aunali1.com/apple/wifi-fw/18G2022/C-4364__s-B3/ seems to have symlinks for it's .trx files. C-4364__s-B2 has files of the same name so use them instead?
		if 'C-4364__s-B3' in firmwareFiles["FIRMWARE"]:
			firmwareFiles["FIRMWARE"] = "C-4364__s-B2/" + trxFile
			print("The trx file selected is missing (probably because it's a symlink), so one from the other 4364 folder is being used. This may not work but it might.")
		
		return firmwareFiles
		
	apple_t2 = {}

	t2models = ["MacBookPro16,3", "MacBookPro16,2", "MacBookPro16,1", "MacBookPro16,4", "MacBookPro15,4", "MacBookPro15,1", "MacBookPro15,3", "MacBookPro15,2", "MacBookAir9,1", "MacBookAir8,2", "MacBookAir8,1", "Macmini8,1", "MacPro7,1", "iMac20,1", "iMac20,2", "iMacPro1,1"]

	## Check for t2
	if os.system("lspci |grep 'Apple Inc. T2' > /dev/null") == 10: # XXX revert before merge with main
		model = open(f'/sys/devices/virtual/dmi/id/product_name', 'r').read()
	else:
		print("This computer does not have a t2 chip.")
		ret  = False
		while ret != True:
			try:
				model = archinstall.generic_select(t2models, "Which is the model identifier of the t2 Mac you intend to use? ")
				if model == None:
					raise IndexError
				ret = True
			except IndexError:
				print("Invalid input.")

	apple_t2["model"] = model

	## WiFi ##

	apple_t2['wifi'] = checkWifiSupport(model)

	if apple_t2['wifi'] == "Download":
		print("Please get the output of running `ioreg -l | grep RequestedFiles` in Terminal on macOS, and use it to answer the next few questions.")
		ret = False
		while ret != True:
			try:
				apple_t2['wifiFW'] = select_download_firmware()
				ret = True
			except (IndexError, KeyError):
				print("Invalid input")


	## Touchbar ##

	if "MacBookPro" in model:
		apple_t2['touchbar'] = True
	else:
		apple_t2['touchbar'] = False


	## Audio Conf ##

	if model == "MacBookPro16,1" or model == "MacBookPro16,4":
		apple_t2['altAudioConf'] = True
	else:
		apple_t2['altAudioConf'] = False

	## repeat user's selections ##

	print("Your selected options for the apple-t2 profile:", end="\n\t")
	print(apple_t2)

	archinstall.storage["apple_t2"] = apple_t2

	return True

	"""
	Stored Vars:
	'wifi': Download/M1/None
	'wifiFW': {'FIRMWARE': 'C-4377__s-B3/formosa-X0.trx', 'REGULATORY': 'C-4377__s-B3/formosa-X0.clmb', 'NVRAM': 'C-4377__s-B3/P-formosa-ID_M-SPPR_V-m__m-2.1.txt'}
	'touchbar': True/False
	'altAudioConf': True/False
	'model': 'MacBookPro15,1'
	"""



if __name__ == 'apple-t2':

	apple_t2 = archinstall.storage["apple_t2"]

	## t2linux repo ##

	print('Adding t2linux repo to /etc/pacman.conf in install')
	with open(f'{installation.mountpoint}/etc/pacman.conf', 'a') as pacmanconf:
		pacmanconf.write("\n[mbp]\n")
		pacmanconf.write("Server = https://dl.t2linux.org/archlinux/$repo/$arch\n")

	# add package signing key #

	installation.arch_chroot("sh -c 'curl https://dl.t2linux.org/archlinux/key.asc > /t2key.asc'")
	installation.arch_chroot("pacman-key --add /t2key.asc")
	installation.arch_chroot("pacman-key --lsign 7F9B8FC29F78B339") # aunali1's key
	os.remove(f"{installation.mountpoint}/t2key.asc")

	## Kernel and apple-bce ##

	print('Installing patched kernel and apple-bce')

	# add modules to mkinitpcio before the mbp initramfs' are generated
	installation.arch_chroot("sed -i s/^MODULES=\(/MODULES=\(apple_bce\ hid_apple\ usbhid\ /gm /etc/mkinitcpio.conf")

	installation.arch_chroot("pacman -Syu --noconfirm linux-mbp git linux-mbp-headers apple-bce-dkms-git")
	with open(f"{installation.mountpoint}/etc/modules-load.d/t2.conf", 'a') as modulesConf:
		modulesConf.write("apple-bce\n")

	## add kernel to systemd-boot as default ##

	print("Adding linux-mbp to systemd-boot menu as default")

	try:
		# work around https://github.com/archlinux/archinstall/issues/322
		confFiles = []
		for file in os.listdir(f"{installation.mountpoint}/boot/loader/entries"):
			if "mbp" not in file:
				confFiles.append(file)
		normalBootFileName = sorted(confFiles)[-1]
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
	except:
		print("Failed to set linux-mbp as the default kernel.")

	### build packages ###

	try:
		installation.arch_chroot("mkdir /usr/local/src/t2linux")
		installation.arch_chroot("chown nobody:nobody /usr/local/src/t2linux") # makepkg doesn't run as root
		installation.arch_chroot("runuser nobody -s /bin/sh -c 'git clone -b testing https://github.com/Redecorating/archinstall-mbp /usr/local/src/t2linux'")
	except:
		print("Failed to clone Redecorating/archinstall-mbp, the next few steps will most likely also fail.")

	## apple-ibridge (touchbar)
	if apple_t2["touchbar"] == True:
		try:
			print("Building apple-ibridge-dkms-git")
			installation.arch_chroot("runuser nobody -s /bin/sh -c 'cd /usr/local/src/t2linux/apple-ibridge-dkms-git && makepkg'")
			print("Installing apple-ibridge-dkms-git")
			installation.arch_chroot("sh -c 'pacman -U --noconfirm /usr/local/src/t2linux/apple-ibridge-dkms-git/apple-ibridge-dkms-git-*-x86_64.pkg*'")
		except:
			print("An error occured when installing the toucbar driver.")

	## audio conf ##
	try:
		if apple_t2["altAudioConf"] == True:
			print("Installing alternate t2 alsa card profile files for 16 inch MacBookPro")
			installation.arch_chroot("runuser nobody -s /bin/sh -c 'cd /usr/local/src/t2linux/apple-t2-audio-config/alt && makepkg'")
			installation.arch_chroot("sh -c 'pacman -U --noconfirm  /usr/local/src/t2linux/apple-t2-audio-config/alt/apple-t2-audio-config-alt-*-any.pkg*'")
		else:
			print("Installing t2 alsa card profile files")
			installation.arch_chroot("runuser nobody -s /bin/sh -c 'cd /usr/local/src/t2linux/apple-t2-audio-config/normal && makepkg'")
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
				installation.arch_chroot(f"sed -i 's#{key}#{link}#g' /usr/local/src/t2linux/apple-t2-wifi-firmware/PKGBUILD")
			installation.arch_chroot(f"sed -i 's#MODEL#{model}#g' /usr/local/src/t2linux/apple-t2-wifi-firmware/PKGBUILD")

			print("Downloading firmware and making package")
			installation.arch_chroot("runuser nobody -s /bin/sh -c 'cd /usr/local/src/t2linux/apple-t2-wifi-firmware && makepkg'")

			print("Installing WiFi firmware package")
			installation.arch_chroot("sh -c 'pacman -U --noconfirm /usr/local/src/t2linux/apple-t2-wifi-firmware/apple-t2-wifi-*-any.pkg*'")
		except:
			print("An error occured when installing WiFi firmware.")
	elif apple_t2["wifi"] == "M1":
		try:
			print("Cloning patches from https://github.com/jamlam/mbp-16.1-linux-wifi")
			installation.arch_chroot("runuser nobody -s /bin/sh -c 'git clone https://github.com/jamlam/mbp-16.1-linux-wifi /usr/local/src/t2linux/mbp-16.1-linux-wifi'")
			print("Installing kernel build dependencies")
			installation.arch_chroot("pacman -S --needed --noconfirm bc kmod libelf pahole cpio perl tar xz xmlto python-sphinx python-sphinx_rtd_theme graphviz imagemagick git")
			print("Downloading kernel source")
			installation.arch_chroot("runuser nobody -s /bin/sh -c 'cd /usr/local/src/t2linux/mbp-16.1-linux-wifi && makepkg -o'")
			print("The custom kernel patches are ready in /usr/local/src/t2linux/mbp-16.1-linux-wifi for you to build later, by running `makepkg -ie` in `/usr/local/src/t2linux/mbp-16.1-linux-wifi` (this takes a few hours to compile). You will also need firmware from /usr/share/firmware in macOS (Read the WiFi guide at wiki.t2linux.org).")
		except:
			print("An error occured while preparing the kernel with M1 wifi patches.")
	else:
		print("Nothing is being done for WiFi.")

	# TODO: chown -r it to not nobody


	# nvram ro
	try:
		print('Setting nvram to remount at boot as readonly, as writing to it panics the t2 chip')
		with open(f"{installation.mountpoint}/etc/fstab", 'a') as fstab:
			fstab.write("\nefivarfs /sys/firmware/efi/efivars efivarfs ro,remount 0 0\n")
	except:
		print("Failed to set nvram to remount.")
# vim: autoindent tabstop=4 shiftwidth=4 noexpandtab number
