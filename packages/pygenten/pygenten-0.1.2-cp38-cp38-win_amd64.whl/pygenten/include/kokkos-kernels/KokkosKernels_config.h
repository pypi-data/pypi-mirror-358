#ifndef KOKKOSKERNELS_CONFIG_H
#define KOKKOSKERNELS_CONFIG_H

/* Define Fortran mangle from Trilinos macro definition */
// clang-format off
#ifndef F77_BLAS_MANGLE
#define F77_BLAS_MANGLE(name,NAME) name
#endif
// clang-format on

/* Define the current version of Kokkos Kernels */
#define KOKKOSKERNELS_VERSION 40400
#define KOKKOSKERNELS_VERSION_MAJOR 4
#define KOKKOSKERNELS_VERSION_MINOR 4
#define KOKKOSKERNELS_VERSION_PATCH 0


/* Define if fortran blas 1 function can return complex type */
#define KOKKOSKERNELS_TPL_BLAS_RETURN_COMPLEX

/* Define if building in debug mode */
/* #undef HAVE_KOKKOSKERNELS_DEBUG */

/* Define this macro if the quadmath TPL is enabled */
/* #undef HAVE_KOKKOSKERNELS_QUADMATH */

/* Define this macro if the MKL TPL is enabled.  This is different
   than just linking against the MKL to get the BLAS and LAPACK; it
   requires (a) header file(s) as well, and may use functions other
   than just BLAS and LAPACK functions.  */
/* #undef HAVE_KOKKOSKERNELS_MKL */
/* #undef KOKKOSKERNELS_ENABLE_TPL_MKL_SYCL_OVERRIDE */

/* #undef KOKKOSKERNELS_ENABLE_TESTS_AND_PERFSUITE */
/* #undef KOKKOSKERNELS_ENABLE_BENCHMARK */

/* Define this macro if experimental features of Kokkoskernels are enabled */
/* #undef HAVE_KOKKOSKERNELS_EXPERIMENTAL */

/* Define this macro if we have SuperLU API version 5 */
/* #undef HAVE_KOKKOSKERNELS_SUPERLU5_API */

/* Define this macro to disallow instantiations of kernels which are not covered
 * by ETI */
/* #undef KOKKOSKERNELS_ETI_ONLY */
/* Define this macro to only test ETI types */
#define KOKKOSKERNELS_TEST_ETI_ONLY

/* Whether to build kernels for execution space Kokkos::Cuda */
/* #undef KOKKOSKERNELS_INST_EXECSPACE_CUDA */
/* #undef KOKKOSKERNELS_INST_MEMSPACE_CUDASPACE */
/* #undef KOKKOSKERNELS_INST_MEMSPACE_CUDAUVMSPACE */
/* Whether to build kernels for execution space Kokkos::HIP */
/* #undef KOKKOSKERNELS_INST_EXECSPACE_HIP */
/* #undef KOKKOSKERNELS_INST_MEMSPACE_HIPSPACE */
/* #undef KOKKOSKERNELS_INST_MEMSPACE_HIPMANAGEDSPACE */
/* Whether to build kernels for execution space Kokkos::Experimental::SYCL */
/* #undef KOKKOSKERNELS_INST_EXECSPACE_SYCL */
/* #undef KOKKOSKERNELS_INST_MEMSPACE_SYCLSPACE */
/* #undef KOKKOSKERNELS_INST_MEMSPACE_SYCLSHAREDSPACE */
/* Whether to build kernels for execution space Kokkos::Experimental::OpenMPTarget */
/* #undef KOKKOSKERNELS_INST_EXECSPACE_OPENMPTARGET */
/* #undef KOKKOSKERNELS_INST_MEMSPACE_OPENMPTARGETSPACE */
/* Whether to build kernels for execution space Kokkos::OpenMP */
/* #undef KOKKOSKERNELS_INST_EXECSPACE_OPENMP */
/* Whether to build kernels for execution space Kokkos::Threads */
/* #undef KOKKOSKERNELS_INST_EXECSPACE_THREADS */
/* Whether to build kernels for execution space Kokkos::Serial */
#define KOKKOSKERNELS_INST_EXECSPACE_SERIAL

/* Whether to build kernels for memory space Kokkos::HostSpace */
/* #undef KOKKOSKERNELS_INST_MEMSPACE_HOSTSPACE */

/* Whether to build kernels for scalar type double */
/* #undef KOKKOSKERNELS_INST_DOUBLE */
/* Whether to build kernels for scalar type float */
/* #undef KOKKOSKERNELS_INST_FLOAT */
/* Whether to build kernels for scalar type Kokkos::Experimental::half_t */
/* #undef KOKKOSKERNELS_INST_HALF */
/* Whether to build kernels for scalar type Kokkos::Experimental::bhalf_t */
/* #undef KOKKOSKERNELS_INST_BHALF */
/* Whether to build kernels for scalar type complex<double> */
/* #undef KOKKOSKERNELS_INST_COMPLEX_DOUBLE */
/* Whether to build kernels for scalar type complex<float> */
/* #undef KOKKOSKERNELS_INST_COMPLEX_FLOAT */
#if defined KOKKOSKERNELS_INST_COMPLEX_DOUBLE
#define KOKKOSKERNELS_INST_KOKKOS_COMPLEX_DOUBLE_
#endif
#if defined KOKKOSKERNELS_INST_COMPLEX_FLOAT
#define KOKKOSKERNELS_INST_KOKKOS_COMPLEX_FLOAT_
#endif

/* Whether to build kernels for multivectors of LayoutLeft */
/* #undef KOKKOSKERNELS_INST_LAYOUTLEFT */
/* Whether to build kernels for multivectors of LayoutRight */
/* #undef KOKKOSKERNELS_INST_LAYOUTRIGHT */

/* Whether to build kernels for ordinal type int */
/* #undef KOKKOSKERNELS_INST_ORDINAL_INT */
/* Whether to build kernels for ordinal type int64_t */
/* #undef KOKKOSKERNELS_INST_ORDINAL_INT64_T */

/* Whether to build kernels for offset type int */
/* #undef KOKKOSKERNELS_INST_OFFSET_INT */
/* Whether to build kernels for offset type size_t */
/* #undef KOKKOSKERNELS_INST_OFFSET_SIZE_T */

/*
 * Third Party Libraries
 */

/* BLAS library */
#define KOKKOSKERNELS_ENABLE_TPL_BLAS
/* LAPACK */
#define KOKKOSKERNELS_ENABLE_TPL_LAPACK
/* MKL library */
/* #undef KOKKOSKERNELS_ENABLE_TPL_MKL */
/* CUBLAS */
/* #undef KOKKOSKERNELS_ENABLE_TPL_CUBLAS */
/* CUSPARSE */
/* #undef KOKKOSKERNELS_ENABLE_TPL_CUSPARSE */
/* CUSOLVER */
/* #undef KOKKOSKERNELS_ENABLE_TPL_CUSOLVER */
/* MAGMA */
/* #undef KOKKOSKERNELS_ENABLE_TPL_MAGMA */
/* SuperLU */
/* #undef KOKKOSKERNELS_ENABLE_TPL_SUPERLU */
/* #undef KOKKOSKERNELS_ENABLE_TPL_SuperLU */
/* CHOLMOD */
/* #undef KOKKOSKERNELS_ENABLE_TPL_CHOLMOD */
/* CBLAS */
/* #undef KOKKOSKERNELS_ENABLE_TPL_CBLAS */
/* LAPACKE */
/* #undef KOKKOSKERNELS_ENABLE_TPL_LAPACKE */
/* METIS */
/* #undef KOKKOSKERNELS_ENABLE_TPL_METIS */
/* ARMPL */
/* #undef KOKKOSKERNELS_ENABLE_TPL_ARMPL */
/* #undef ARMPL_BUILD */
/* ROCBLAS */
/* #undef KOKKOSKERNELS_ENABLE_TPL_ROCBLAS */
/* ROCSPARSE */
/* #undef KOKKOSKERNELS_ENABLE_TPL_ROCSPARSE */
/* ROCSOLVER */
/* #undef KOKKOSKERNELS_ENABLE_TPL_ROCSOLVER */

/* #undef KOKKOSKERNELS_ENABLE_SUPERNODAL_SPTRSV */

/* if MKL or ARMPL, BLAS is also defined */
#if defined(KOKKOSKERNELS_ENABLE_TPL_MKL) || \
    defined(KOKKOSKERNELS_ENABLE_TPL_ARMPL)
#if !defined(KOKKOSKERNELS_ENABLE_TPL_BLAS)
#define KOKKOSKERNELS_ENABLE_TPL_BLAS
#endif
#endif

#if !defined(KOKKOS_ENABLE_CUDA) && !defined(KOKKOS_ENABLE_HIP) && \
    !defined(KOKKOS_ENABLE_SYCL) && !defined(KOKKOS_ENABLE_OPENMPTARGET)
#define KOKKOSKERNELS_ENABLE_HOST_ONLY
#endif

/*
 * "Optimization level" for computational kernels in this subpackage.
 * The higher the level, the more code variants get generated, and
 * thus the longer the compile times.  However, more code variants
 * mean both better performance overall, and more uniform performance
 * for corner cases.
 */
#define KOKKOSLINALG_OPT_LEVEL @KokkosLinAlg_Opt_Level @

#ifndef KOKKOSKERNELS_IMPL_COMPILE_LIBRARY
#define KOKKOSKERNELS_IMPL_COMPILE_LIBRARY false
#endif

#endif  // KOKKOSKERNELS_CONFIG_H
