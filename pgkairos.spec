%define pkgname pgkairos
%define pkgversion 1.0

Name:		%{pkgname}
Version:	%{pkgversion}
Release:	1%{?dist}
Summary:	PostgreSQL extension to collect run time statistics and export them to Kairos
Group:		Applications
License:	GPLv3
Requires:	postgresql96-server postgresql96-plpython python-psutil
Source0:	%{name}-%{version}.tar.gz

%description
Collect of statistics through a PostgreSQL extension.

Features include:
* Collect of statistics from pg_stat_database dynamic table (function snap())
* Collect of statistics from pg_stat_statistic dynamic table (function snap_detailed())
* Collect of statistics at system level through python psutil (function snap_system ())
* Purge of statistics older than a parametrized value (function purge())
* Export of statistics to Kairos system (function export())

%prep
pwd
%setup -q -n %{name}-%{version}

%build

%install
mkdir -p $RPM_BUILD_ROOT/usr/pgsql-9.6/share/extension
install -p -m 755 *.sql $RPM_BUILD_ROOT/usr/pgsql-9.6/share/extension
install -p -m 755 *.control $RPM_BUILD_ROOT/usr/pgsql-9.6/share/extension

%files
%defattr(-, root, root)
/usr/pgsql-9.6/share/extension/%{name}.control
/usr/pgsql-9.6/share/extension/%{name}--%{version}.sql

%changelog
