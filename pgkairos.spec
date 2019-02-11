%define pkgname pgkairos
%define pkgversion pkgversion

Name:		%{pkgname}
Version:	%{pkgversion}
Release:	1%{?dist}
Summary:	PostgreSQL extension to collect run time statistics and export them to Kairos
Group:		Applications
License:	GPLv3
Requires:	python-psutil
Prefix:     /usr/local/share/postgresql/extension
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
mkdir -p $RPM_BUILD_ROOT%{prefix}
install -p -m 755 *.sql $RPM_BUILD_ROOT%{prefix}
install -p -m 755 *.control $RPM_BUILD_ROOT%{prefix}

%files
%defattr(-, root, root)
%{prefix}/%{name}.control
%{prefix}/%{name}--%{version}.sql

%changelog
