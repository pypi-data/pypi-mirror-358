#line 1 "/tmp/build-via-sdist-cxbrejgp/pyccel-2.0.1/pyccel/extensions/gFTL/include/v2/parameters/define_derived_macros.m4"



   ! Input tokens
   !   Mandatory:
   !     __T2
   !
   !   Optional:
   ! 
   !     __T2_deferred
   !     __T2_polymorphic
   !     __T2_KINDLEN
   !     __T2_kindlen_dummy
   !     __T2_kindlen_component
   !     __T2_rank
   !     __T2_shape

   !     __T2_EQ
   !     __T2_NE
   !     __T2_LT
   !     __T2_GT
   !     __T2_LE
   !     __T2_GE

   !     __T2_EQ_SCALAR
   !     __T2_NE_SCALAR
   !     __T2_LT_SCALAR
   !     __T2_GT_SCALAR
   !     __T2_LE_SCALAR
   !     __T2_GE_SCALAR

   !     __T2_MOVE
   !     __T2_FREE
   !     __T2_COPY

   !  Output tokens:  (some not defined depending upon inputs)
   !
   !     __T2_declare_component__
   !     __T2_declare_result__
   !     __T2_declare_dummy__

   !     __T2_DECLARE__
   !     __T2_allocatable__
   !     __T2_deferred__
   !     __T2_EQ_SCALAR__
   !     __T2_NE_SCALAR__
   !     __T2_LT_SCALAR__
   !     __T2_GT_SCALAR__
   !     __T2_LE_SCALAR__
   !     __T2_GE_SCALAR__

   !     __T2_KINDLEN__
   !     __T2_kindlen_dummy__
   !     __T2_kindlen_component__

   !     __T2_dimension_result__
   !     __T2_dimension_component__
   !     __T2_dimension_dummy__

   !     __T2_type_id__
   !     __T2_kind__
   !     __T2_kindlen_string__

#if __T2 > 0
   ! Instrinsic types

   ! Some older compilers do not support declaring intrinsics with TYPE,
   ! e.g., TYPE(integer), so we suppress that here.

   ! Special per-type settings for different intrinsics:

#    define __T2_type_id__  __T2 >> 3
#    define __T2_kind__  1 << (__T2 & 07)

#    define __T2_DECLARE__(type,kindlen) __IDENTITY(type)__IDENTITY(kindlen)
#    define __T2_NAME__(type,kindlen) __IDENTITY(type)//__IDENTITY(kindlen)
#    if (__T2_type_id__ == __COMPLEX__) | (__T2_type_id__ == __DOUBLE_COMPLEX__)
#        define __T2_type__ complex
#        define __T2_name__ "complex"
#        define __T2_EQ_SCALAR__(a,b) a == b
#        define __T2_NE_SCALAR__(a,b) a /= b
#        if __T2_type_id__ == __COMPLEX__
#            if __T2_kind__ == 16
#                define __T2_KINDLEN__(context) (kind=REAL16)
#                define __T2_kindlen_string__ "(kind=REAL16)"
#            elif __T2_kind__ == 32
#                define __T2_KINDLEN__(context) (kind=REAL32)
#                define __T2_kindlen_string__ "(kind=REAL32)"
#            elif __T2_kind__ == 64
#                define __T2_KINDLEN__(context) (kind=REAL64)
#                define __T2_kindlen_string__ "(kind=REAL64)"
#            elif __T2_kind__ == 128
#                define __T2_KINDLEN__(context) (kind=REAL128)
#                define __T2_kindlen_string__ "(kind=REAL128)"
#            endif
#            if !defined(__T2_default__)
#                define __T2_default_scalar__ (0.,0.)
#           endif
#       else
#            define __T2_KINDLEN__(context) (kind=kind(1.d0))
#            define __T2_kindlen_string__ "(kind=kind(1.d0))"
#            if !defined(__T2_default__)
#                define __T2_default_scalar__ (0.d0,0.d0)
#           endif
#       endif
#    elif __T2_type_id__ == __LOGICAL__

#        define __T2_type__ logical
#        define __T2_EQ_SCALAR__(a,b) a .eqv. b
#        define __T2_NE_SCALAR__(a,b) a .neqv. b
#        define __T2_name__ "logical"
#        if !defined(__T2_default__)
#            define __T2_default_scalar__ .false.
#        endif

#    elif __T2_type_id__ == __UNLIMITED_POLYMORPHIC__

#        undef __T2_DECLARE__
#        undef __T2_NAME__
#        define __T2_DECLARE__(type,kindlen) __IDENTITY(class(*))
#        define __T2_NAME__(type,kindlen) __IDENTITY("class(*)")
#        define __T2_polymorphic__
#        define __T2_type__ *
#        define __T2_name__ "*"
#        if !defined(__T2_default__)
#            define __T2_default_scalar__ NO_TYPE__
#        endif

#    else

!        Most intrinsics can be compared with consistent scalars
#        define __T2_EQ_SCALAR__(a,b) a == b
#        define __T2_NE_SCALAR__(a,b) a /= b
#        define __T2_LE_SCALAR__(a,b) a <= b
#        define __T2_GE_SCALAR__(a,b) a >= b
#        define __T2_LT_SCALAR__(a,b) a < b
#        define __T2_GT_SCALAR__(a,b) a > b

#        if __T2_type_id__ == __INTEGER__

#            define __T2_type__ integer
#            define __T2_name__ "integer"
#            if __T2_kind__ == 8
#                define __T2_KINDLEN__(context) (kind=INT8)
#                define __T2_kindlen_string__ "(kind=INT8)"
#            elif __T2_kind__ == 16
#                define __T2_KINDLEN__(context) (kind=INT16)
#                define __T2_kindlen_string__ "(kind=INT16)"
#            elif __T2_kind__ == 32
#                define __T2_KINDLEN__(context) (kind=INT32)
#                define __T2_kindlen_string__ "(kind=INT32)"
#            elif __T2_kind__ == 64
#                define __T2_KINDLEN__(context) (kind=INT64)
#                define __T2_kindlen_string__ "(kind=INT64)"
#            endif
#            if !defined(__T2_default__)
#                define __T2_default_scalar__ 0
#            endif

#        elif __T2_type_id__ == __REAL__

#            define __T2_type__ real
#            define __T2_name__ "real"
#            if __T2_kind__ == 16
#                define __T2_KINDLEN__(context) (kind=REAL16)
#                define __T2_kindlen_string__ "(kind=REAL16)"
#            elif __T2_kind__ == 32
#                define __T2_KINDLEN__(context) (kind=REAL32)
#                define __T2_kindlen_string__ "(kind=REAL32)"
#            elif __T2_kind__ == 64
#                define __T2_KINDLEN__(context) (kind=REAL64)
#                define __T2_kindlen_string__ "(kind=REAL64)"
#            elif __T2_kind__ == 128
#                define __T2_KINDLEN__(context) (kind=REAL128)
#                define __T2_kindlen_string__ "(kind=REAL128)"
#            endif
#           if !defined(__T2_default__)
#               define __T2_default_scalar__ 0.
#           endif

#        elif __T2_type_id__ == __DOUBLE_PRECISION__

#            define __T2_type__ double precision
#            define __T2_name__ "double precision"
#            if !defined(__T2_default__)
#                define __T2_default_scalar__ 0.
#            endif

#        elif __T2_type_id__ == __CHARACTER__

#            define __T2_type__ character
#            define __T2_name__ "character"
#            if __T2_kind__ > 1
#                define __T2_deferred__
#                define __T2_KINDLEN__(context) (len=context)
#                define __T2_kindlen_string__ "(len=:)"
#                if !defined(__T2_default__)
#                    define __T2_default_scalar__ ""
#                endif
#            else
#                if !defined(__T2_default__)
#                    define __T2_default_scalar__ ""
#                endif
#            endif

#        endif

#    endif

#else
! User defined derived type (or C_PTR, etc)

#    define __T2_type__ __T2
#    ifdef __T2_name
#        define __T2_name__ __T2_name
#    endif
#    ifdef __T2_polymorphic
#        define __T2_polymorphic__
#        define __T2_DECLARE__(t,kindlen) class(__IDENTITY(t)__IDENTITY(kindlen))
#        define __T2_NAME__(name,kindlen) "class("//name//kindlen//")"
#    else
#        define __T2_DECLARE__(t,kindlen) type(__IDENTITY(t)__IDENTITY(kindlen))
#        define __T2_NAME__(name,kindlen) "type("//name//kindlen//")"
#    endif
#    if defined(__T2_default)
#       define __T2_default_scalar__ __T2_default
#    endif

#endif

#ifdef __T2_KINDLEN
#    define __T2_KINDLEN__(context)  __T2_KINDLEN(context)
#else
#    ifndef __T2_KINDLEN__
#        define __T2_KINDLEN__(context)
#    endif
#endif

#ifdef __T2_kindlen_dummy
#    define __T2_kindlen_dummy__ __T2_kindlen_dummy
#else
#    define __T2_kindlen_dummy__ __T2_KINDLEN__(*)
#endif

#ifdef __T2_kindlen_component
#    define __T2_kindlen_component__ __T2_kindlen_component
#else
#    define __T2_kindlen_component__ __T2_KINDLEN__(:)
#endif

#ifdef __T2_kindlen_string
#    define __T2_kindlen_string__ __T2_kindlen_string
#else
#    ifndef __T2_kindlen_string__
#        define __T2_kindlen_string__ ""
#    endif
#endif

#ifdef __T2_rank
#    if __T2_rank == 1
#        define __T2_dimension_result__ , dimension(:)
#        define __T2_rank_string__ "1"
#        define __T2_shape_string__ ", dimension(:)"
#    elif __T2_rank == 2
#        define __T2_dimension_result__ , dimension(:,:)
#        define __T2_rank_string__ "2"
#        define __T2_shape_string__ ", dimension(:,:)"
#    elif __T2_rank == 3
#        define __T2_dimension_result__ , dimension(:,:,:)
#        define __T2_rank_string__ "3"
#        define __T2_shape_string__ ", dimension(:,:,:)"
#    elif __T2_rank == 4
#        define __T2_dimension_result__ , dimension(:,:,:,:)
#        define __T2_rank_string__ "4"
#        define __T2_shape_string__ ", dimension(:,:,:,:)"
#    elif __T2_rank == 5
#        define __T2_dimension_result__ , dimension(:,:,:,:,:)
#        define __T2_rank_string__ "5"
#        define __T2_shape_string__ ", dimension(:,:,:,:,:)"
#    elif __T2_rank == 6
#        define __T2_dimension_result__ , dimension(:,:,:,:,:,:)
#        define __T2_rank_string__ "6"
#        define __T2_shape_string__ ", dimension(:,:,:,:,:,:)"
#    elif __T2_rank == 7
#        define __T2_dimension_result__ , dimension(:,:,:,:,:,:,:)
#        define __T2_rank_string__ "7"
#        define __T2_shape_string__ ", dimension(:,:,:,:,:,:,:)"
#    endif
#    if defined(__T2_shape)
         ! fixed shape       
#        define __T2_dimension_component__ , __IDENTITY(dimension)__IDENTITY(__T2_shape)
#        ifdef __T2_shape_string
#            define __T2_dimension_string__ ", "//__T2_shape_string
#        else
#            define __T2_dimension_string__ ", dimension(rank<"//__T2_rank_string__//">)"
#        endif
#        ifndef __T2_default__
#            define __T2_default__ __T2_default_scalar__
#        endif
#    else
         ! deferred shape
#        define __T2_dimension_component__ __T2_dimension_result__
#        define __T2_dimension_string__ __T2_shape_string__
#        ifndef __T2_default__
#            define __T2_default__ reshape([__T2_type__ :: ],spread(0,1,__T2_rank))
#        endif
#    endif
#    define __T2_dimension_dummy__ __T2_dimension_component__


#else
! Scalar
#    define __T2_dimension_result__
#    define __T2_dimension_component__
#    define __T2_dimension_dummy__
#    define __T2_dimension_string__ ""
#    ifdef __T2_default_scalar__
#        define __T2_default__ __T2_default_scalar__
#    endif
#endif

#if defined(__T2_deferred) && !defined(__T2_deferred__)
#   define __T_deferred__
#endif

#if defined(__T2_deferred__) || defined(__T2_polymorphic__) || (__T2_rank > 0)
#else
#    define __T2_listable__
#endif

#if defined(__T2_deferred__) || defined(__T2_polymorphic__) || (defined(__T2_rank) && !defined(__T2_shape))
#    define __T2_allocatable__
#    define __T2_allocatable_attr__ , allocatable
#    define __T2_allocatable_string__ ", allocatable"
#else
#    define __T2_allocatable_attr__
#    define __T2_allocatable_string__ ""
#endif

! Intel fpp has issues with comma in a macro argument, so we do something a bit brute force here
#ifdef __T2_allocatable__
#    define __T2_declare_component__ __T2_DECLARE__(__T2_type__,__T2_kindlen_component__)__T2_dimension_component__, allocatable
#else
#    define __T2_declare_component__ __T2_DECLARE__(__T2_type__,__T2_kindlen_component__)__T2_dimension_component__
#endif
#define __T2_declare_result__ __T2_DECLARE__(__T2_type__,__T2_kindlen_component__)__T2_dimension_result__
#define __T2_declare_dummy__ __T2_DECLARE__(__T2_type__,__T2_kindlen_dummy__)__T2_dimension_dummy__
#undef tmp

#ifdef __T2_name__
#    define __T2_declare_string__ __T2_NAME__(__T2_name__,__T2_kindlen_string__)//__T2_dimension_string__//__T2_allocatable_string__
#endif

! If user defines __T2_EQ we assume that it is elemental
! for use in array comparisons.   If there is ever a reasonable
! situation that violates this assumption, then a new token
! will need to be added to deactivate this assumption.
#ifdef __T2_EQ
#    define __T2_EQ__(lhs,rhs) __T2_EQ(lhs,rhs)
#elif defined(__T2_EQ_SCALAR__)
#    if __T2_rank == 0
#        define __T2_EQ__(lhs,rhs) __T2_EQ_SCALAR__(lhs,rhs)
#    elif defined(__T2_shape)
#        define __T2_EQ__(lhs,rhs) all(__T2_EQ_SCALAR__([lhs],[rhs]))
#    else
! Must be careful about lack of short-circuit rules in Fortran.   Can only compare
! arrays of same shape, so we use reshape to compare the first N elements (always safe) as well as comparing shapes.
#        define __T2_EQ__(lhs,rhs) all(shape(lhs)==shape(rhs)).and.all(reshape(lhs,[min(size(lhs),size(rhs))])==reshape(lhs,[min(size(lhs),size(rhs))]))
#    endif
#endif

#ifdef __T2_LT
#    define __T2_LT__(lhs,rhs) __T2_LT(lhs,rhs)
#elif defined(__T2_LT_SCALAR__)
#    if __T2_rank == 0
#        define __T2_LT__(lhs,rhs) __T2_LT_SCALAR__(lhs,rhs)
#    endif
#endif


#ifdef __T2_FREE
#    define __T2_FREE__(x)  __T2_FREE(x)
#else
#    ifdef __T2_allocatable__
#        define __T2_FREE__(x)  deallocate(x)
#    else
#        define __T2_FREE__(x)
#    endif
#endif

#ifdef __T2_MOVE
#    define  __T2_MOVE__(lhs,rhs)  __T2_MOVE(lhs,rhs)
#else
#    ifdef __T2_allocatable__
#        define  __T2_MOVE__(lhs,rhs)  call move_alloc(from=rhs,to=lhs)
#    else
#        define  __T2_MOVE__(lhs,rhs)  lhs=rhs
#    endif
#endif


#ifdef __T2_COPY
#    define  __T2_COPY__(lhs,rhs)  __T2_COPY(lhs,rhs)
#else
#    if defined(__T2_polymorphic__)
#        define __T2_COPY__(lhs,rhs) allocate(lhs, source=rhs)
#    else
#        define __T2_COPY__(lhs,rhs) lhs=rhs
#    endif
#endif

