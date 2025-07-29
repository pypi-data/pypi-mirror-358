#line 1 "/tmp/build-via-sdist-cxbrejgp/pyccel-2.0.1/pyccel/extensions/gFTL/include/v2/parameters/define_derived_macros.m4"



   ! Input tokens
   !   Mandatory:
   !     __T1
   !
   !   Optional:
   ! 
   !     __T1_deferred
   !     __T1_polymorphic
   !     __T1_KINDLEN
   !     __T1_kindlen_dummy
   !     __T1_kindlen_component
   !     __T1_rank
   !     __T1_shape

   !     __T1_EQ
   !     __T1_NE
   !     __T1_LT
   !     __T1_GT
   !     __T1_LE
   !     __T1_GE

   !     __T1_EQ_SCALAR
   !     __T1_NE_SCALAR
   !     __T1_LT_SCALAR
   !     __T1_GT_SCALAR
   !     __T1_LE_SCALAR
   !     __T1_GE_SCALAR

   !     __T1_MOVE
   !     __T1_FREE
   !     __T1_COPY

   !  Output tokens:  (some not defined depending upon inputs)
   !
   !     __T1_declare_component__
   !     __T1_declare_result__
   !     __T1_declare_dummy__

   !     __T1_DECLARE__
   !     __T1_allocatable__
   !     __T1_deferred__
   !     __T1_EQ_SCALAR__
   !     __T1_NE_SCALAR__
   !     __T1_LT_SCALAR__
   !     __T1_GT_SCALAR__
   !     __T1_LE_SCALAR__
   !     __T1_GE_SCALAR__

   !     __T1_KINDLEN__
   !     __T1_kindlen_dummy__
   !     __T1_kindlen_component__

   !     __T1_dimension_result__
   !     __T1_dimension_component__
   !     __T1_dimension_dummy__

   !     __T1_type_id__
   !     __T1_kind__
   !     __T1_kindlen_string__

#if __T1 > 0
   ! Instrinsic types

   ! Some older compilers do not support declaring intrinsics with TYPE,
   ! e.g., TYPE(integer), so we suppress that here.

   ! Special per-type settings for different intrinsics:

#    define __T1_type_id__  __T1 >> 3
#    define __T1_kind__  1 << (__T1 & 07)

#    define __T1_DECLARE__(type,kindlen) __IDENTITY(type)__IDENTITY(kindlen)
#    define __T1_NAME__(type,kindlen) __IDENTITY(type)//__IDENTITY(kindlen)
#    if (__T1_type_id__ == __COMPLEX__) | (__T1_type_id__ == __DOUBLE_COMPLEX__)
#        define __T1_type__ complex
#        define __T1_name__ "complex"
#        define __T1_EQ_SCALAR__(a,b) a == b
#        define __T1_NE_SCALAR__(a,b) a /= b
#        if __T1_type_id__ == __COMPLEX__
#            if __T1_kind__ == 16
#                define __T1_KINDLEN__(context) (kind=REAL16)
#                define __T1_kindlen_string__ "(kind=REAL16)"
#            elif __T1_kind__ == 32
#                define __T1_KINDLEN__(context) (kind=REAL32)
#                define __T1_kindlen_string__ "(kind=REAL32)"
#            elif __T1_kind__ == 64
#                define __T1_KINDLEN__(context) (kind=REAL64)
#                define __T1_kindlen_string__ "(kind=REAL64)"
#            elif __T1_kind__ == 128
#                define __T1_KINDLEN__(context) (kind=REAL128)
#                define __T1_kindlen_string__ "(kind=REAL128)"
#            endif
#            if !defined(__T1_default__)
#                define __T1_default_scalar__ (0.,0.)
#           endif
#       else
#            define __T1_KINDLEN__(context) (kind=kind(1.d0))
#            define __T1_kindlen_string__ "(kind=kind(1.d0))"
#            if !defined(__T1_default__)
#                define __T1_default_scalar__ (0.d0,0.d0)
#           endif
#       endif
#    elif __T1_type_id__ == __LOGICAL__

#        define __T1_type__ logical
#        define __T1_EQ_SCALAR__(a,b) a .eqv. b
#        define __T1_NE_SCALAR__(a,b) a .neqv. b
#        define __T1_name__ "logical"
#        if !defined(__T1_default__)
#            define __T1_default_scalar__ .false.
#        endif

#    elif __T1_type_id__ == __UNLIMITED_POLYMORPHIC__

#        undef __T1_DECLARE__
#        undef __T1_NAME__
#        define __T1_DECLARE__(type,kindlen) __IDENTITY(class(*))
#        define __T1_NAME__(type,kindlen) __IDENTITY("class(*)")
#        define __T1_polymorphic__
#        define __T1_type__ *
#        define __T1_name__ "*"
#        if !defined(__T1_default__)
#            define __T1_default_scalar__ NO_TYPE__
#        endif

#    else

!        Most intrinsics can be compared with consistent scalars
#        define __T1_EQ_SCALAR__(a,b) a == b
#        define __T1_NE_SCALAR__(a,b) a /= b
#        define __T1_LE_SCALAR__(a,b) a <= b
#        define __T1_GE_SCALAR__(a,b) a >= b
#        define __T1_LT_SCALAR__(a,b) a < b
#        define __T1_GT_SCALAR__(a,b) a > b

#        if __T1_type_id__ == __INTEGER__

#            define __T1_type__ integer
#            define __T1_name__ "integer"
#            if __T1_kind__ == 8
#                define __T1_KINDLEN__(context) (kind=INT8)
#                define __T1_kindlen_string__ "(kind=INT8)"
#            elif __T1_kind__ == 16
#                define __T1_KINDLEN__(context) (kind=INT16)
#                define __T1_kindlen_string__ "(kind=INT16)"
#            elif __T1_kind__ == 32
#                define __T1_KINDLEN__(context) (kind=INT32)
#                define __T1_kindlen_string__ "(kind=INT32)"
#            elif __T1_kind__ == 64
#                define __T1_KINDLEN__(context) (kind=INT64)
#                define __T1_kindlen_string__ "(kind=INT64)"
#            endif
#            if !defined(__T1_default__)
#                define __T1_default_scalar__ 0
#            endif

#        elif __T1_type_id__ == __REAL__

#            define __T1_type__ real
#            define __T1_name__ "real"
#            if __T1_kind__ == 16
#                define __T1_KINDLEN__(context) (kind=REAL16)
#                define __T1_kindlen_string__ "(kind=REAL16)"
#            elif __T1_kind__ == 32
#                define __T1_KINDLEN__(context) (kind=REAL32)
#                define __T1_kindlen_string__ "(kind=REAL32)"
#            elif __T1_kind__ == 64
#                define __T1_KINDLEN__(context) (kind=REAL64)
#                define __T1_kindlen_string__ "(kind=REAL64)"
#            elif __T1_kind__ == 128
#                define __T1_KINDLEN__(context) (kind=REAL128)
#                define __T1_kindlen_string__ "(kind=REAL128)"
#            endif
#           if !defined(__T1_default__)
#               define __T1_default_scalar__ 0.
#           endif

#        elif __T1_type_id__ == __DOUBLE_PRECISION__

#            define __T1_type__ double precision
#            define __T1_name__ "double precision"
#            if !defined(__T1_default__)
#                define __T1_default_scalar__ 0.
#            endif

#        elif __T1_type_id__ == __CHARACTER__

#            define __T1_type__ character
#            define __T1_name__ "character"
#            if __T1_kind__ > 1
#                define __T1_deferred__
#                define __T1_KINDLEN__(context) (len=context)
#                define __T1_kindlen_string__ "(len=:)"
#                if !defined(__T1_default__)
#                    define __T1_default_scalar__ ""
#                endif
#            else
#                if !defined(__T1_default__)
#                    define __T1_default_scalar__ ""
#                endif
#            endif

#        endif

#    endif

#else
! User defined derived type (or C_PTR, etc)

#    define __T1_type__ __T1
#    ifdef __T1_name
#        define __T1_name__ __T1_name
#    endif
#    ifdef __T1_polymorphic
#        define __T1_polymorphic__
#        define __T1_DECLARE__(t,kindlen) class(__IDENTITY(t)__IDENTITY(kindlen))
#        define __T1_NAME__(name,kindlen) "class("//name//kindlen//")"
#    else
#        define __T1_DECLARE__(t,kindlen) type(__IDENTITY(t)__IDENTITY(kindlen))
#        define __T1_NAME__(name,kindlen) "type("//name//kindlen//")"
#    endif
#    if defined(__T1_default)
#       define __T1_default_scalar__ __T1_default
#    endif

#endif

#ifdef __T1_KINDLEN
#    define __T1_KINDLEN__(context)  __T1_KINDLEN(context)
#else
#    ifndef __T1_KINDLEN__
#        define __T1_KINDLEN__(context)
#    endif
#endif

#ifdef __T1_kindlen_dummy
#    define __T1_kindlen_dummy__ __T1_kindlen_dummy
#else
#    define __T1_kindlen_dummy__ __T1_KINDLEN__(*)
#endif

#ifdef __T1_kindlen_component
#    define __T1_kindlen_component__ __T1_kindlen_component
#else
#    define __T1_kindlen_component__ __T1_KINDLEN__(:)
#endif

#ifdef __T1_kindlen_string
#    define __T1_kindlen_string__ __T1_kindlen_string
#else
#    ifndef __T1_kindlen_string__
#        define __T1_kindlen_string__ ""
#    endif
#endif

#ifdef __T1_rank
#    if __T1_rank == 1
#        define __T1_dimension_result__ , dimension(:)
#        define __T1_rank_string__ "1"
#        define __T1_shape_string__ ", dimension(:)"
#    elif __T1_rank == 2
#        define __T1_dimension_result__ , dimension(:,:)
#        define __T1_rank_string__ "2"
#        define __T1_shape_string__ ", dimension(:,:)"
#    elif __T1_rank == 3
#        define __T1_dimension_result__ , dimension(:,:,:)
#        define __T1_rank_string__ "3"
#        define __T1_shape_string__ ", dimension(:,:,:)"
#    elif __T1_rank == 4
#        define __T1_dimension_result__ , dimension(:,:,:,:)
#        define __T1_rank_string__ "4"
#        define __T1_shape_string__ ", dimension(:,:,:,:)"
#    elif __T1_rank == 5
#        define __T1_dimension_result__ , dimension(:,:,:,:,:)
#        define __T1_rank_string__ "5"
#        define __T1_shape_string__ ", dimension(:,:,:,:,:)"
#    elif __T1_rank == 6
#        define __T1_dimension_result__ , dimension(:,:,:,:,:,:)
#        define __T1_rank_string__ "6"
#        define __T1_shape_string__ ", dimension(:,:,:,:,:,:)"
#    elif __T1_rank == 7
#        define __T1_dimension_result__ , dimension(:,:,:,:,:,:,:)
#        define __T1_rank_string__ "7"
#        define __T1_shape_string__ ", dimension(:,:,:,:,:,:,:)"
#    endif
#    if defined(__T1_shape)
         ! fixed shape       
#        define __T1_dimension_component__ , __IDENTITY(dimension)__IDENTITY(__T1_shape)
#        ifdef __T1_shape_string
#            define __T1_dimension_string__ ", "//__T1_shape_string
#        else
#            define __T1_dimension_string__ ", dimension(rank<"//__T1_rank_string__//">)"
#        endif
#        ifndef __T1_default__
#            define __T1_default__ __T1_default_scalar__
#        endif
#    else
         ! deferred shape
#        define __T1_dimension_component__ __T1_dimension_result__
#        define __T1_dimension_string__ __T1_shape_string__
#        ifndef __T1_default__
#            define __T1_default__ reshape([__T1_type__ :: ],spread(0,1,__T1_rank))
#        endif
#    endif
#    define __T1_dimension_dummy__ __T1_dimension_component__


#else
! Scalar
#    define __T1_dimension_result__
#    define __T1_dimension_component__
#    define __T1_dimension_dummy__
#    define __T1_dimension_string__ ""
#    ifdef __T1_default_scalar__
#        define __T1_default__ __T1_default_scalar__
#    endif
#endif

#if defined(__T1_deferred) && !defined(__T1_deferred__)
#   define __T_deferred__
#endif

#if defined(__T1_deferred__) || defined(__T1_polymorphic__) || (__T1_rank > 0)
#else
#    define __T1_listable__
#endif

#if defined(__T1_deferred__) || defined(__T1_polymorphic__) || (defined(__T1_rank) && !defined(__T1_shape))
#    define __T1_allocatable__
#    define __T1_allocatable_attr__ , allocatable
#    define __T1_allocatable_string__ ", allocatable"
#else
#    define __T1_allocatable_attr__
#    define __T1_allocatable_string__ ""
#endif

! Intel fpp has issues with comma in a macro argument, so we do something a bit brute force here
#ifdef __T1_allocatable__
#    define __T1_declare_component__ __T1_DECLARE__(__T1_type__,__T1_kindlen_component__)__T1_dimension_component__, allocatable
#else
#    define __T1_declare_component__ __T1_DECLARE__(__T1_type__,__T1_kindlen_component__)__T1_dimension_component__
#endif
#define __T1_declare_result__ __T1_DECLARE__(__T1_type__,__T1_kindlen_component__)__T1_dimension_result__
#define __T1_declare_dummy__ __T1_DECLARE__(__T1_type__,__T1_kindlen_dummy__)__T1_dimension_dummy__
#undef tmp

#ifdef __T1_name__
#    define __T1_declare_string__ __T1_NAME__(__T1_name__,__T1_kindlen_string__)//__T1_dimension_string__//__T1_allocatable_string__
#endif

! If user defines __T1_EQ we assume that it is elemental
! for use in array comparisons.   If there is ever a reasonable
! situation that violates this assumption, then a new token
! will need to be added to deactivate this assumption.
#ifdef __T1_EQ
#    define __T1_EQ__(lhs,rhs) __T1_EQ(lhs,rhs)
#elif defined(__T1_EQ_SCALAR__)
#    if __T1_rank == 0
#        define __T1_EQ__(lhs,rhs) __T1_EQ_SCALAR__(lhs,rhs)
#    elif defined(__T1_shape)
#        define __T1_EQ__(lhs,rhs) all(__T1_EQ_SCALAR__([lhs],[rhs]))
#    else
! Must be careful about lack of short-circuit rules in Fortran.   Can only compare
! arrays of same shape, so we use reshape to compare the first N elements (always safe) as well as comparing shapes.
#        define __T1_EQ__(lhs,rhs) all(shape(lhs)==shape(rhs)).and.all(reshape(lhs,[min(size(lhs),size(rhs))])==reshape(lhs,[min(size(lhs),size(rhs))]))
#    endif
#endif

#ifdef __T1_LT
#    define __T1_LT__(lhs,rhs) __T1_LT(lhs,rhs)
#elif defined(__T1_LT_SCALAR__)
#    if __T1_rank == 0
#        define __T1_LT__(lhs,rhs) __T1_LT_SCALAR__(lhs,rhs)
#    endif
#endif


#ifdef __T1_FREE
#    define __T1_FREE__(x)  __T1_FREE(x)
#else
#    ifdef __T1_allocatable__
#        define __T1_FREE__(x)  deallocate(x)
#    else
#        define __T1_FREE__(x)
#    endif
#endif

#ifdef __T1_MOVE
#    define  __T1_MOVE__(lhs,rhs)  __T1_MOVE(lhs,rhs)
#else
#    ifdef __T1_allocatable__
#        define  __T1_MOVE__(lhs,rhs)  call move_alloc(from=rhs,to=lhs)
#    else
#        define  __T1_MOVE__(lhs,rhs)  lhs=rhs
#    endif
#endif


#ifdef __T1_COPY
#    define  __T1_COPY__(lhs,rhs)  __T1_COPY(lhs,rhs)
#else
#    if defined(__T1_polymorphic__)
#        define __T1_COPY__(lhs,rhs) allocate(lhs, source=rhs)
#    else
#        define __T1_COPY__(lhs,rhs) lhs=rhs
#    endif
#endif

