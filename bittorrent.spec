%define bt_dir		       %{_localstatedir}/lib/bittorrent
%define bt_datadir	       %{bt_dir}/data
%define bt_statedir	       %{bt_dir}/state

Summary:	Tool for copying files from one machine to another
Name:		bittorrent
Version:	5.3
Release:	16
Group:		Networking/File transfer
License:	GPLv3+
Url:		http://bittorrent.com/
Source0:	http://download.bittorrent.com/dl/BitTorrent-%{version}-GPL.tar.gz
#gw init scripts from Fedora
Source1:	btseed
Source2:	bttrack
Patch5:		BitTorrent-5.2.2-paths.patch
Patch6:		bittorrent-5.0.7-default-download.patch
BuildArch: noarch
Requires:	python(abi) = 2.7
Requires:	python-twisted-web
BuildRequires:	pkgconfig(python2)
BuildRequires:	python-twisted-core
BuildRequires:	pythonegg(zope.interface)

Requires(pre,post,preun,postun): rpm-helper

%description
BitTorrent is a tool for copying files from one machine to
another. FTP punishes sites for being popular. Since all uploading is
done from one place, a popular site needs big iron and big
bandwidth. With BitTorrent, clients automatically mirror files they
download, making the publisher's burden almost nothing.

%prep
%setup -q -n BitTorrent-%version-GPL
tar xf BitTorrent_mainline_library_python.tar
mv python_bt_codebase_library/* .
tar xf BitTorrent_mainline_python.tar
mv python_bt_codebase/* .
%patch5 -p1 -b .paths
%patch6 -p1 -b .download

%build
python2 ./setup.py build

%install
rm -rf %{buildroot} %{name}.lang
python2 ./setup.py install --root=%{buildroot}

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

# AdamW 2008/12: bittorrent-gui doesn't work with wx 2.8 and has been
# generally superseded by other clients, so we're not going to package
# it any more. Transmission provides / obsoletes it. This deletes the
# GUI-only files.

rm -rf %{buildroot}%{_bindir}/bittorrent \
	%{buildroot}%{_bindir}/maketorrent \
	%{buildroot}%{_datadir}/pixmaps/BitTorrent-5.2.2/

#%%find_lang %{name}

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

%files 
#-f %{name}.lang
%doc %_datadir/doc/%{name}-5.2.2
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
%py2_puresitedir/BitTorrent*
%py2_puresitedir/BTL
%py2_puresitedir/khashmir
%py2_puresitedir/Zeroconf*
%attr(-,torrent,torrent) %dir %{bt_dir}/
%attr(-,torrent,torrent) %dir %{bt_datadir}/
%attr(-,torrent,torrent) %dir %{bt_statedir}/
%attr(-,torrent,torrent) %dir /var/log/bittorrent/
%{_sysconfdir}/rc.d/init.d/btseed
%{_sysconfdir}/rc.d/init.d/bttrack
%config(noreplace) %{_sysconfdir}/logrotate.d/bittorrent
%config(noreplace) %{_sysconfdir}/sysconfig/bittorrent
