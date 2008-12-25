%define release 	%mkrel 2
%if %mdvver < 200900
%define _localstatedir /var
%endif
%define bt_dir		       %{_localstatedir}/lib/bittorrent
%define bt_datadir	       %{bt_dir}/data
%define bt_statedir	       %{bt_dir}/state

Summary: Tool for copying files from one machine to another
Name: bittorrent
Version: 5.2.2
Release: %release
Source0: http://download.bittorrent.com/dl/BitTorrent-%{version}.tar.gz
#gw init scripts from Fedora
Source1: btseed
Source2: bttrack
Source5: bittorrent-bash-completion-20050712.bz2
Patch5: BitTorrent-5.2.2-paths.patch
Patch6: bittorrent-5.0.7-default-download.patch
License: BitTorrent Open Source License
Group: Networking/File transfer
URL: http://bittorrent.com/
BuildRoot: %{_tmppath}/%{name}-buildroot
BuildArchitectures: noarch
%py_requires -d
BuildRequires: python-twisted-core
Requires: python-twisted-web
Requires(pre): rpm-helper
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(postun): rpm-helper


%description
BitTorrent is a tool for copying files from one machine to
another. FTP punishes sites for being popular. Since all uploading is
done from one place, a popular site needs big iron and big
bandwidth. With BitTorrent, clients automatically mirror files they
download, making the publisher's burden almost nothing.

%package gui
Summary: GUI versions of the BitTorrent file transfer tools
Group: Networking/File transfer
Requires: wxpython2.6
Requires: %name = %version
Conflicts: kdelibs-common <= 3.1.3
Requires(post):desktop-file-utils
Requires(postun):desktop-file-utils

%description gui
BitTorrent is a tool for copying files from one machine to
another. FTP punishes sites for being popular. Since all uploading is
done from one place, a popular site needs big iron and big
bandwidth. With BitTorrent, clients automatically mirror files they
download, making the publisher's burden almost nothing.

This package contains the graphical versions of the BitTorrent tools.

%prep
%setup -q -n BitTorrent-%version
%patch5 -p1 -b .paths
%patch6 -p1 -b .download

%build
python ./setup.py build

%install
rm -rf $RPM_BUILD_ROOT %name.lang
python ./setup.py install --root=$RPM_BUILD_ROOT

perl -p -i -e 's/env python2/env python/' $RPM_BUILD_ROOT%_bindir/*
mkdir -p %buildroot%_liconsdir %buildroot%_miconsdir
ln -s %_datadir/pixmaps/BitTorrent-%version/logo/bittorrent_icon_16.png  ${RPM_BUILD_ROOT}%{_miconsdir}/%{name}.png
ln -s %_datadir/pixmaps/BitTorrent-%version/logo/bittorrent_icon_32.png  ${RPM_BUILD_ROOT}%{_iconsdir}/%{name}.png
ln -s %_datadir/pixmaps/BitTorrent-%version/logo/bittorrent_icon_48.png  ${RPM_BUILD_ROOT}%{_liconsdir}/%{name}.png


install -m 755 -d $RPM_BUILD_ROOT%{_datadir}/applications/
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=BitTorrent
Comment=Download files with BitTorrent
Exec=%{_bindir}/%{name}
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
MimeType=application/x-bittorrent
Categories=GTK;X-MandrivaLinux-Internet-FileTransfer;Network;FileTransfer;P2P;
EOF

cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}-maketorrent.desktop << EOF
[Desktop Entry]
Name=BitTorrent Creator
Comment=Create BitTorrent metadata files
Exec=%{_bindir}/maketorrent
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=GTK;X-MandrivaLinux-Internet-FileTransfer;Network;FileTransfer;P2P;
EOF

mkdir -p $RPM_BUILD_ROOT%{_datadir}/mime-info
cat << EOF > $RPM_BUILD_ROOT%{_datadir}/mime-info/BitTorrent\ GUI.mime
application/x-bittorrent
	ext: torrent
EOF

mkdir -p %buildroot%_sysconfdir/bash_completion.d
bzcat %SOURCE5 > %buildroot%_sysconfdir/bash_completion.d/bittorrent

# Create options files for initscripts
mkdir -p %buildroot%{_sysconfdir}/sysconfig/
cat <<EOF >%buildroot%{_sysconfdir}/sysconfig/bittorrent
SEEDDIR=%{bt_datadir}
SEEDOPTS="--max_upload_rate 350 --display_interval 300"
SEEDLOG=/var/log/bittorrent/btseed.log
TRACKPORT=6969
TRACKDIR=%{bt_datadir}
TRACKSTATEFILE=%{bt_statedir}/bttrack
TRACKLOG=/var/log/bittorrent/bttrack.log
TRACKOPTS="--min_time_between_log_flushes 4.0 --show_names 1 --hupmonitor 1"
EOF

# Have the services' log files rotated
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d/
cat <<EOF >%{buildroot}%{_sysconfdir}/logrotate.d/bittorrent
/var/log/bittorrent/btseed.log {
					    notifempty
					    missingok
					    postrotate
						/sbin/service btseed condrestart 2>/dev/null >/dev/null || :
						endscript
}

/var/log/bittorrent/bttrack.log {
					     notifempty
					     missingok
					     postrotate
						/sbin/service bttrack condrestart 2>/dev/null >/dev/null || :
						endscript
}
EOF

# pidof doesn't find scripts with hyphenated names, so make some convenience links for initscripts
%{__ln_s} bittorrent-tracker %{buildroot}%{_bindir}/bttrack
%{__ln_s} launchmany-console %{buildroot}%{_bindir}/btseed
mkdir -p %{buildroot}%{bt_dir}
mkdir -p %{buildroot}%{bt_datadir}
mkdir -p %{buildroot}%{bt_statedir}
mkdir -p %{buildroot}/var/{run,log/bittorrent}

install -D -m 755 %SOURCE1 %{buildroot}%{_sysconfdir}/rc.d/init.d/btseed
install -D -m 755 %SOURCE2 %{buildroot}%{_sysconfdir}/rc.d/init.d/bttrack


%find_lang %name


%clean
rm -rf $RPM_BUILD_ROOT

%pre
%_pre_useradd torrent %{bt_dir} /sbin/nologin

%post
%_post_service btseed
%_post_service bttrack

%preun
%_preun_service btseed
%_preun_service bttrack

%postun
%_postun_userdel torrent


%if %mdkversion < 200900
%post gui
%{update_menus}
%update_desktop_database
%endif

%if %mdkversion < 200900
%postun gui
%{clean_menus}
%clean_desktop_database
%endif

%files -f %name.lang
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/bash_completion.d/*
%doc %_datadir/doc/%name-%version
%_bindir/btseed
%_bindir/bttrack
%_bindir/bittorrent-curses
%_bindir/bittorrent-console
%_bindir/maketorrent-console
%_bindir/launchmany-curses
%_bindir/launchmany-console
%_bindir/changetracker-console
%_bindir/torrentinfo-console
%_bindir/bittorrent-tracker
%py_puresitedir/BitTorrent*
%py_puresitedir/BTL
%py_puresitedir/khashmir
%py_puresitedir/Zeroconf*
%attr(-,torrent,torrent) %dir %{bt_dir}/
%attr(-,torrent,torrent) %dir %{bt_datadir}/
%attr(-,torrent,torrent) %dir %{bt_statedir}/
%attr(-,torrent,torrent) %dir /var/log/bittorrent/
%{_sysconfdir}/rc.d/init.d/btseed
%{_sysconfdir}/rc.d/init.d/bttrack
%config(noreplace) %{_sysconfdir}/logrotate.d/bittorrent
%config(noreplace) %{_sysconfdir}/sysconfig/bittorrent


%files gui
%defattr(-,root,root)
%doc README.txt
%_bindir/bittorrent
%_bindir/maketorrent
%_datadir/applications/mandriva*
%_datadir/mime-info/*
%_iconsdir/%{name}.png
%_miconsdir/%{name}.png
%_liconsdir/%{name}.png
%_datadir/pixmaps/BitTorrent-%version/



