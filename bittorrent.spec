%define release 	%mkrel 8
%if %mdvver < 200900
%define _localstatedir /var
%endif
%define bt_dir		       %{_localstatedir}/lib/bittorrent
%define bt_datadir	       %{bt_dir}/data
%define bt_statedir	       %{bt_dir}/state

Summary: Tool for copying files from one machine to another
Name: bittorrent
Version: 5.3
Release: %release
Source0: http://download.bittorrent.com/dl/BitTorrent-%{version}-GPL.tar.gz
#gw init scripts from Fedora
Source1: btseed
Source2: bttrack
Patch5: BitTorrent-5.2.2-paths.patch
Patch6: bittorrent-5.0.7-default-download.patch
License: GPLv3+
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

%prep
%setup -q -n BitTorrent-%version-GPL
tar xf BitTorrent_mainline_library_python.tar
mv python_bt_codebase_library/* .
tar xf BitTorrent_mainline_python.tar
mv python_bt_codebase/* .
%patch5 -p1 -b .paths
%patch6 -p1 -b .download

%build
python ./setup.py build

%install
rm -rf $RPM_BUILD_ROOT %name.lang
python ./setup.py install --root=$RPM_BUILD_ROOT

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
%doc %_datadir/doc/%name-5.2.2
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



%changelog
* Tue May 03 2011 Oden Eriksson <oeriksson@mandriva.com> 5.3-8mdv2011.0
+ Revision: 663324
- mass rebuild

* Sun Oct 31 2010 Funda Wang <fwang@mandriva.org> 5.3-7mdv2011.0
+ Revision: 590786
- rebuild for py2.7

* Tue Mar 16 2010 Oden Eriksson <oeriksson@mandriva.com> 5.3-6mdv2010.1
+ Revision: 522197
- rebuilt for 2010.1

* Sun Aug 09 2009 Oden Eriksson <oeriksson@mandriva.com> 5.3-5mdv2010.0
+ Revision: 413172
- rebuild

* Wed Mar 04 2009 Götz Waschk <waschk@mandriva.org> 5.3-4mdv2009.1
+ Revision: 348212
- new version
- update license

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - keep bash completion in its own package

* Sat Dec 27 2008 Adam Williamson <awilliamson@mandriva.org> 5.2.2-3mdv2009.1
+ Revision: 319993
- drop bittorrent-gui, it's not very good and won't work with wx 2.8

* Thu Dec 25 2008 Funda Wang <fwang@mandriva.org> 5.2.2-2mdv2009.1
+ Revision: 318991
- rediff paths patch
- rebuild for new python

* Tue Nov 25 2008 Götz Waschk <waschk@mandriva.org> 5.2.2-1mdv2009.1
+ Revision: 306571
- new version
- set localstatedir for backports
- don't use localstatedir for logs

* Thu Jul 17 2008 Götz Waschk <waschk@mandriva.org> 5.2.0-3mdv2009.0
+ Revision: 236710
- add services from Fedora (bug #41872)

* Thu Jun 12 2008 Pixel <pixel@mandriva.com> 5.2.0-2mdv2009.0
+ Revision: 218431
- rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Mon Feb 18 2008 Thierry Vignaud <tv@mandriva.org> 5.2.0-2mdv2008.1
+ Revision: 170777
- rebuild
- fix "foobar is blabla" summary (=> "blabla") so that it looks nice in rpmdrake
- drop old menu
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Tue Nov 20 2007 Götz Waschk <waschk@mandriva.org> 5.2.0-1mdv2008.1
+ Revision: 110698
- new version

* Fri Oct 19 2007 Götz Waschk <waschk@mandriva.org> 5.0.9-1mdv2008.1
+ Revision: 100309
- new version

  + Thierry Vignaud <tv@mandriva.org>
    - kill desktop-file-validate's 'warning: key "Encoding" in group "Desktop Entry" is deprecated'

* Tue Aug 14 2007 Götz Waschk <waschk@mandriva.org> 5.0.9-1mdv2008.0
+ Revision: 63226
- new version

* Wed Jul 18 2007 Götz Waschk <waschk@mandriva.org> 5.0.8-1mdv2008.0
+ Revision: 53240
- new version

* Thu May 10 2007 Götz Waschk <waschk@mandriva.org> 5.0.7-4mdv2008.0
+ Revision: 25896
- drop patch 0
- depend on wxpython2.6

* Wed Apr 18 2007 Götz Waschk <waschk@mandriva.org> 5.0.7-3mdv2008.0
+ Revision: 14759
- patch for wxpython 2.8


* Mon Mar 19 2007 Adam Williamson <awilliamson@mandriva.com> 5.0.7-3mdv2007.1
+ Revision: 146396
- update patch 6: default to ~/Desktop instead (per fcrozat)

* Mon Mar 19 2007 Adam Williamson <awilliamson@mandriva.com> 5.0.7-2mdv2007.1
+ Revision: 146389
- patch 6: use our Download directory, not Bittorrent's default (which doesn't exist and causes an error)

* Mon Mar 05 2007 Götz Waschk <waschk@mandriva.org> 5.0.7-1mdv2007.1
+ Revision: 132848
- new version

* Fri Mar 02 2007 Götz Waschk <waschk@mandriva.org> 5.0.6-1mdv2007.1
+ Revision: 131427
- new version

* Fri Jan 19 2007 Götz Waschk <waschk@mandriva.org> 5.0.5-1mdv2007.1
+ Revision: 110548
- new version

* Mon Jan 08 2007 Götz Waschk <waschk@mandriva.org> 5.0.4-1mdv2007.1
+ Revision: 105962
- new version
- switch to included icons

* Thu Dec 07 2006 Götz Waschk <waschk@mandriva.org> 5.0.3-1mdv2007.1
+ Revision: 91938
- new version

* Fri Dec 01 2006 Götz Waschk <waschk@mandriva.org> 5.0.2-1mdv2007.1
+ Revision: 89531
- new version
- remove installation workaround

* Thu Nov 30 2006 Götz Waschk <waschk@mandriva.org> 5.0.1-3mdv2007.1
+ Revision: 89254
- fix the postuninstall macro

* Thu Nov 30 2006 Götz Waschk <waschk@mandriva.org> 5.0.1-2mdv2007.1
+ Revision: 89238
- fix wrong pixmaps path

* Wed Nov 29 2006 Götz Waschk <waschk@mandriva.org> 5.0.1-1mdv2007.1
+ Revision: 88458
- new version
- drop patch 0
- update file list

* Thu Nov 02 2006 Götz Waschk <waschk@mandriva.org> 5.0.0-2mdv2007.1
+ Revision: 75179
- new version

* Sun Oct 29 2006 Götz Waschk <waschk@mandriva.org> 4.26.0-2mdv2007.1
+ Revision: 73598
- patch to fix bittorrent-curses (bug #26809)

* Sat Oct 14 2006 Götz Waschk <waschk@mandriva.org> 4.26.0-1mdv2007.1
+ Revision: 64488
- new version
- Import bittorrent

* Thu Oct 12 2006 Götz Waschk <waschk@mandriva.org> 4.24.2-1mdv2007.1
- update file list
- fix source URL
- new version

* Wed Aug 23 2006 Götz Waschk <waschk@mandriva.org> 4.20.9-1mdv2007.0
- New release 4.20.9

* Tue Aug 15 2006 Götz Waschk <waschk@mandriva.org> 4.20.8-2mdv2007.0
- fix buildrequires

* Tue Aug 15 2006 Götz Waschk <waschk@mandriva.org> 4.20.8-1mdv2007.0
- New release 4.20.8

* Fri Aug 04 2006 Götz Waschk <waschk@mandriva.org> 4.20.6-1mdv2007.0
- rediff patch 5
- New release 4.20.6

* Tue Jul 18 2006 Götz Waschk <waschk@mandriva.org> 4.20.4-1mdv2007.0
- update patch 5
- New release 4.20.4

* Sat Jul 01 2006 Götz Waschk <waschk@mandriva.org> 4.20.2-1mdv2007.0
- drop patch
- New release 4.20.2

* Fri Jun 30 2006 Götz Waschk <waschk@mandriva.org> 4.20.1-2mdv2007.0
- remove windows specific import

* Wed Jun 28 2006 Götz Waschk <waschk@mandriva.org> 4.20.1-1
- New release 4.20.1

* Thu Jun 22 2006 Götz Waschk <waschk@mandriva.org> 4.20.0-1
- New release 4.20.0

* Tue Jun 20 2006 Götz Waschk <waschk@mandriva.org> 4.9.9-2mdv2007.0
- xdg menu

* Thu Jun 15 2006 Götz Waschk <waschk@mandriva.org> 4.9.9-1
- New release 4.9.9

* Fri Jun 09 2006 Götz Waschk <waschk@mandriva.org> 4.9.8-1
- New release 4.9.8

* Sat Jun 03 2006 Götz Waschk <waschk@mandriva.org> 4.9.7-1mdv2007.0
- New release 4.9.7

* Fri May 26 2006 Götz Waschk <waschk@mandriva.org> 4.9.6-2mdv2007.0
- fix deps

* Thu May 25 2006 Götz Waschk <waschk@mandriva.org> 4.9.6-1mdk
- New release 4.9.6

* Thu May 11 2006 Götz Waschk <waschk@mandriva.org> 4.9.3-1mdk
- New release 4.9.3

* Mon May 08 2006 G?Waschk <waschk@mandriva.org> 4.9.2-3mdk
- fix deps

* Sat May 06 2006 G?Waschk <waschk@mandriva.org> 4.9.2-2mdk
- update deps
- add missing icon

* Sat May 06 2006 G?Waschk <waschk@mandriva.org> 4.9.2-1mdk
- update file list
- New release 4.9.2

* Tue Jan 31 2006 Götz Waschk <waschk@mandriva.org> 4.4.0-1mdk
- New release 4.4.0

* Wed Jan 25 2006 G?Waschk <waschk@mandriva.org> 4.3.6-1mdk
- noarch again
- New release 4.3.6

* Wed Jan 11 2006 Michael Scherer <misc@mandriva.org> 4.3.5-2mdk
- use the new python macro

* Mon Jan 09 2006 Götz Waschk <waschk@mandriva.org> 4.3.5-1mdk
- New release 4.3.5

* Sun Jan 01 2006 David Walluck <walluck@mandriva.org> 4.3.3-2mdk
- own %%_datadir/pixmaps/BitTorrent-%%version

* Wed Dec 21 2005 Götz Waschk <waschk@mandriva.org> 4.3.3-1mdk
- New release 4.3.3

* Mon Dec 12 2005 Götz Waschk <waschk@mandriva.org> 4.3.2-1mdk
- New release 4.3.2

* Tue Dec 06 2005 Götz Waschk <waschk@mandriva.org> 4.3.1-1mdk
- New release 4.3.1

* Mon Dec 05 2005 Götz Waschk <waschk@mandriva.org> 4.3.0-1mdk
- New release 4.3.0

* Sat Dec 03 2005 Götz Waschk <waschk@mandriva.org> 4.2.1-1mdk
- New release 4.2.1

* Wed Nov 23 2005 Götz Waschk <waschk@mandriva.org> 4.2.0-1mdk
- New release 4.2.0

* Fri Nov 18 2005 Götz Waschk <waschk@mandriva.org> 4.1.8-1mdk
- New release 4.1.8

* Thu Nov 03 2005 Götz Waschk <waschk@mandriva.org> 4.1.7-1mdk
- New release 4.1.7

* Fri Oct 14 2005 G?Waschk <waschk@mandriva.org> 4.1.6-1mdk
- drop patch 0
- drop obsolete man pages
- New release 4.1.6

* Sun Aug 28 2005 G?Waschk <waschk@mandriva.org> 4.1.4-5mdk
- rebuild

* Sat Aug 27 2005 G?Waschk <waschk@mandriva.org> 4.1.4-4mdk
- annoy the x86_64 maintainers back

* Sat Aug 27 2005 Götz Waschk <waschk@mandriva.org> 4.1.4-3mdk
- rebuild to replace lib64 by lib

* Fri Aug 26 2005 G?Waschk <waschk@mandriva.org> 4.1.4-2mdk
- remove pycrypto dependancy

* Thu Aug 25 2005 G?Waschk <waschk@mandriva.org> 4.1.4-1mdk
- update source 5
- update file list
- update the patch
- New release 4.1.4

* Tue Jul 19 2005 G?Waschk <waschk@mandriva.org> 4.1.3-1mdk
- New release 4.1.3

* Thu Jul 14 2005 G?Waschk <waschk@mandriva.org> 4.1.2-2mdk
- add Guillaume's bash-completion for bittorrent

* Sat Jun 11 2005 G?Waschk <waschk@mandriva.org> 4.1.2-1mdk
- rediff the patch
- New release 4.1.2

* Thu May 26 2005 G?Waschk <waschk@mandriva.org> 4.1.1-3mdk
- add translations (only french for now)
- New release 4.1.1

* Fri May 20 2005 G?Waschk <waschk@mandriva.org> 4.1.0-3mdk
- fix mkrel

* Fri May 20 2005 G?Waschk <waschk@mandriva.org> 4.1.0-2mdk
- mkrel

* Fri May 20 2005 G?Waschk <waschk@mandriva.org> 4.1.0-1mdk
- update file list
- New release 4.1.0

* Sun Apr 03 2005 Daouda LO <daouda@mandrakesoft.com> 4.0.1-1mdk
- new version
- tested with drakbt (#14500)
- 4.0.0 bugfixes:
  o fix mouse and keyboard freezes when downloading files 
  o fix settings/preferences not saved when quiting
  o fix bug on reading metainfo

* Tue Mar 08 2005 G?Waschk <waschk@linux-mandrake.com> 4.0.0-1mdk
- new version

* Wed Feb 16 2005 G?Waschk <waschk@linux-mandrake.com> 3.9.1-2mdk
- fix deps

* Sun Jan 23 2005 Goetz Waschk <waschk@linux-mandrake.com> 3.9.1-1mdk
- New release 3.9.1

* Tue Dec 28 2004 G?Waschk <waschk@linux-mandrake.com> 3.9.0-2mdk
- fix patch 5

* Tue Dec 21 2004 G?Waschk <waschk@linux-mandrake.com> 3.9.0-1mdk
- drop patches 1,2,3,4 don't apply anymore
- drop patch 0, must be updated!
- change license
- fix URL
- New release 3.9.0

* Sat Dec 04 2004 Michael Scherer <misc@mandrake.org> 3.4.2-7mdk
- Rebuild for new python

* Thu Sep 23 2004 G?Waschk <waschk@linux-mandrake.com> 3.4.2-6mdk
- make help appear in a friendly dialog (bug #8809)

* Mon Aug 16 2004 G?Waschk <waschk@linux-mandrake.com> 3.4.2-5mdk
- fix deps

* Sat Aug 14 2004 Laurent MONTEL <lmontel@mandrakesoft.com> 3.4.2-4mdk
- Rebuild for new menu

* Thu Jul 08 2004 G?Waschk <waschk@linux-mandrake.com> 3.4.2-3mdk
- update patch 3 for btcompletedirgui.py

* Thu Jul 08 2004 G?Waschk <waschk@linux-mandrake.com> 3.4.2-2mdk
- patch for new wxPythonGTK (J.A. Magallon), please test

* Tue Apr 06 2004 G?Waschk <waschk@linux-mandrake.com> 3.4.2-1mdk
- rediff patch 1
- new version

* Sat Apr 03 2004 G?Waschk <waschk@linux-mandrake.com> 3.4.1a-1mdk
- rediff patch 1
- new version

