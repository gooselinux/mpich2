Summary:	A high-performance implementation of MPI
Name:		mpich2
Version:	1.2.1
Release:	2.3%{?dist}
License:	MIT
Group:		Development/Libraries
URL:		http://www.mcs.anl.gov/research/projects/mpich2
Source0:	http://www.mcs.anl.gov/research/projects/mpich2/downloads/tarballs/%{version}/%{name}-%{version}.tar.gz
Source1:	mpich2.macros	
Patch0:		mpich2-modules.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	libXt-devel, libuuid-devel
BuildRequires:	java-devel-openjdk, gcc-gfortran
BuildRequires:	emacs-common, perl, python
Obsoletes:	%{name}-libs < 1.1.1
Requires:	environment-modules
Requires:	python
Requires(post):	chkconfig
Requires(preun):chkconfig
Requires(posttrans):chkconfig
#Requires chkconfig for /usr/sbin/alternatives

%description
MPICH2 is a high-performance and widely portable implementation of the
MPI standard. This release has all MPI-2.1 functions and features
required by the standard with the exeption of support for the
"external32" portable I/O format.

The mpich2 binaries in this RPM packages were configured to use the default
process manager 'MPD' using the default device 'ch3'. The ch3 device
was configured with support for the nemesis channel that allows for
shared-memory and TCP/IP sockets based communication.

This build also include support for using '/usr/sbin/alternatives'
and/or the 'module environment' to select which MPI implementation to use
when multiple implementations are installed.

%package devel
Summary:	Development files for mpich2
Group:		Development/Libraries
Provides:	%{name}-devel-static = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}
Requires:	pkgconfig
Requires:	gcc-gfortran 
Requires(post):	chkconfig
Requires(preun):chkconfig
Requires(posttrans):chkconfig
ExcludeArch: s390 s390x ppc ppc64

#Requires chkconfig for /usr/sbin/alternatives

%description devel
Contains development headers and libraries for mpich2

%package doc
Summary:	Documentations and examples for mpich2
Group:          Documentation
BuildArch:      noarch

%description doc
Contains documentations, examples and manpages for mpich2

# We only compile with gcc, but other people may want other compilers.
# Set the compiler here.
%{!?opt_cc: %global opt_cc gcc}
%{!?opt_fc: %global opt_fc gfortran}
%{!?opt_f77: %global opt_f77 gfortran}
# Optional CFLAGS to use with the specific compiler...gcc doesn't need any,
# so uncomment and undefine to NOT use
%{!?opt_cc_cflags: %global opt_cc_cflags %{optflags}}
%{!?opt_fc_fflags: %global opt_fc_fflags %{optflags}}
#%{!?opt_fc_fflags: %global opt_fc_fflags %{optflags} -I%{_fmoddir}}
%{!?opt_f77_fflags: %global opt_f77_fflags %{optflags}}

%ifarch s390
%global m_option -m31
%else
%global m_option -m%{__isa_bits}
%endif

%ifarch %{ix86} x86_64
%global selected_channels ch3:nemesis
%else
%global selected_channels ch3:sock
%endif

%ifarch x86_64 ia64 ppc64 s390x sparc64
%global priority 41
%else
%global priority 40
%endif

%ifarch x86_64 s390
%global XFLAGS -fPIC
%endif

%prep
%setup -q
%patch0 -p0 -b .modu

%build
%configure	\
	--enable-sharedlibs=gcc					\
	--enable-f90						\
	--with-device=%{selected_channels}			\
	--sysconfdir=%{_sysconfdir}/%{name}-%{_arch}		\
	--includedir=%{_includedir}/%{name}-%{_arch}		\
	--libdir=%{_libdir}/%{name}/lib				\
	--datadir=%{_datadir}/%{name}				\
	--mandir=%{_mandir}/%{name}				\
	--docdir=%{_datadir}/%{name}/doc			\
	--htmldir=%{_datadir}/%{name}/doc			\
	--with-java=%{_sysconfdir}/alternatives/java_sdk	\
	F90=%{opt_fc}						\
	F77=%{opt_f77}						\
	CFLAGS="%{m_option} -O2 %{?XFLAGS}"			\
	CXXFLAGS="%{m_option} -O2 %{?XFLAGS}"			\
	F90FLAGS="%{m_option} -O2 %{?XFLAGS}"			\
	FFLAGS="%{m_option} -O2 %{?XFLAGS}"			\
	LDFLAGS='-Wl,-z,noexecstack'				\
	MPICH2LIB_CFLAGS="%{?opt_cc_cflags}"			\
	MPICH2LIB_CXXFLAGS="%{optflags}"			\
	MPICH2LIB_F90FLAGS="%{?opt_fc_fflags}"			\
	MPICH2LIB_FFLAGS="%{?opt_f77_fflags}"	
#	MPICH2LIB_LDFLAGS='-Wl,-z,noexecstack'			\
#	MPICH2_MPICC_FLAGS="%{m_option} -O2 %{?XFLAGS}"		\
#	MPICH2_MPICXX_FLAGS="%{m_option} -O2 %{?XFLAGS}"	\
#	MPICH2_MPIF90_FLAGS="%{m_option} -O2 %{?XFLAGS}"	\
#	MPICH2_MPIF77_FLAGS="%{m_option} -O2 %{?XFLAGS}"

#	F90FLAGS="%{?opt_fc_fflags} -I%{_fmoddir}/%{name} %{?XFLAGS}"	\
#make %{?_smp_mflags} doesn't work
make VERBOSE=1

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

mkdir -p %{buildroot}%{_libdir}/%{name}/bin %{buildroot}%{_mandir}/man1
rm -f %{buildroot}%{_bindir}/{mpiexec,mpirun,mpdrun}

for execfile in mpiexec mpirun; do 
  ln -s ../../../bin/mpiexec.py %{buildroot}%{_libdir}/%{name}/bin/$execfile
done
BASIC_PGMS="slog2print slog2navigator slog2filter slog2updater logconvertor jumpshot"
CLOG_PGMS="clogprint clogTOslog2 clog2print clog2TOslog2"
RLOG_PGMS="rlogprint rlogTOslog2"
for exefile in $BASIC_PGMS $CLOG_PGMS $RLOG_PGMS mpich2version ; do
  mv %{buildroot}%{_bindir}/$exefile %{buildroot}%{_libdir}/%{name}/bin/$exefile
done

pushd  %{buildroot}%{_bindir}/
ln -s mpiexec.py mpdrun
touch mpiexec mpirun mpich2version
touch %{buildroot}%{_mandir}/man1/mpiexec.1
popd
for b in mpicxx mpicc mpif77 mpif90 mpic++; do 
  mv %{buildroot}%{_bindir}/$b %{buildroot}%{_libdir}/%{name}/bin/;
  touch %{buildroot}%{_bindir}/$b;
  touch %{buildroot}%{_mandir}/man1/$b.1;
done

mv %{buildroot}%{_libdir}/%{name}/lib/pkgconfig %{buildroot}%{_libdir}/
chmod -x %{buildroot}%{_libdir}/pkgconfig/*.pc

#mkdir -p %{buildroot}/%{_fmoddir}/%{name}
#mv  %{buildroot}%{_includedir}/%{name}/*.mod %{buildroot}/%{_fmoddir}/%{name}/

# Install the module file
mkdir -p %{buildroot}%{_datadir}/Modules/modulefiles
cp -pr src/packaging/envmods/mpich2.module %{buildroot}%{_datadir}/Modules/modulefiles/%{name}-%{_arch}
sed -i 's#'%{_bindir}'#'%{_libdir}/%{name}/bin'#;s#@LIBDIR@#'%{_libdir}'#;s#@ARCH@#'%{_arch}'#' %{buildroot}%{_datadir}/Modules/modulefiles/%{name}-%{_arch}

# Install the RPM macro
mkdir -p %{buildroot}%{_sysconfdir}/rpm
cp -pr %{SOURCE1} %{buildroot}%{_sysconfdir}/rpm/macros.%{name}

cp -pr src/mpe2/README src/mpe2/README.mpe2

# Silence rpmlint
sed -i '/^#! \//,1 d' %{buildroot}%{_sysconfdir}/%{name}-%{_arch}/{mpi*.conf,mpe_help.*}

# Work-around the multilib conflicts created by the makefiles
for dirs in collchk graphics logging; do 
  mv %{buildroot}%{_datadir}/%{name}/examples_$dirs/Makefile{,-%{_arch}}
done

# The uninstall script here is not needed/necesary for rpm packaging 
rm -rf %{buildroot}%{_sbindir}/mpe*

find %{buildroot} -type f -name "*.la" -exec rm -f {} ';'


%clean
rm -rf %{buildroot}

%post

/sbin/ldconfig

if [ $1 -eq 1 ] ; then
/usr/sbin/alternatives	\
	--install %{_bindir}/mpirun mpi-run %{_bindir}/mpiexec.py %{priority}	\
	--slave	%{_bindir}/mpiexec mpi-exec %{_bindir}/mpiexec.py	\
	--slave	%{_bindir}/mpich2version mpi-ver			\
			%{_libdir}/%{name}/bin/mpich2version		\
	--slave	%{_mandir}/man1/mpiexec.1.gz mpi-exec-man		\
			%{_mandir}/%{name}/man1/mpiexec.1.gz		\
	--slave	%{_mandir}/man1/mpif90.1.gz mpif90-man			\
			%{_mandir}/%{name}/man1/mpif90.1.gz		\
	--slave	%{_mandir}/man1/mpif77.1.gz mpif77-man			\
			%{_mandir}/%{name}/man1/mpif77.1.gz		\
	--slave	%{_mandir}/man1/mpicc.1.gz mpicc-man			\
			%{_mandir}/%{name}/man1/mpicc.1.gz		\
	--slave	%{_mandir}/man1/mpicxx.1.gz mpicxx-man			\
			%{_mandir}/%{name}/man1/mpicxx.1.gz
fi

%posttrans
if [ $1 -eq 0 ] ; then
/usr/sbin/alternatives	\
	--install %{_bindir}/mpirun mpi-run %{_bindir}/mpiexec.py %{priority}	\
	--slave	%{_bindir}/mpiexec mpi-exec %{_bindir}/mpiexec.py	\
	--slave	%{_bindir}/mpich2version mpi-ver			\
			%{_libdir}/%{name}/bin/mpich2version		\
	--slave	%{_mandir}/man1/mpiexec.1.gz mpi-exec-man		\
			%{_mandir}/%{name}/man1/mpiexec.1.gz		\
	--slave	%{_mandir}/man1/mpif90.1.gz mpif90-man			\
			%{_mandir}/%{name}/man1/mpif90.1.gz		\
	--slave	%{_mandir}/man1/mpif77.1.gz mpif77-man			\
			%{_mandir}/%{name}/man1/mpif77.1.gz		\
	--slave	%{_mandir}/man1/mpicc.1.gz mpicc-man			\
			%{_mandir}/%{name}/man1/mpicc.1.gz		\
	--slave	%{_mandir}/man1/mpicxx.1.gz mpicxx-man			\
			%{_mandir}/%{name}/man1/mpicxx.1.gz
fi

%preun
if [ $1 -eq 0 ] ; then
/usr/sbin/alternatives --remove mpi-run %{_bindir}/mpiexec.py
fi

%postun -p /sbin/ldconfig

%post devel
if [ $1 -eq 1 ] ; then
/usr/sbin/alternatives	\
	--install %{_bindir}/mpicc mpicc %{_libdir}/%{name}/bin/mpicc %{priority}	\
	--slave	%{_bindir}/mpicxx mpicxx %{_libdir}/%{name}/bin/mpicxx	\
	--slave	%{_bindir}/mpic++ mpic++ %{_libdir}/%{name}/bin/mpicxx	\
	--slave	%{_bindir}/mpif90 mpif90 %{_libdir}/%{name}/bin/mpif90	\
	--slave	%{_bindir}/mpif77 mpif77 %{_libdir}/%{name}/bin/mpif77
fi
# Remove the old alternative
if [ $1 -gt 1 ] ; then
	if [ -e %{_bindir}/mp%{__isa_bits}-mpicc ] ; then
		/usr/sbin/alternatives --remove mpicc %{_bindir}/mp%{__isa_bits}-mpicc
	fi
fi

%posttrans devel
if [ $1 -eq 0 ] ; then
/usr/sbin/alternatives	\
	--install %{_bindir}/mpicc mpicc %{_libdir}/%{name}/bin/mpicc %{priority}	\
	--slave	%{_bindir}/mpicxx mpicxx %{_libdir}/%{name}/bin/mpicxx	\
	--slave	%{_bindir}/mpic++ mpic++ %{_libdir}/%{name}/bin/mpicxx	\
	--slave	%{_bindir}/mpif90 mpif90 %{_libdir}/%{name}/bin/mpif90	\
	--slave	%{_bindir}/mpif77 mpif77 %{_libdir}/%{name}/bin/mpif77
fi

%preun devel
if [ $1 -ge 0 ] ; then
/usr/sbin/alternatives --remove mpicc %{_libdir}/%{name}/bin/mpicc
fi

%files
%defattr(-,root,root,-)
%doc CHANGES COPYRIGHT README src/mpe2/README.mpe2 RELEASE_NOTES
%{_bindir}/*
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/lib
%dir %{_libdir}/%{name}/bin
%{_libdir}/%{name}/lib/*.jar
%{_libdir}/%{name}/lib/mpe*.o
%{_libdir}/%{name}/lib/*.so.*
%{_libdir}/%{name}/bin/mpiexec
%{_libdir}/%{name}/bin/mpirun
%{_libdir}/%{name}/bin/mpich2version
%config %{_sysconfdir}/%{name}-%{_arch}/
%config %{_sysconfdir}/rpm/macros.%{name}
%dir %{_mandir}/%{name}
%doc %{_mandir}/%{name}/man1/
%{_datadir}/Modules/modulefiles/%{name}-%{_arch}
%exclude %{_bindir}/mpif*
%exclude %{_bindir}/mpic*
%ghost %{_bindir}/mpiexec
%ghost %{_bindir}/mpirun
%ghost %{_bindir}/mpich2version
%ghost %{_mandir}/man1/mpi*.1.gz

%files devel
%defattr(-,root,root,-)
%{_libdir}/%{name}/bin/mpicc
%{_libdir}/%{name}/bin/mpicxx
%{_libdir}/%{name}/bin/mpic++
%{_libdir}/%{name}/bin/mpif90
%{_libdir}/%{name}/bin/mpif77
%{_libdir}/%{name}/bin/*log*
%{_libdir}/%{name}/bin/jumpshot
%ghost %{_bindir}/mpicc
%ghost %{_bindir}/mpicxx
%ghost %{_bindir}/mpic++
%ghost %{_bindir}/mpif90
%ghost %{_bindir}/mpif77
%{_includedir}/%{name}-%{_arch}/
#%{_fmoddir}/%{name}/
%{_libdir}/%{name}/lib/*.a
%{_libdir}/%{name}/lib/*.so
%{_libdir}/%{name}/lib/trace_rlog/libTraceInput.so
%{_libdir}/pkgconfig/%{name}-ch3.pc
%{_datadir}/%{name}/examples*/Makefile-%{_arch}

%files doc
%defattr(-,root,root,-)
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/doc/
%{_datadir}/%{name}/examples*
%{_datadir}/%{name}/logfiles/
%{_mandir}/%{name}/man3/
%{_mandir}/%{name}/man4/
%exclude %{_datadir}/%{name}/examples*/Makefile-%{_arch}

%changelog
* Thu Aug 5 2010 Jay Fenlason <fenlason@redhat.com> 1.1.1-2.3
- ExcludeArch PowerPC and S390{,x} because they no longer have
  the Java jdk required for building.
  Resolves: rhbz#613122 - no longer compiles on s390, etc

* Fri Jul 9 2010 Jay Fenlason <fenlason@redhat.com>
- Fix the attempted removal of %{_bindir}/mp%{__isa_bits}-mpicc
  in the devel package to match upstream Fedora.
  Resolves: rhbz#587209 mpich2-devel.i686 and mpich2-devel.x86_64 cannot coexist

* Fri Mar 26 2010 Jay Fenlason <fenlason@redhat.com> 1.1.1-2.2
- Move the .2 to the correct(?) place in the release field.
- add -fPIC for s390, to close
  Resolves: rhbz#572901 File usr/lib/mpich2/lib/libfmpich.so.1.2 acquired TEXTREL relocations on s390, this suggests missing -fPIC

* Fri Jan 8 2010 Jay Fenlason <fenlason@redhat.com> - 1.1.1-2.1
- add the m_option macro to replace hardcoding -m{__isa_bits}
  and define it correctly for s390, where __isa_bits is 32, but
  the option to pass to gcc et all is -m31.
  Resolves: rhbz#553650 - mpich2 is failing to build

* Thu Nov 26 2009 Deji Akingunola <dakingun@gmail.com> - 1.2.1-2
- Fix the mpich2.module patch.

* Wed Nov 18 2009 Deji Akingunola <dakingun@gmail.com> - 1.2.1-1
- Update to 1.2.1

* Tue Nov 03 2009 Deji Akingunola <dakingun@gmail.com> - 1.2-2
- Backport upstream patch to workaround changes in Python behaviour in F-12
- Clean-up the spec file to remove its 'Fedora-ness'.

* Sat Oct 10 2009 Deji Akingunola <dakingun@gmail.com> - 1.2-1
- Adapt to the Fedora MPI packaging guildelines
- Split out a -doc subpackage
- New upstream version, v1.2

* Tue Aug 11 2009 Deji Akingunola <dakingun@gmail.com> - 1.1.1p1-1
- New upstream version

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 22 2009 Deji Akingunola <dakingun@gmail.com> - 1.1.1-1
- Update to 1.1.1
- Remove (and obsolete) the -libs subpackage, it is not necessary.
- Change e2fsprogs BR to libuuid

* Wed May 20 2009 Deji Akingunola <dakingun@gmail.com> - 1.1-1
- Update to 1.1

* Wed May 20 2009 Deji Akingunola <dakingun@gmail.com> - 1.1-0.4.rc1
- Install the libdir under /etc/ld.so.conf.d

* Mon May 18 2009 Deji Akingunola <dakingun@gmail.com> - 1.1-0.3.rc1
- Update to 1.1rc1
- Update spec to follow the proposed packaging guildelines wrt using alternatives
- Also change to use the global macro instead of define.

* Sun Mar 29 2009 Deji Akingunola <dakingun@gmail.com> - 1.1-0.2.b1
- Specifically build with openjdk Java, so Jumpshot works (Anthony Chan)

* Wed Mar 18 2009 Deji Akingunola <dakingun@gmail.com> - 1.1-0.1.b1
- Update for the 1.1 (beta) release
- Stop building with dllchan, it is not fully supported
- Fix un-owned directory (#490270)
- Add Posttrans scriplets to work around 1.0.8-3 scriplet brokenness

* Mon Mar 09 2009 Deji Akingunola <dakingun@gmail.com> - 1.0.8-3
- Drop the ssm channel from ppc* archs, it fails to build
- Python scripts in bindir and sbindir are no longer bytecompiled (F-11+)
- Enhance the spec file to support ia64 and sparc
- Include mpiexec and mpirun (symlinks) in the environment module bindir 

* Fri Mar 06 2009 Deji Akingunola <dakingun@gmail.com> - 1.0.8-2
- Fix the source url, pointed out from package review
- Finally accepted to go into Fedora

* Sat Oct 24 2008 Deji Akingunola <dakingun@gmail.com> - 1.0.8-1
- Update to the 1.0.8
- Configure with the default nemesis channel

* Fri May 16 2008 Deji Akingunola <dakingun@gmail.com> - 1.0.7-5
- Update the alternate compiler/compiler flags macro to allow overriding it
  from command-line

* Wed Apr 16 2008 Deji Akingunola <dakingun@gmail.com> - 1.0.7-4
- Apply patch from Orion Poplawski to silence rpmlint

* Tue Apr 15 2008 Deji Akingunola <dakingun@gmail.com> - 1.0.7-3
- Add a note on the device/channels configuration options used, and
- Fix logfile listings as suggested by Orion Poplawski (Package review, 171993)

* Tue Apr 15 2008 Deji Akingunola <dakingun@gmail.com> - 1.0.7-2
- Fix the source url

* Sat Apr 05 2008 Deji Akingunola <dakingun@gmail.com> - 1.0.7-1
- Update to 1.0.7

* Mon Oct 15 2007 Deji Akingunola <dakingun@gmail.com> - 1.0.6p1-1
- Update to 1.0.6p1

* Mon Oct 15 2007 Deji Akingunola <dakingun@gmail.com> - 1.0.6-1
- New version upgrade

* Mon Jul 31 2007 Deji Akingunola <dakingun@gmail.com> - 1.0.5p4-4
- Create a -mpi-manpages subpackage for the MPI routines manuals

* Fri Jul 27 2007 Deji Akingunola <dakingun@gmail.com> - 1.0.5p4-3
- Fix java-gcj-compat BR
- Handle upgrades in the post scripts

* Mon Jun 12 2007 Deji Akingunola <dakingun@gmail.com> - 1.0.5p4-2
- Fix typos and make other adjustments arising from Fedora package reviews

* Mon Jun 12 2007 Deji Akingunola <dakingun@gmail.com> - 1.0.5p4-1
- Patch #4 release

* Mon Feb 12 2007 Deji Akingunola <dakingun@gmail.com> - 1.0.5p2-1
- Patch #2 release

* Tue Jan 09 2007 Deji Akingunola <dakingun@gmail.com> - 1.0.5p1-1
- New release with manpages
- Create a -libs subpackage as it's done in Fedora's openmpi to help with
  multi-libs packaging
- Disable modules support (until I can properly figure it out)

* Wed Dec 27 2006 Deji Akingunola <dakingun@gmail.com> - 1.0.5-1
- New release

* Sat Nov 18 2006 Deji Akingunola <dakingun@gmail.com> - 1.0.4p1-2
- Set the java_sdk directory so all java bit work  

* Sat Sep 02 2006 Deji Akingunola <dakingun@gmail.com> - 1.0.4p1-1
- Update to version 1.0.4p1
- Cleanup up spec file to use alternatives similarly to FC's openmpi

* Wed Aug 02 2006 Deji Akingunola <dakingun@gmail.com> - 1.0.4-1
- Update to version 1.0.4

* Thu May 18 2006 Deji Akingunola <dakingun@gmail.com> - 1.0.3-3
- Add missing BRs (Orion Polawski)

* Mon Apr 10 2006 Deji Akingunola <dakingun@gmail.com> - 1.0.3-2
- Rewrite the spec, borrowing extensively from openmpi's spec by Jason Vas Dias
- Allows use of environment modules and alternatives

* Fri Nov 25 2005 Deji Akingunola <dakingun@gmail.com> - 1.0.3-1
- Update to new version

* Sat Oct 15 2005 Deji Akingunola <deji.aking@gmail.com> - 1.0.2p1-1
- Initial package
