%{?_javapackages_macros:%_javapackages_macros}
Name:          spatial4j
Version:       0.4.1
Release:       2.2
Summary:       A Geospatial Library for Java
Group:		Development/Java
License:       ASL 2.0
URL:           https://github.com/spatial4j
Source0:       https://github.com/spatial4j/spatial4j/archive/%{name}-%{version}.tar.gz

BuildRequires: mvn(com.vividsolutions:jts)
BuildRequires: mvn(org.sonatype.oss:oss-parent:pom:)

# test deps
%if 0
BuildRequires: mvn(com.carrotsearch.randomizedtesting:randomizedtesting-runner)
BuildRequires: mvn(junit:junit)
BuildRequires: mvn(org.slf4j:slf4j-simple)
%endif
BuildRequires: maven-local

BuildArch:     noarch

%description
Spatial4j is a general purpose spatial/geospatial Java library.
It's core capabilities are 3-fold: to provide common geospatially-aware shapes,
to provide distance calculations and other math, and to read and write the
shapes to strings.

%package javadoc
Summary:       Javadoc for %{name}

%description javadoc
This package contains javadoc for %{name}.

%prep
%setup -q -n %{name}-%{name}-%{version}

# unavailable mvn plugin
%pom_remove_plugin de.thetaphi:forbiddenapis

%build

%mvn_file : %{name}
# Test skipped for unavailable test deps
%mvn_build -f

%install
%mvn_install

%files -f .mfiles
%doc CHANGES.md LICENSE.txt README.md

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt

%changelog
* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Mar 10 2014 gil cattaneo <puntogil@libero.it> 0.4.1-1
- update to 0.4.1
- switch to java-headless (build)requires (rhbz#1068543)

* Thu Jan 23 2014 gil cattaneo <puntogil@libero.it> 0.4-1
- update to 0.4

* Mon Aug 26 2013 gil cattaneo <puntogil@libero.it> 0.3-1
- initial rpm
