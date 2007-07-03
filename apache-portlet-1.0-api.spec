# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define base_name	portlet-1.0-api
%define section		free
%define gcj_support	1

Name:		apache-portlet-1.0-api
Version:	1.0
Release:	%mkrel 3.3
Epoch:		0
Summary:        Portlet API 1.0 from Jetspeed2
License:	Apache License
Url:		http://portals.apache.org/jetspeed-2/
Group:          Development/Java
#Vendor:		JPackage Project
#Distribution:	JPackage
Source0:	apache-portlet-1.0-api.tar.bz2
# svn export http://svn.apache.org/repos/asf/portals/jetspeed-2/tags/JETSPEED-RELEASE-2.0/portlet-api/
Source1:	apache-portlet-1.0-api-project-info.xml
Source2:	apache-portlet-1.0-api-LICENSE.TXT
Patch0:		apache-portlet-1.0-api-project_xml.patch
%if 0
BuildRequires:	maven
%endif
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  java-devel >= 0:1.4
BuildRequires:	ant >= 0:1.6
Provides:	portlet = %{epoch}:%{version}
Provides:	portlet-1.0-api = %{epoch}:%{version}
%if %{gcj_support}
Requires(post): java-gcj-compat
Requires(postun): java-gcj-compat
BuildRequires:  java-gcj-compat-devel
%else
BuildArch:	noarch
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
Java Standard Portlet API accoring to JSR-168, from Jetspeed-2 

%package javadoc
Summary:        Javadoc %{name}
Group:          Development/Java

%description javadoc
%{summary}.


%prep
%setup -q -n portlet-api
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
cp %{SOURCE1} project-info.xml

%patch0 -b .sav

%build
%if 0
export MAVEN_HOME_LOCAL=$(pwd)/.maven
maven \
	-Dmaven.repo.remote=file:/usr/share/maven/repository \
	-Dmaven.home.local=$MAVEN_HOME_LOCAL \
	jar:jar javadoc
%endif
%{__mkdir_p} target
%{__mkdir_p} target/docs/apidocs
pushd src/java
%{javac} `find . -type f -name "*.java"`
%{jar} cf ../../target/portlet-api-1.0.jar `find . -type f -name "*.class"`
%{javadoc} -d ../../target/docs/apidocs `find . -type f -name "*.java"`

%install
%{__rm} -rf %{buildroot}

install -d -m 755 $RPM_BUILD_ROOT%{_javadir}

install -m 0644 target/portlet-api-1.0.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && ln -sf %{name}-%{version}.jar %{base_name}-%{version}.jar)

# create unversioned symlinks
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} $(echo $jar | sed -e 's+-%{version}\.jar+.jar+'); done)

install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr target/docs/apidocs/* \
	$RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink

install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp %{SOURCE2} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/LICENSE.TXT

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ "$1" = "0" ]; then
  rm -f %{_javadocdir}/%{name}
fi

%files
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}/LICENSE.TXT
%{_javadir}/%{name}*.jar
%{_javadir}/%{base_name}*.jar
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%{_libdir}/gcj/%{name}/*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%ghost %{_javadocdir}/%{name}

