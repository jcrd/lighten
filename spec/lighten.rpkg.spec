Name: {{{ git_cwd_name name="lighten" }}}
Version: {{{ git_cwd_version lead="$(git tag | sed -n 's/^v//p' | sort --version-sort -r | head -n1)" }}}
Release: 1%{?dist}
Summary: Intelligent monitor brightness control utility

License: MIT
URL: https://github.com/jcrd/lighten
VCS: {{{ git_cwd_vcs }}}
Source0: {{{ git_cwd_pack }}}

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
{{{ git_cwd_setup_macro }}}

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
{{{ git_cwd_changelog }}}
