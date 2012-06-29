%define		gitrel	b735277
Summary:	Reusable cluster resource scripts
Name:		resource-agents
Version:	3.9.2
Release:	1
License:	GPL v2+; LGPL v2.1+
Group:		Daemons
URL:		http://www.linux-ha.org/
Source0:	https://github.com/ClusterLabs/resource-agents/tarball/v3.9.2
# Source0-md5:	3b5790e8041f2a459d8a0ff310682bfe
Source1:	ldirectord.init
Source2:	%{name}.tmpfiles
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cluster-glue-libs-devel
BuildRequires:	docbook-dtd44-xml
BuildRequires:	docbook-style-xsl
BuildRequires:	glib2-devel
BuildRequires:	libtool
BuildRequires:	libxslt-progs
BuildRequires:	openssl-tools
BuildRequires:	pkgconfig
BuildRequires:	python-devel
BuildRequires:	which
Obsoletes:	heartbeat-resources < 3.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Scripts to allow common services to operate in a High Availability
environment.

%package -n ldirectord
Summary:	A Monitoring Daemon for Maintaining High Availability Resources
License:	GPL v2+
Group:		Applications/System
Requires(post,preun):	/sbin/chkconfig
Requires:	ipvsadm
Requires:	perl-MailTools
Requires:	perl-Net-SSLeay
Requires:	perl-Socket6
Requires:	perl-libwww
Requires:	rc-scripts
Provides:	heartbeat-ldirectord
Obsoletes:	heartbeat-ldirectord

%description -n ldirectord
The Linux Director Daemon (ldirectord) was written by Jacob Rief.
<jacob.rief@tiscover.com>

ldirectord is a stand alone daemon for monitoring the services on real
servers. Currently, HTTP, HTTPS, and FTP services are supported.
lditrecord is simple to install and works with the heartbeat code
(http://www.linux-ha.org/).

See 'ldirectord -h' and linux-ha/doc/ldirectord for more information.

%prep
%setup -q -n ClusterLabs-%{name}-%{gitrel}

%build
%{__libtoolize}
%{__aclocal}
%{__autoheader}
%{__automake}
%{__autoconf}
%configure \
	FSCK=/sbin/fsck \
	FUSER=/bin/fuser \
	IPTABLES=%{_sbindir}/iptables \
	MAILCMD=/bin/mail \
	MOUNT=/bin/mount \
	PING=/bin/ping \
	--with-initdir=/etc/rc.d/init.d \
	--enable-fatal-warnings=yes \
	--docdir=%{_docdir}/%{name}-%{version}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d \
	$RPM_BUILD_ROOT%{systemdtmpfilesdir}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# in doc
rm $RPM_BUILD_ROOT%{_datadir}/%{name}/ra-api-1.dtd

rm -f $RPM_BUILD_ROOT/etc/rc.d/init.d/ldirectord
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ldirectord
cp -a ldirectord/ldirectord.cf $RPM_BUILD_ROOT%{_sysconfdir}/ha.d
install %{SOURCE2} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf

# Dont package static libs or compiled python
find $RPM_BUILD_ROOT -name '*.a' -type f -print0 | xargs -0 rm -f
find $RPM_BUILD_ROOT -name '*.la' -type f -print0 | xargs -0 rm -f
find $RPM_BUILD_ROOT -name '*.pyc' -type f -print0 | xargs -0 rm -f
find $RPM_BUILD_ROOT -name '*.pyo' -type f -print0 | xargs -0 rm -f

# Unset execute permissions from things that shouln't have it
find $RPM_BUILD_ROOT -name 'ocf-*'  -type f -print0 | xargs -0 chmod a-x
chmod a+rx $RPM_BUILD_ROOT%{_sbindir}/ocf-tester

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n ldirectord
/sbin/chkconfig --add ldirectord
%service ldirectord restart

%preun	-n ldirectord
if [ "$1" = "0" ]; then
	%service -q ldirectord stop
	/sbin/chkconfig --del ldirectord
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS doc/README.webapps heartbeat/ra-api-1.dtd
%attr(755,root,root) %{_libdir}/heartbeat/send_arp
%attr(755,root,root) %{_libdir}/heartbeat/sfex_daemon
%attr(755,root,root) %{_libdir}/heartbeat/findif
%attr(755,root,root) %{_libdir}/heartbeat/tickle_tcp
%{_datadir}/resource-agents
%attr(755,root,root) %{_sbindir}/ocf-tester
%attr(755,root,root) %{_sbindir}/ocft
%attr(755,root,root) %{_sbindir}/sfex_init
%attr(755,root,root) %{_sbindir}/sfex_stat
%attr(755,root,root) %{_sbindir}/rhev-check.sh
%{_sysconfdir}/ha.d/shellfuncs
%{_includedir}/heartbeat/agent_config.h
%attr(1755,root,root) /var/run/resource-agents
%dir %{_datadir}/cluster
%dir %{_datadir}/cluster/utils
%dir %{_datadir}/cluster/relaxng
%dir %{_prefix}/lib/ocf
%dir %{_prefix}/lib/ocf/resource.d
%dir %{_prefix}/lib/ocf/resource.d/heartbeat
%dir %{_prefix}/lib/ocf/lib
%dir %{_prefix}/lib/ocf/lib/heartbeat
%attr(755,root,root) %{_prefix}/lib/ocf/resource.d/heartbeat/*
%attr(755,root,root) %{_datadir}/cluster/*.sh
%{_datadir}/cluster/*.metadata
%{_datadir}/cluster/SAP*
%{_datadir}/cluster/svclib_nfslock
%{_datadir}/cluster/ocf-shellfuncs
%{_datadir}/cluster/relaxng/*
%attr(755,root,root) %{_datadir}/cluster/utils/*
%{_prefix}/lib/ocf/resource.d/heartbeat/.ocf-*
%{_prefix}/lib/ocf/lib/heartbeat/ocf-*
%{_prefix}/lib/ocf/resource.d/redhat
%{_mandir}/man7/*.7*
%{_mandir}/man8/ocf-tester.8*
%{_mandir}/man8/sfex_init.8*
%{systemdtmpfilesdir}/%{name}.conf


%files -n ldirectord
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ha.d/ldirectord.cf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/ldirectord
%attr(755,root,root) %{_sysconfdir}/ha.d/resource.d/ldirectord
%attr(754,root,root) /etc/rc.d/init.d/ldirectord
%attr(755,root,root) %{_sbindir}/*ldirectord*
%{_mandir}/man8/*ldirectord*.8*
