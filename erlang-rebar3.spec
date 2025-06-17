
%bcond_with	bootstrap	# bootstrap build
%bcond_with	tests		# build without tests

Summary:	Erlang Build Tools
Name:		erlang-rebar3
Version:	3.25.0
Release:	0.1
License:	MIT
Group:		Development/Tools
Source0:	https://github.com/erlang/rebar3/tarball/%{version}/rebar3-%{version}.tar.bz2
# Source0-md5:	c4a5482c66a7a5503048ae3b3b6e6ec4
Source1:	rebar3.escript
URL:		https://github.com/erlang/rebar3
BuildRequires:	erlang >= 2:17
%if %{without bootstrap}
BuildRequires:	erlang-rebar3
%endif
BuildRequires:	rpmbuild(macros) >= 2.035
%{?erlang_requires}
Provides:	rebar = %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_enable_debug_packages	0

%description
Erlang Build Tools.

%prep
%setup -qc
mv erlang-rebar3-*/* .
%{__rm} -r erlang-rebar3-*

%{__sed} -i -e '1s,/usr/bin/env escript,/usr/bin/escript,' \
	vendor/relx/priv/templates/install_upgrade_escript \
	vendor/relx/priv/templates/nodetool

%build
ebin_paths=$(perl -e 'print join(":", grep { !/rebar/} (glob("%{_libdir}/erlang/lib/*/ebin"), glob("%{_datadir}/erlang/lib/*/ebin")))')

%if %{with bootstrap}
#DIAGNOSTIC=1 \
./bootstrap bare compile --paths $ebin_paths --separator :
%else
rm -rf vendor
#DIAGNOSTIC=1 \
rebar3 bare compile --paths $ebin_paths --separator :
install %{SOURCE1} ./rebar3
%endif

%if %{with tests}
./rebar3 eunit -v
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir} \
	$RPM_BUILD_ROOT%{_libdir}/erlang/lib/rebar3-%{version}/ebin

%if %{with bootstrap}
    ldir=bootstrap
%else
    ldir=prod
%endif

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/rebar3
cp -p _build/${ldir}/lib/rebar/ebin/rebar.app $RPM_BUILD_ROOT%{_libdir}/erlang/lib/rebar3-%{version}/ebin
cp -p _build/${ldir}/lib/rebar/ebin/*.beam $RPM_BUILD_ROOT%{_libdir}/erlang/lib/rebar3-%{version}/ebin
cp -a apps/rebar/priv $RPM_BUILD_ROOT%{_libdir}/erlang/lib/rebar3-%{version}

# should be packaged as separate packages
for v in bbmustache certifi cf cth_readable erlware_commons eunit_formatters getopt providers relx ssl_verify_fun; do
	ver=$(sed -nE 's/.*<<"version">>,<<"([^"]*)">>.*/\1/p' vendor/$v/hex_metadata.config)
	n=${v}-${ver}
	install -d $RPM_BUILD_ROOT%{_libdir}/erlang/lib/${n}/
	for f in _build/${ldir}/lib/${v}/*; do
		# remove broken symlinks
		[ -L "$f" ] && [ ! -e "$f" ] && rm "$f"
	done

	cp -rpL _build/${ldir}/lib/${v}/* $RPM_BUILD_ROOT%{_libdir}/erlang/lib/${n}
done

%files
%defattr(644,root,root,755)
%doc LICENSE README.md THANKS rebar.config.sample
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/rebar3
%{_libdir}/erlang/lib/*-*

%clean
rm -rf $RPM_BUILD_ROOT
