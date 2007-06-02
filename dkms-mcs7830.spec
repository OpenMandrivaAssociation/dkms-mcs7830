%define module_name mcs7830
%define name dkms-%{module_name}
%define version 1.4
%define release %mkrel 2

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	DKMS-ready kernel-source for the MCS7830 usb Fast Ethernet adapter
License:	GPL
Source:		%{module_name}-%{version}.tar.bz2
Source1:	GPL-V2.bz2
Source2:	README-mcs7830.bz2
Source3:	AUTHORS-mcs7830.bz2
Url:		http://www.moschip.com/html/support.html
Group:		System/Kernel and hardware
Requires(pre):	dkms
Requires(post): dkms
Buildroot:	%{_tmppath}/%{name}-%{version}-root
Exclusivearch:	%{ix86} x86_64

%description
The USB to MAC Ethernet Controller is a unique solution to interface peripheral devices to Universal Serial Bus 2.0 (USB 2.0) and 10/100 Base -T Ethernet. This device has been specially designed to provide simple solution to communicate with Ethernet applications accomplished by its highly integrated functionality. It is ideal for LAN (Local Area Network) applications. It provides internal buffering to enable parallel operations from USB ports on host side and MAC ports on the Ethernet bus. It also provides serial interface for EEPROM storing device ID.

%prep
#%setup -q -n %{module_name}FC4Ver%{version}
%setup -q -n Linux_2.6_src

%build
bzip2 -dc %SOURCE1 > LICENSE
bzip2 -dc %SOURCE2 > README
bzip2 -dc %SOURCE3 > AUTHORS

%install
mkdir -p %{buildroot}/usr/src/%{module_name}-%{version}
cp -a * %{buildroot}/usr/src/%{module_name}-%{version}
cat > %{buildroot}/usr/src/%{module_name}-%{version}/dkms.conf <<EOF
PACKAGE_VERSION="%{version}-%{release}"

# Items below here should not have to change with each driver version
PACKAGE_NAME="%{module_name}"
MAKE[0]="cd \${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build ; make KERNEL_PATH=\${kernel_source_dir}"
CLEAN="cd \${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build ; make KERNEL_PATH=\${kernel_source_dir} clean"

BUILT_MODULE_NAME[0]="\$PACKAGE_NAME"
DEST_MODULE_LOCATION[0]="/kernel/3rdparty/%{module_name}/"

REMAKE_INITRD="no"
AUTOINSTALL=yes
POST_INSTALL="post-install"
POST_REMOVE="post-remove"
EOF

cat > %{buildroot}/usr/src/%{module_name}-%{version}/post-install <<EOF
grep '[^#]*%{module_name}' %{_sysconfdir}/modprobe.preload || echo %{module_name}>>%{_sysconfdir}/modprobe.preload
#grep '%{module_name}' %{_sysconfdir}/modprobe.conf || echo "options %{module_name} msg_level=0" >>%{_sysconfdir}/modprobe.conf
EOF
chmod +x %{buildroot}/usr/src/%{module_name}-%{version}/post-install

mkdir -p %{buildroot}%{_sysconfdir}/udev/rules.d/
cat > %{buildroot}%{_sysconfdir}/udev/rules.d/%{module_name}.rules <<EOF
KERNEL=="%{module_name}", SYMLINK="mcs7830", MODE="0666"
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
dkms add -m %{module_name} -v %{version} --rpm_safe_upgrade
dkms build -m %{module_name} -v %{version} --rpm_safe_upgrade
dkms install -m %{module_name} -v %{version} --rpm_safe_upgrade
#Load it now so that we don't need to wait until next reboot 
rmmod %{module_name} > /dev/null 2>&1
modprobe %{module_name}

%preun
if [ $1 = 0 ]
then
	sed -i '/%{module_name}/d' /etc/modprobe.preload
	sed -i '/%{module_name}/d' /etc/modprobe.conf
fi
dkms remove -m %{module_name} -v %{version} --rpm_safe_upgrade --all ||:

%files
%doc LICENSE README AUTHORS
%defattr(-,root,root)
%_usrsrc/%{module_name}-%{version}
%_sysconfdir/udev/rules.d/%{module_name}.rules
