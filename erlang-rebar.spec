
%bcond_with	bootstrap	# bootstrap build
%bcond_with	tests		# build without tests

Summary:	Erlang Build Tools
Name:		erlang-rebar
Version:	2.6.4
Release:	1
License:	MIT
Group:		Development/Tools
Source0:	https://github.com/rebar/rebar/tarball/%{version}/rebar-%{version}.tar.bz2
# Source0-md5:	d5083a6bcb0df31e809d5bb0d6be502e
Source1:	rebar.escript
URL:		https://github.com/rebar/rebar
BuildRequires:	erlang >= 2:17
%if %{without bootstrap}
BuildRequires:	erlang-rebar
%endif
BuildRequires:	rpmbuild(macros) >= 2.035
%{?erlang_requires}
Provides:	rebar = %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Erlang Build Tools.

%prep
%setup -qc
mv rebar-rebar-*/* .
%{__rm} -r rebar-rebar-*

%{__sed} -i -e '1s,/usr/bin/env escript,/usr/bin/escript,' \
	priv/templates/simplenode.install_upgrade.escript \
	priv/templates/simplenode.nodetool

%build
%if %{with bootstrap}
./bootstrap
./rebar compile -v
%else
rebar compile -v
install %{SOURCE1} ./rebar
%endif

%if %{with tests}
./rebar eunit -v
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir} \
	$RPM_BUILD_ROOT%{_libdir}/erlang/lib/rebar-%{version}/{ebin,include}

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/rebar
cp -p ebin/rebar.app $RPM_BUILD_ROOT%{_libdir}/erlang/lib/rebar-%{version}/ebin
cp -p ebin/*.beam $RPM_BUILD_ROOT%{_libdir}/erlang/lib/rebar-%{version}/ebin
cp -p include/*.hrl $RPM_BUILD_ROOT%{_libdir}/erlang/lib/rebar-%{version}/include
cp -a priv $RPM_BUILD_ROOT%{_libdir}/erlang/lib/rebar-%{version}

%files
%defattr(644,root,root,755)
%doc LICENSE README.md THANKS rebar.config.sample
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/rebar
%{_libdir}/erlang/lib/rebar-%{version}

%clean
rm -rf $RPM_BUILD_ROOT
