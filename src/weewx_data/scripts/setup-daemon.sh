#!/bin/sh
#
# Install files that integrate WeeWX into an operating system.
# This script must be run using sudo, or as root.
#
set -e

UTIL_ROOT=$HOME/weewx-data/util

if [ "$(id -u)" != "0" ]; then
  echo "This script requires admin privileges.  Use 'sudo' or run as root."
  exit 1
fi

ts=`date +"%Y%m%d%H%M%S"`

copy_file() {
    src=$1
    dst=$2
    if [ -f "$dst" ]; then
	mv ${dst} ${dst}.${ts}
    fi
    echo "Installing $dst"
    cp $src $dst
}

remove_file() {
    dst=$1
    if [ -f "$dst" ]; then
        echo "Removing $dst"
	rm $dst
    fi
}

install_udev() {
    if [ -d /etc/udev/rules.d ]; then
	copy_file $UTIL_ROOT/udev/rules.d/weewx.rules /etc/udev/rules.d/60-weewx.rules
	echo "    If you are using a device that is connected to the computer by USB or"
	echo "    serial port, unplug the device then plug it back in again to ensure that"
	echo "    permissions are applied correctly."
    fi
}

uninstall_udev() {
    remove_file /etc/udev/rules.d/60-weewx.rules
}

install_systemd() {
    copy_file $UTIL_ROOT/systemd/weewx.service /etc/systemd/system/weewx.service
    copy_file $UTIL_ROOT/systemd/weewx@.service /etc/systemd/system/weewx@.service

    echo "Reloading systemd"
    systemctl daemon-reload
    echo "Enabling weewx to start when system boots"
    systemctl enable weewx
        
    echo "You can start/stop weewx with the following commands:"
    echo "  \033[1msudo systemctl start weewx\033[0m"
    echo "  \033[1msudo systemctl stop weewx\033[0m"
}

uninstall_systemd() {
    echo "Stopping weewx"
    systemctl stop weewx
    echo "Disabling weewx"
    systemctl disable weewx
    remove_file /etc/systemd/system/weewx@.service
    remove_file /etc/systemd/system/weewx.service
}

install_sysv() {
    if [ -d /etc/default ]; then
        copy_file $UTIL_ROOT/default/weewx /etc/default/weewx
    fi
    copy_file $UTIL_ROOT/init.d/weewx-multi /etc/init.d/weewx
    chmod 755 /etc/init.d/weewx

    echo "Enabling weewx to start when system boots"
    update-rc.d weewx defaults

    echo "You can start/stop weewx with the following commands:"
    echo "  \033[1m/etc/init.d/weewx start\033[0m"
    echo "  \033[1m/etc/init.d/weewx stop\033[0m"
}

uninstall_sysv() {
    echo "Stopping weewx"
    /etc/init.d/weewx stop
    echo "Disabling weewx"
    update-rc.d weewx remove
    remove_file /etc/init.d/weewx
    remove_file /etc/default/weewx
}

install_bsd() {
    if [ -d /etc/defaults ]; then
        copy_file $UTIL_ROOT/default/weewx /etc/defaults/weewx.conf
    fi
    copy_file $UTIL_ROOT/init.d/weewx.bsd /usr/local/etc/rc.d/weewx
    chmod 755 /usr/local/etc/rc.d/weewx

    echo "Enabling weewx to start when system boots"
    sysrc weewx_enable="YES"

    echo "You can start/stop weewx with the following commands:"
    echo "  \033[1msudo service weewx start\033[0m"
    echo "  \033[1msudo service weewx stop\033[0m"
}

uninstall_bsd() {
    echo "Stopping weewx..."
    service weewx stop
    echo "Disabling weewx..."
    sysrc weewx_enable="NO"
    remove_file /usr/local/etc/rc.d/weewx
    remove_file /etc/defaults/weewx.conf
}

install_macos() {
    copy_file $UTIL_ROOT/launchd/com.weewx.weewxd.plist /Library/LaunchDaemons

    echo "You can start/stop weewx with the following commands:"
    echo "  \033[1msudo launchctl load /Library/LaunchDaemons/com.weewx.weewxd.plist\033[0m"
    echo "  \033[1msudo launchctl unload /Library/LaunchDaemons/com.weewx.weewxd.plist\033[0m"
}

uninstall_macos() {
    echo "Stopping weewx"
    launchctl unload /Library/LaunchDaemons/com.weewx.weewxd.plist
    remove_file /Library/LaunchDaemons/com.weewx.weewxd.plist
}


do_install() {
    init_system=$1
    echo "Set up the files necessary to run WeeWX at system startup."

    if [ ! -d $UTIL_ROOT ]; then
        echo "Cannot find utility files at location '$UTIL_ROOT'"
        exit 1
    fi

    echo "Copying files from $UTIL_ROOT"

    if [ -d /usr/local/etc/rc.d ]; then
        install_bsd
    elif [ "$init_system" = "/sbin/launchd" ]; then
        install_macos
    elif [ "$init_system" = "systemd" ]; then
        install_udev
        install_systemd
    elif [ "$init_system" = "init" ]; then
        install_udev
        install_sysv
    else
        echo "Unrecognized platform with init system $init_system"
    fi
}

do_uninstall() {
    init_system=$1
    echo "Remove the files for running WeeWX at system startup."

    if [ -d /usr/local/etc/rc.d ]; then
        uninstall_bsd
    elif [ "$init_system" = "/sbin/launchd" ]; then
        uninstall_macos
    elif [ "$init_system" = "systemd" ]; then
        uninstall_systemd
        uninstall_udev
    elif [ "$init_system" = "init" ]; then
        uninstall_sysv
        uninstall_udev
    else
        echo "Unrecognized platform with init system $init_system"
    fi
}

pid1=$(ps -p 1 -o comm=)
ACTION=$1
if [ "$ACTION" = "" -o "$ACTION" = "install" ]; then
    do_install $pid1
elif [ "$ACTION" = "uninstall" ]; then
    do_uninstall $pid1
fi
