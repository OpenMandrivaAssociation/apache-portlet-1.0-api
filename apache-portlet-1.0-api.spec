# Copyright (c) 2000-2007, JPackage Project
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

%define _with_gcj_support 1
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'

%define _without_maven 1
%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define base_name portlet-1.0-api

%define section free

Name:           apache-portlet-1.0-api
Version:        1.0
Release:        %mkrel 5.0.7
Epoch:          0
Summary:        Portlet API 1.0 from Jetspeed2
License:        Apache License
Url:            http://portals.apache.org/jetspeed-2/
Group:          Development/Java
Source0:        apache-portlet-1.0-api.tar.gz
# svn export http://svn.apache.org/repos/asf/portals/jetspeed-2/tags/JETSPEED-RELEASE-2.0/portlet-api/
Source1:        apache-portlet-1.0-api-pom.xml
Source2:        apache-portlet-1.0-api-LICENSE.TXT
Source3:        apache-portlet-1.0-api-build.xml
BuildRequires:  java-rpmbuild >= 0:1.7.2
BuildRequires:  java-devel >= 0:1.4
BuildRequires:  ant >= 0:1.6
BuildRequires:  ant-nodeps
%if %{with_maven}
BuildRequires:  maven2 >= 2.0.4-9
BuildRequires:  maven2-plugin-compiler
BuildRequires:  maven2-plugin-install
BuildRequires:  maven2-plugin-jar
BuildRequires:  maven2-plugin-javadoc
BuildRequires:  maven2-plugin-release
BuildRequires:  maven2-plugin-resources
BuildRequires:  maven2-plugin-surefire
%endif
Requires(post): jpackage-utils >= 0:1.7.2
Requires(postun): jpackage-utils >= 0:1.7.2 

Provides:       portlet = %{epoch}:%{version}
Provides:       portlet-1.0-api = %{epoch}:%{version}

%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-buildroot
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
%endif

%description
Java Standard Portlet API accoring to JSR-168, from Jetspeed-2 

%package javadoc
Summary:        Javadoc %{name}
Group:          Development/Java
Requires(post):   /bin/rm,/bin/ln
Requires(postun): /bin/rm

%description javadoc
%{summary}.


%prep
%setup -q -n %{name}
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
cp %{SOURCE1} pom.xml
cp %{SOURCE3} build.xml


%build
%if %{with_maven}
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mvn-jpp -e \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        install javadoc:javadoc
%else
export CLASSPATH=
export OPT_JAR_LIST="ant/ant-nodeps"
%{ant} jar javadoc
%endif

%install
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_javadir}

install -m 0644 target/portlet-api-1.0.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && ln -sf %{name}-%{version}.jar %{base_name}-%{version}.jar)

%add_to_maven_depmap javax.portlet portlet-api 1.0 JPP %{base_name}
# create unversioned symlinks
(cd %{buildroot}%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} $(echo $jar | sed -e 's+-%{version}\.jar+.jar+'); done)

#poms
install -d -m 755 %{buildroot}%{_datadir}/maven2/poms
install -pm 644 pom.xml %{buildroot}%{_datadir}/maven2/poms/JPP.portlet-api.pom

install -d -m 755 %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr target/site/apidocs/* \
        %{buildroot}%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name} # ghost symlink

install -d -m 755 %{buildroot}%{_docdir}/%{name}-%{version}
cp %{SOURCE2} %{buildroot}%{_docdir}/%{name}-%{version}/LICENSE.TXT

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf %{buildroot}

%post
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}/LICENSE.TXT
%{_javadir}/%{name}*.jar
%{_javadir}/%{base_name}*.jar
%{_datadir}/maven2
%config(noreplace) %{_mavendepmapfragdir}/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}-%{version}.jar.*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%dir %{_javadocdir}/%{name}
