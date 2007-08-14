%define release 	%mkrel 1
#fixed2
%{?!mkrel:%define mkrel(c:) %{-c: 0.%{-c*}.}%{!?_with_unstable:%(perl -e '$_="%{1}";m/(.\*\\D\+)?(\\d+)$/;$rel=${2}-1;re;print "$1$rel";').%{?subrel:%subrel}%{!?subrel:1}.%{?distversion:%distversion}%{?!distversion:%(echo $[%{mdkversion}/10])}}%{?_with_unstable:%{1}}%{?distsuffix:%distsuffix}%{?!distsuffix:mdk}}
#gw for backports
%{?!py_puresitedir:%define py_puresitedir %_libdir/python%pyver/site-packages}

Summary: BitTorrent is a tool for copying files from one machine to another
Name: bittorrent
Version: 5.0.9
Release: %release
Source0: http://download.bittorrent.com/dl/BitTorrent-%{version}.tar.bz2
Source5: bittorrent-bash-completion-20050712.bz2
Patch5: BitTorrent-4.20.6-paths.patch
Patch6: bittorrent-5.0.7-default-download.patch
License: BitTorrent Open Source License
Group: Networking/File transfer
URL: http://bittorrent.com/
BuildRoot: %{_tmppath}/%{name}-buildroot
BuildArchitectures: noarch
BuildRequires: python-devel
BuildRequires: python-twisted-core
Requires: python
Requires: python-twisted-web


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

mkdir -p $RPM_BUILD_ROOT%{_menudir}
cat << EOF >  $RPM_BUILD_ROOT%{_menudir}/%{name}-gui
?package(bittorrent-gui): needs="x11" section="Internet/File Transfer" command="bittorrent" mimetypes="application/x-bittorrent" accept_url="false" multiple_files="true" title="BitTorrent" longtitle="Download files with BitTorrent" icon="%name.png" xdg="true"
?package(bittorrent-gui): needs="x11" section="Internet/File Transfer" command="maketorrent" title="BitTorrent Creator" longtitle="Create BitTorrent metadata files"  icon="%name.png" xdg="true"
EOF

install -m 755 -d $RPM_BUILD_ROOT%{_datadir}/applications/
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
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
Encoding=UTF-8
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

%find_lang %name


%clean
rm -rf $RPM_BUILD_ROOT


%post gui
%{update_menus}
%update_desktop_database

%postun gui
%{clean_menus}
%clean_desktop_database

%files -f %name.lang
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/bash_completion.d/*
%doc %_datadir/doc/%name-%version
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

%files gui
%defattr(-,root,root)
%doc README.txt
%_bindir/bittorrent
%_bindir/maketorrent
%_menudir/*
%_datadir/applications/mandriva*
%_datadir/mime-info/*
%_iconsdir/%{name}.png
%_miconsdir/%{name}.png
%_liconsdir/%{name}.png
%_datadir/pixmaps/BitTorrent-%version/



