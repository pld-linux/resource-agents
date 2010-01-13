# TODO
# - docbook deps
# - avoid remote docbook.xsl include:
#  /usr/bin/xsltproc --xinclude http://docbook.sourceforge.net/release/xsl/current/manpages/docbook.xsl
# - sync with heartbeat.spec (if any)
%define		subver	rc2
%define		rel		0.1
Summary:	Reusable cluster resource scripts
Name:		resource-agents
Version:	1.0.2
Release:	0.%{subver}.%{rel}
License:	GPL v2+; LGPL v2.1+
Group:		Daemons
URL:		http://www.linux-ha.org/
Source0:	http://www.linux-ha.org/w/images/9/99/Resource-agents-%{version}-%{subver}.tar.bz2
# Source0-md5:	fe1ec605e57279f689d893f0c85bef2c
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cluster-glue-libs-devel
BuildRequires:	docbook-dtd44-xml
#BuildRequires:	docbook-dtds
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
Requires(post):	/sbin/chkconfig
Requires(preun):	/sbin/chkconfig
Requires:	ipvsadm
Requires:	perl-MailTools
Requires:	perl-Net-SSLeay
Requires:	perl-libwww-perl
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
%setup -q -n %{name}-%{version}-%{subver}

%build
%{__libtoolize}
%{__aclocal}
%{__autoheader}
%{__automake}
%{__autoconf}
%configure \
	--with-initdir=/etc/rc.d/init.d \
	--enable-fatal-warnings=yes \
	--docdir=%{_docdir}/%{name}-%{version}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

#install -d $RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d
#ln -s %{_sbindir}/ldirectord $RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d/ldirectord

mkdir $RPM_BUILD_ROOT/sbin
cd $RPM_BUILD_ROOT/sbin
ln -sf %{_sysconfdir}/rc.d/init.d/ldirectord rcldirectord

# Dont package static libs or compiled python
find $RPM_BUILD_ROOT -name '*.a' -type f -print0 | xargs -0 rm -f
find $RPM_BUILD_ROOT -name '*.la' -type f -print0 | xargs -0 rm -f
find $RPM_BUILD_ROOT -name '*.pyc' -type f -print0 | xargs -0 rm -f
find $RPM_BUILD_ROOT -name '*.pyo' -type f -print0 | xargs -0 rm -f

# Unset execute permissions from things that shouln't have it
find $RPM_BUILD_ROOT -name '.ocf-*' -type f -print0 | xargs -0 chmod a-x
find $RPM_BUILD_ROOT -name 'ocf-*'  -type f -print0 | xargs -0 chmod a-x
find $RPM_BUILD_ROOT -name '*.dtd'  -type f -print0 | xargs -0 chmod a-x
chmod 0755 $RPM_BUILD_ROOT%{_sbindir}/ocf-tester

%clean
rm -rf $RPM_BUILD_ROOT

%preun -n ldirectord
/sbin/chkconfig --del ldirectord

%postun -n ldirectord -p /sbin/ldconfig

%post -n ldirectord
/sbin/chkconfig --add ldirectord

%files
%defattr(644,root,root,755)
%doc AUTHORS doc/README.webapps
%doc %{_datadir}/%{name}/ra-api-1.dtd
%dir %{_prefix}/lib/ocf
%dir %{_prefix}/lib/ocf/resource.d
%{_prefix}/lib/ocf/resource.d/heartbeat
%attr(755,root,root) %{_sbindir}/ocf-tester
%attr(755,root,root) %{_sbindir}/sfex_init
%{_mandir}/man7/*.7*

# For compatability with pre-existing agents
%dir %{_libdir}/heartbeat
%{_libdir}/heartbeat/ocf-shellfuncs
%{_libdir}/heartbeat/ocf-returncodes
%dir %{_sysconfdir}/ha.d
%{_sysconfdir}/ha.d/shellfuncs

%{_libdir}/heartbeat/send_arp
%{_libdir}/heartbeat/sfex_daemon
%{_libdir}/heartbeat/findif

%files -n ldirectord
%defattr(644,root,root,755)
%doc ldirectord/ldirectord.cf
%config(noreplace) /etc/logrotate.d/ldirectord
%attr(754,root,root) /etc/rc.d/init.d/ldirectord
%dir %{_sysconfdir}/ha.d/resource.d
%{_sysconfdir}/ha.d/resource.d/ldirectord
%attr(755,root,root) %{_sbindir}/ldirectord
%attr(755,root,root) /sbin/rcldirectord
%{_mandir}/man8/ldirectord.8*
