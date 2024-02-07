#
# spec file for package pmdk
#
# Copyright (c) 2021 SUSE LLC
# Copyright 2016, Intel Corporation
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#

%global debug_package %{nil}

%global source_date_epoch_from_changelog 0

%define min_ndctl_ver 63.0

Name:           pmdk
Epoch:          100
Version:        2.0.0
Release:        1%{?dist}
Summary:        Persistent Memory Development Kit
License:        BSD-3-Clause
Group:          Development/Libraries/C and C++
URL:            https://github.com/pmem/pmdk/tags

Source0:        %{name}_%{version}.orig.tar.gz

BuildRequires:  automake
BuildRequires:  fdupes
BuildRequires:  man
BuildRequires:  pkg-config
BuildRequires:  pandoc
BuildRequires:  cmake
# NVML was renamed upstream to PMDK between 1.3 and 1.3.1
Obsoletes:      nvml < %{epoch}:%{version}-%{release}
Provides:       nvml = %{epoch}:%{version}-%{release}
BuildRequires:  daxctl-devel >= %min_ndctl_ver
BuildRequires:  ndctl-devel >= %min_ndctl_ver

# By design, NVML does not support any 32-bit architecture.
# Due to dependency on xmmintrin.h and some inline assembly, it can be
# compiled only for x86_64 at the moment.
# Other 64-bit architectures could also be supported, if only there is
# a request for that, and if somebody provides the arch-specific
# implementation of the low-level routines for flushing to persistent
# memory.
ExclusiveArch:  x86_64 aarch64 ppc64le

# Debug variants of the libraries should be filtered out of the provides.
%global __provides_exclude_from ^%_libdir/pmdk_debug/.*\\.so.*$

%description
The Persistent Memory Development Kit (PMDK), formerly known as NVML
(Non-Volatile Memory Library), is a collection of libraries and tools
built on the DAX (Direct Access) feature of the Linux kernel which
allows applications to access persistent memory as memory-mapped
files, as described in the SNIA NVM Programming Model.

%package tools
Summary:        Utilities for Persistent Memory
Group:          System/Base
Obsoletes:      nvml-tools < %{epoch}:%{version}-%{release}
Provides:       nvml-tools = %{epoch}:%{version}-%{release}
Requires:       bash-completion

%description tools
The Persistent Memory Development Kit (PMDK) is a collection of
libraries and tools built on the DAX (Direct Access) feature of the
Linux kernel which allows applications to access persistent memory as
memory-mapped files, as described in the SNIA NVM Programming Model.

* pmempool: utility for administration and diagnosis  of PMDK pools
* pmreorder: Python scripts to parse and replay operations logged by pmemcheck
* daxio: utility to perform I/O on DAX devices

%package -n libpmem1
Summary:        Low-level persistent memory support library
Group:          System/Libraries

%description -n libpmem1
libpmem provides low level persistent memory support, in particular,
support for the persistent memory instructions for flushing changes
to pmem.

%package -n libpmem-devel
Summary:        Development files for the low-level persistent memory library
Group:          Development/Libraries/C and C++
Requires:       libpmem1 = %{epoch}:%{version}-%{release}

%description -n libpmem-devel
libpmem provides low level persistent memory support. In particular,
support for the persistent memory instructions for flushing changes
to pmem is provided.

This library is provided for software which tracks every store to
pmem and needs to flush those changes to durability. Most developers
will find higher level libraries like libpmemobj to be much more
convenient.

%package -n libpmem2-1
Summary:        Low-level persistent memory support library
Group:          System/Libraries

%description -n libpmem2-1
libpmem provides low level persistent memory support, in particular,
support for the persistent memory instructions for flushing changes
to pmem. libpmem2 has a new API that addresses many of the shortcommings
of libpmem1

%package -n libpmem2-devel
Summary:        Development files for the low-level persistent memory library
Group:          Development/Libraries/C and C++
Requires:       libpmem2-1 = %{epoch}:%{version}-%{release}

%description -n libpmem2-devel
libpmem2 provides low level persistent memory support. In particular,
support for the persistent memory instructions for flushing changes
to pmem is provided.

This library is provided for software which tracks every store to
pmem and needs to flush those changes to durability. Most developers
will find higher level libraries like libpmemobj to be much more
convenient. libpmem2 has a new API that addresses many of the shortcommings
of libpmem1

%package -n libpmemobj1
Summary:        Persistent Memory Transactional Object Store library
Group:          System/Libraries

%description -n libpmemobj1
The libpmemobj library provides a transactional object store,
providing memory allocation, transactions, and general facilities for
persistent memory programming.

%package -n libpmemobj-devel
Summary:        Development files for the Persistent Memory Transactional Object Store library
Group:          Development/Libraries/C and C++
Requires:       libpmemobj1 = %{epoch}:%{version}-%{release}

%description -n libpmemobj-devel
The libpmemobj library provides a transactional object store,
providing memory allocation, transactions, and general facilities for
persistent memory programming. Developers new to persistent memory
probably want to start with this library.

%package -n libpmempool1
Summary:        Persistent Memory pool management library
Group:          System/Libraries

%description -n libpmempool1
The libpmempool library provides a set of utilities for off-line administration,
analysis, diagnostics and repair of persistent memory pools created
by libpmemlog, libpemblk and libpmemobj libraries.

%package -n libpmempool-devel
Summary:        Development files for Persistent Memory pool management library
Group:          Development/Libraries/C and C++
Requires:       libpmempool1 = %{epoch}:%{version}-%{release}

%description -n libpmempool-devel
The libpmempool library provides a set of utilities for off-line administration,
analysis, diagnostics and repair of persistent memory pools created
by libpmemlog, libpemblk and libpmemobj libraries.

%package devel-doc
Summary:        Man pages for the libpmem C API
Group:          Documentation/Man

%description devel-doc
Documentation for the pmem library interface.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
%define _lto_cflags %nil
# Currently, NVML makefiles do not allow to easily override CFLAGS,
# so the build flags are passed via EXTRA_CFLAGS.  For debug build
# selected flags are overriden to disable compiler optimizations.
#
# remaining issues:
# * jemalloc attempts to use __builtin_clz, this might not always work
EXTRA_CFLAGS_RELEASE="%optflags" \
EXTRA_CFLAGS_DEBUG="%optflags -Wp,-U_FORTIFY_SOURCE -O0" \
EXTRA_CXXFLAGS="%optflags" \
make %{?_smp_mflags} BINDIR="%_bindir" EXTRA_CFLAGS="-Wno-error" \
  NORPATH=1

# Override LIB_AR with empty string to skip installation of static libraries
%install
b="%buildroot"
%make_install LIB_AR= \
	prefix="%_prefix" \
	libdir="%_libdir" \
	includedir="%_includedir" \
	mandir="%_mandir" \
	bindir="%_bindir" \
	sysconfdir="%_sysconfdir" \
	docdir="%_docdir"
mkdir -p "$b/%_datadir/pmdk"
cp utils/pmdk.magic "$b/%_datadir/pmdk/"

#Fix installation dir for bash completion
mkdir -p %buildroot/%_datadir/bash-completion/completions
mv %buildroot/%_sysconfdir/bash_completion.d/* %buildroot/%_datadir/bash-completion/completions

%fdupes %buildroot/%_prefix

%check
cp src/test/testconfig.sh.example src/test/testconfig.sh
#make check

%post   -n libpmem1 -p /sbin/ldconfig
%postun -n libpmem1 -p /sbin/ldconfig
%post   -n libpmem2-1 -p /sbin/ldconfig
%postun -n libpmem2-1 -p /sbin/ldconfig
%post   -n libpmemobj1 -p /sbin/ldconfig
%postun -n libpmemobj1 -p /sbin/ldconfig
%post   -n libpmempool1 -p /sbin/ldconfig
%postun -n libpmempool1 -p /sbin/ldconfig

%files
%_datadir/pmdk/
%doc ChangeLog

%files tools
%_datadir/bash-completion/completions/*
%_bindir/daxio
%_bindir/pmempool
%_bindir/pmreorder
%_datadir/pmreorder/
%_mandir/man1/daxio.1*
%_mandir/man1/pmempool-*.1*
%_mandir/man1/pmempool.1*
%_mandir/man1/pmreorder.1*
%_mandir/man5/*.5*
%doc LICENSE

%files -n libpmem1
%_libdir/libpmem.so.1*

%files -n libpmem-devel
%_libdir/libpmem.so
%_libdir/pkgconfig/libpmem.pc
%dir %_libdir/pmdk_debug/
%_libdir/pmdk_debug/libpmem.so*
%_includedir/libpmem.h

%files -n libpmem2-1
%_libdir/libpmem2.so.1*

%files -n libpmem2-devel
%_libdir/libpmem2.so
%_libdir/pkgconfig/libpmem2.pc
%dir %_libdir/pmdk_debug/
%_libdir/pmdk_debug/libpmem2.so*
%_includedir/libpmem2.h
%dir %_includedir/libpmem2/
%_includedir/libpmem2/base.h

%files -n libpmemobj1
%_libdir/libpmemobj.so.1*

%files -n libpmemobj-devel
%_libdir/libpmemobj.so
%dir %_libdir/pmdk_debug/
%_libdir/pkgconfig/libpmemobj.pc
%_libdir/pmdk_debug/libpmemobj.so*
%_includedir/libpmemobj.h
%_includedir/libpmemobj/

%files -n libpmempool1
%_libdir/libpmempool.so.1*

%files -n libpmempool-devel
%_libdir/libpmempool.so
%_libdir/pkgconfig/libpmempool.pc
%dir %_libdir/pmdk_debug
%_libdir/pmdk_debug/libpmempool.so*
%_includedir/libpmempool.h

%files devel-doc
%_mandir/man3/*.3*
%_mandir/man7/*.7*
%doc ChangeLog CONTRIBUTING.md README.md

%changelog
