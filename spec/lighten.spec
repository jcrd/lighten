Name: lighten
Version: 0.1.0
Release: 1%{?dist}
Summary: Intelligent monitor brightness control utility

License: MIT
URL: https://github.com/jcrd/lighten
Source0: https://github.com/jcrd/lighten/archive/v0.1.0.tar.gz

Requires: ddcutil
Requires: gdbm
Requires: python3-gobject
Requires: python3-hid

BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)

%global debug_package %{nil}

%description
Intelligent monitor brightness control utility.

%prep
%setup

%build
%py3_build

%install
%py3_install
mkdir -p %{buildroot}/usr/lib/systemd/user
cp -a systemd/lightend.service %{buildroot}/usr/lib/systemd/user

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/%{name}
%{python3_sitelib}/%{name}d
%{python3_sitelib}/%{name}-*.egg-info/
%{_bindir}/lighten
%{_bindir}/lightend
/usr/lib/systemd/user/lightend.service

%changelog
* Sun Sep  4 2022 James Reed <james@twiddlingbits.net> - 0.1.0-1
- Initial release
