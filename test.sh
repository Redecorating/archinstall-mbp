#!/bin/sh
set -e

name=ArchMBP-0.1

#mkdir mnt

dd if=/dev/zero of=${name}.iso bs=256M count=16

#parted -s ${name}.iso \
#mklabel gpt \
#mkpart EFI fat32 1MiB 49MiB \
#mkpart ${name} ext4 50MiB 2047MiB

sudo losetup -P loop100 ${name}.iso
#sudo mkfs.fat -F32 -n EFI /dev/loop100p1
#sudo mkfs.ext4 -L ${name} /dev/loop100p2

#sudo mount /dev/loop100p2 /mnt
#sudo mkdir /mnt/boot
#sudo mount /dev/loop100p1 /mnt/boot


