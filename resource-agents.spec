%bcond_without	systemd	# systemd
Summary:	Reusable cluster resource scripts
Summary(pl.UTF-8):	Skrypty wielokrotnego użytku do obsługi zasobów klastrowych
Name:		resource-agents
Version:	4.14.0
Release:	1
License:	GPL v2+, LGPL v2.1+
Group:		Daemons
#Source0Download: https://github.com/ClusterLabs/resource-agents/releases
Source0:	https://github.com/ClusterLabs/resource-agents/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	0f48ab395633d2a92a31a54b7b0c018d
Source1:	ldirectord.init
Source2:	%{name}.tmpfiles
Patch0:		%{name}-types.patch
Patch1:		%{name}-bash.patch
Patch2:		%{name}-ac.patch
URL:		https://github.com/ClusterLabs/resource-agents
BuildRequires:	autoconf >= 2.63
BuildRequires:	automake >= 1:1.10.1
BuildRequires:	cluster-glue-libs-devel
BuildRequires:	docbook-dtd44-xml
BuildRequires:	docbook-style-xsl
BuildRequires:	glib2-devel >= 2.0
BuildRequires:	libnet-devel >= 1.0
BuildRequires:	libqb-devel
BuildRequires:	libxslt-progs
BuildRequires:	openssl-tools
BuildRequires:	perl-tools-pod
BuildRequires:	pkgconfig >= 1:0.18
BuildRequires:	python3-devel
BuildRequires:	rpm-perlprov
BuildRequires:	sed >= 4.0
%{?with_systemd:BuildRequires:	systemd-devel}
BuildRequires:	which
Requires:	cluster-glue
Requires:	python3
Obsoletes:	heartbeat-resources < 3.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Scripts to allow common services to operate in a High Availability
environment.

%description -l pl.UTF-8
Skrypty pozwalające na działanie popularnych usług w środowisku
wysokiej dostępności (High Availability).

%package devel
Summary:	Resource Agents header file
Summary(pl.UTF-8):	Plik nagłówkowy Resource Agents
Group:		Development/Libraries
# doesn't require base
Conflicts:	resource-agents < 4.1.1

%description devel
Resource Agents header file.

%description devel -l pl.UTF-8
Plik nagłówkowy Resource Agents.

%package -n ldirectord
Summary:	A Monitoring Daemon for Maintaining High Availability Resources
Summary(pl.UTF-8):	Demon monitorujący do utrzymywania zasobów z wysoką dostępnością
License:	GPL v2+
Group:		Applications/System
Requires(post,preun):	/sbin/chkconfig
Requires:	ipvsadm
Requires:	rc-scripts
Provides:	heartbeat-ldirectord
Obsoletes:	heartbeat-ldirectord < 3.0

%description -n ldirectord
The Linux Director Daemon (ldirectord) is a stand alone daemon for
monitoring the services on real servers. Currently, HTTP, HTTPS, and
FTP services are supported. ldirectord is simple to install and works
with Pacemaker.

%description -n ldirectord -l pl.UTF-8
Demon Linux Director (ldirectord) to samodzielny demon do
monitorowania usług na rzeczywistych serwerach. Obecnie obsługiwane są
usługi HTTP, HTTPS i FTP. ldirectord jest prosty do zainstalowania i
współpracuje z Pacemakerem.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
# with strict alasing tools/tickle_tcp.c emits "maybe uninitialized" warnings
CFLAGS="%{rpmcflags} -fno-strict-aliasing"
%configure \
	FSCK=/sbin/fsck \
	FUSER=/bin/fuser \
	IPTABLES=%{_sbindir}/iptables \
	MAILCMD=/bin/mail \
	MOUNT=/bin/mount \
	PING=/bin/ping \
	PYTHON="%{__python3}" \
	--docdir=%{_docdir}/%{name}-%{version} \
	--enable-fatal-warnings \
	--with-initdir=/etc/rc.d/init.d \
	--with-ocf-root=%{_prefix}/lib/ocf \
	--with-ras-set=all \
	--with-systemdsystemunitdir=%{systemdunitdir}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d \
	$RPM_BUILD_ROOT%{systemdtmpfilesdir}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# in doc
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/ra-api-1.dtd

%{__rm} $RPM_BUILD_ROOT/etc/rc.d/init.d/ldirectord
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ldirectord
cp -a ldirectord/ldirectord.cf $RPM_BUILD_ROOT%{_sysconfdir}/ha.d
install %{SOURCE2} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf

# Unset execute permissions from things that shouln't have it
find $RPM_BUILD_ROOT%{_datadir} -name 'ocf-*'  -type f -print0 | xargs -0 chmod a-x

%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

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
%doc AUTHORS ChangeLog doc/README.webapps heartbeat/ra-api-1.dtd
%attr(755,root,root) %{_sbindir}/ocf-tester
%attr(755,root,root) %{_sbindir}/ocft
%attr(755,root,root) %{_sbindir}/sfex_init
%attr(755,root,root) %{_sbindir}/sfex_stat
%attr(755,root,root) %{_sbindir}/rhev-check.sh

%dir %{_sysconfdir}/ha.d
%dir %{_sysconfdir}/ha.d/resource.d
%{_sysconfdir}/ha.d/shellfuncs

%attr(755,root,root) %{_libexecdir}/heartbeat/send_arp
%attr(755,root,root) %{_libexecdir}/heartbeat/send_ua
%attr(755,root,root) %{_libexecdir}/heartbeat/sfex_daemon
%attr(755,root,root) %{_libexecdir}/heartbeat/findif
%attr(755,root,root) %{_libexecdir}/heartbeat/storage_mon
%attr(755,root,root) %{_libexecdir}/heartbeat/tickle_tcp

%dir %{_prefix}/lib/ocf
%dir %{_prefix}/lib/ocf/lib
%dir %{_prefix}/lib/ocf/lib/heartbeat
%{_prefix}/lib/ocf/lib/heartbeat/ocf-*
%{_prefix}/lib/ocf/lib/heartbeat/ocf.py
%{_prefix}/lib/ocf/lib/heartbeat/*.sh
%dir %{_prefix}/lib/ocf/resource.d
%dir %{_prefix}/lib/ocf/resource.d/heartbeat
%{_prefix}/lib/ocf/resource.d/heartbeat/.ocf-*
%attr(755,root,root) %{_prefix}/lib/ocf/resource.d/heartbeat/*
%{_prefix}/lib/ocf/resource.d/redhat

%dir %{_datadir}/cluster
%{_datadir}/cluster/*.metadata
%attr(755,root,root) %{_datadir}/cluster/*.sh
%{_datadir}/cluster/SAP*
%{_datadir}/cluster/svclib_nfslock
%{_datadir}/cluster/ocf-shellfuncs
%dir %{_datadir}/cluster/relaxng
%{_datadir}/cluster/relaxng/*
%dir %{_datadir}/cluster/utils
%attr(755,root,root) %{_datadir}/cluster/utils/*

%{_datadir}/resource-agents

%if %{with systemd}
%{systemdunitdir}/resource-agents-deps.target
%endif

%attr(1755,root,root) /var/run/resource-agents
%{systemdtmpfilesdir}/%{name}.conf

%{_mandir}/man7/ocf_heartbeat_*.7*
%{_mandir}/man8/ocf-tester.8*
%{_mandir}/man8/sfex_init.8*

%files devel
%defattr(644,root,root,755)
%{_includedir}/heartbeat/agent_config.h
%{_npkgconfigdir}/resource-agents.pc

%files -n ldirectord
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ha.d/ldirectord.cf
%attr(755,root,root) %{_sysconfdir}/ha.d/resource.d/ldirectord
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/ldirectord
%attr(754,root,root) /etc/rc.d/init.d/ldirectord
%if %{with systemd}
%{systemdunitdir}/ldirectord.service
%endif
%attr(755,root,root) %{_sbindir}/ldirectord
%{_mandir}/man8/ldirectord.8*
