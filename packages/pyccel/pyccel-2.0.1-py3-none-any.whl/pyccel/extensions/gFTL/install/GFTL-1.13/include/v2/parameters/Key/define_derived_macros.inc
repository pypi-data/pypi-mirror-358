#line 1 "/tmp/build-via-sdist-cxbrejgp/pyccel-2.0.1/pyccel/extensions/gFTL/include/v2/parameters/define_derived_macros.m4"



   ! Input tokens
   !   Mandatory:
   !     __Key
   !
   !   Optional:
   ! 
   !     __Key_deferred
   !     __Key_polymorphic
   !     __Key_KINDLEN
   !     __Key_kindlen_dummy
   !     __Key_kindlen_component
   !     __Key_rank
   !     __Key_shape

   !     __Key_EQ
   !     __Key_NE
   !     __Key_LT
   !     __Key_GT
   !     __Key_LE
   !     __Key_GE

   !     __Key_EQ_SCALAR
   !     __Key_NE_SCALAR
   !     __Key_LT_SCALAR
   !     __Key_GT_SCALAR
   !     __Key_LE_SCALAR
   !     __Key_GE_SCALAR

   !     __Key_MOVE
   !     __Key_FREE
   !     __Key_COPY

   !  Output tokens:  (some not defined depending upon inputs)
   !
   !     __Key_declare_component__
   !     __Key_declare_result__
   !     __Key_declare_dummy__

   !     __Key_DECLARE__
   !     __Key_allocatable__
   !     __Key_deferred__
   !     __Key_EQ_SCALAR__
   !     __Key_NE_SCALAR__
   !     __Key_LT_SCALAR__
   !     __Key_GT_SCALAR__
   !     __Key_LE_SCALAR__
   !     __Key_GE_SCALAR__

   !     __Key_KINDLEN__
   !     __Key_kindlen_dummy__
   !     __Key_kindlen_component__

   !     __Key_dimension_result__
   !     __Key_dimension_component__
   !     __Key_dimension_dummy__

   !     __Key_type_id__
   !     __Key_kind__
   !     __Key_kindlen_string__

#if __Key > 0
   ! Instrinsic types

   ! Some older compilers do not support declaring intrinsics with TYPE,
   ! e.g., TYPE(integer), so we suppress that here.

   ! Special per-type settings for different intrinsics:

#    define __Key_type_id__  __Key >> 3
#    define __Key_kind__  1 << (__Key & 07)

#    define __Key_DECLARE__(type,kindlen) __IDENTITY(type)__IDENTITY(kindlen)
#    define __Key_NAME__(type,kindlen) __IDENTITY(type)//__IDENTITY(kindlen)
#    if (__Key_type_id__ == __COMPLEX__) | (__Key_type_id__ == __DOUBLE_COMPLEX__)
#        define __Key_type__ complex
#        define __Key_name__ "complex"
#        define __Key_EQ_SCALAR__(a,b) a == b
#        define __Key_NE_SCALAR__(a,b) a /= b
#        if __Key_type_id__ == __COMPLEX__
#            if __Key_kind__ == 16
#                define __Key_KINDLEN__(context) (kind=REAL16)
#                define __Key_kindlen_string__ "(kind=REAL16)"
#            elif __Key_kind__ == 32
#                define __Key_KINDLEN__(context) (kind=REAL32)
#                define __Key_kindlen_string__ "(kind=REAL32)"
#            elif __Key_kind__ == 64
#                define __Key_KINDLEN__(context) (kind=REAL64)
#                define __Key_kindlen_string__ "(kind=REAL64)"
#            elif __Key_kind__ == 128
#                define __Key_KINDLEN__(context) (kind=REAL128)
#                define __Key_kindlen_string__ "(kind=REAL128)"
#            endif
#            if !defined(__Key_default__)
#                define __Key_default_scalar__ (0.,0.)
#           endif
#       else
#            define __Key_KINDLEN__(context) (kind=kind(1.d0))
#            define __Key_kindlen_string__ "(kind=kind(1.d0))"
#            if !defined(__Key_default__)
#                define __Key_default_scalar__ (0.d0,0.d0)
#           endif
#       endif
#    elif __Key_type_id__ == __LOGICAL__

#        define __Key_type__ logical
#        define __Key_EQ_SCALAR__(a,b) a .eqv. b
#        define __Key_NE_SCALAR__(a,b) a .neqv. b
#        define __Key_name__ "logical"
#        if !defined(__Key_default__)
#            define __Key_default_scalar__ .false.
#        endif

#    elif __Key_type_id__ == __UNLIMITED_POLYMORPHIC__

#        undef __Key_DECLARE__
#        undef __Key_NAME__
#        define __Key_DECLARE__(type,kindlen) __IDENTITY(class(*))
#        define __Key_NAME__(type,kindlen) __IDENTITY("class(*)")
#        define __Key_polymorphic__
#        define __Key_type__ *
#        define __Key_name__ "*"
#        if !defined(__Key_default__)
#            define __Key_default_scalar__ NO_TYPE__
#        endif

#    else

!        Most intrinsics can be compared with consistent scalars
#        define __Key_EQ_SCALAR__(a,b) a == b
#        define __Key_NE_SCALAR__(a,b) a /= b
#        define __Key_LE_SCALAR__(a,b) a <= b
#        define __Key_GE_SCALAR__(a,b) a >= b
#        define __Key_LT_SCALAR__(a,b) a < b
#        define __Key_GT_SCALAR__(a,b) a > b

#        if __Key_type_id__ == __INTEGER__

#            define __Key_type__ integer
#            define __Key_name__ "integer"
#            if __Key_kind__ == 8
#                define __Key_KINDLEN__(context) (kind=INT8)
#                define __Key_kindlen_string__ "(kind=INT8)"
#            elif __Key_kind__ == 16
#                define __Key_KINDLEN__(context) (kind=INT16)
#                define __Key_kindlen_string__ "(kind=INT16)"
#            elif __Key_kind__ == 32
#                define __Key_KINDLEN__(context) (kind=INT32)
#                define __Key_kindlen_string__ "(kind=INT32)"
#            elif __Key_kind__ == 64
#                define __Key_KINDLEN__(context) (kind=INT64)
#                define __Key_kindlen_string__ "(kind=INT64)"
#            endif
#            if !defined(__Key_default__)
#                define __Key_default_scalar__ 0
#            endif

#        elif __Key_type_id__ == __REAL__

#            define __Key_type__ real
#            define __Key_name__ "real"
#            if __Key_kind__ == 16
#                define __Key_KINDLEN__(context) (kind=REAL16)
#                define __Key_kindlen_string__ "(kind=REAL16)"
#            elif __Key_kind__ == 32
#                define __Key_KINDLEN__(context) (kind=REAL32)
#                define __Key_kindlen_string__ "(kind=REAL32)"
#            elif __Key_kind__ == 64
#                define __Key_KINDLEN__(context) (kind=REAL64)
#                define __Key_kindlen_string__ "(kind=REAL64)"
#            elif __Key_kind__ == 128
#                define __Key_KINDLEN__(context) (kind=REAL128)
#                define __Key_kindlen_string__ "(kind=REAL128)"
#            endif
#           if !defined(__Key_default__)
#               define __Key_default_scalar__ 0.
#           endif

#        elif __Key_type_id__ == __DOUBLE_PRECISION__

#            define __Key_type__ double precision
#            define __Key_name__ "double precision"
#            if !defined(__Key_default__)
#                define __Key_default_scalar__ 0.
#            endif

#        elif __Key_type_id__ == __CHARACTER__

#            define __Key_type__ character
#            define __Key_name__ "character"
#            if __Key_kind__ > 1
#                define __Key_deferred__
#                define __Key_KINDLEN__(context) (len=context)
#                define __Key_kindlen_string__ "(len=:)"
#                if !defined(__Key_default__)
#                    define __Key_default_scalar__ ""
#                endif
#            else
#                if !defined(__Key_default__)
#                    define __Key_default_scalar__ ""
#                endif
#            endif

#        endif

#    endif

#else
! User defined derived type (or C_PTR, etc)

#    define __Key_type__ __Key
#    ifdef __Key_name
#        define __Key_name__ __Key_name
#    endif
#    ifdef __Key_polymorphic
#        define __Key_polymorphic__
#        define __Key_DECLARE__(t,kindlen) class(__IDENTITY(t)__IDENTITY(kindlen))
#        define __Key_NAME__(name,kindlen) "class("//name//kindlen//")"
#    else
#        define __Key_DECLARE__(t,kindlen) type(__IDENTITY(t)__IDENTITY(kindlen))
#        define __Key_NAME__(name,kindlen) "type("//name//kindlen//")"
#    endif
#    if defined(__Key_default)
#       define __Key_default_scalar__ __Key_default
#    endif

#endif

#ifdef __Key_KINDLEN
#    define __Key_KINDLEN__(context)  __Key_KINDLEN(context)
#else
#    ifndef __Key_KINDLEN__
#        define __Key_KINDLEN__(context)
#    endif
#endif

#ifdef __Key_kindlen_dummy
#    define __Key_kindlen_dummy__ __Key_kindlen_dummy
#else
#    define __Key_kindlen_dummy__ __Key_KINDLEN__(*)
#endif

#ifdef __Key_kindlen_component
#    define __Key_kindlen_component__ __Key_kindlen_component
#else
#    define __Key_kindlen_component__ __Key_KINDLEN__(:)
#endif

#ifdef __Key_kindlen_string
#    define __Key_kindlen_string__ __Key_kindlen_string
#else
#    ifndef __Key_kindlen_string__
#        define __Key_kindlen_string__ ""
#    endif
#endif

#ifdef __Key_rank
#    if __Key_rank == 1
#        define __Key_dimension_result__ , dimension(:)
#        define __Key_rank_string__ "1"
#        define __Key_shape_string__ ", dimension(:)"
#    elif __Key_rank == 2
#        define __Key_dimension_result__ , dimension(:,:)
#        define __Key_rank_string__ "2"
#        define __Key_shape_string__ ", dimension(:,:)"
#    elif __Key_rank == 3
#        define __Key_dimension_result__ , dimension(:,:,:)
#        define __Key_rank_string__ "3"
#        define __Key_shape_string__ ", dimension(:,:,:)"
#    elif __Key_rank == 4
#        define __Key_dimension_result__ , dimension(:,:,:,:)
#        define __Key_rank_string__ "4"
#        define __Key_shape_string__ ", dimension(:,:,:,:)"
#    elif __Key_rank == 5
#        define __Key_dimension_result__ , dimension(:,:,:,:,:)
#        define __Key_rank_string__ "5"
#        define __Key_shape_string__ ", dimension(:,:,:,:,:)"
#    elif __Key_rank == 6
#        define __Key_dimension_result__ , dimension(:,:,:,:,:,:)
#        define __Key_rank_string__ "6"
#        define __Key_shape_string__ ", dimension(:,:,:,:,:,:)"
#    elif __Key_rank == 7
#        define __Key_dimension_result__ , dimension(:,:,:,:,:,:,:)
#        define __Key_rank_string__ "7"
#        define __Key_shape_string__ ", dimension(:,:,:,:,:,:,:)"
#    endif
#    if defined(__Key_shape)
         ! fixed shape       
#        define __Key_dimension_component__ , __IDENTITY(dimension)__IDENTITY(__Key_shape)
#        ifdef __Key_shape_string
#            define __Key_dimension_string__ ", "//__Key_shape_string
#        else
#            define __Key_dimension_string__ ", dimension(rank<"//__Key_rank_string__//">)"
#        endif
#        ifndef __Key_default__
#            define __Key_default__ __Key_default_scalar__
#        endif
#    else
         ! deferred shape
#        define __Key_dimension_component__ __Key_dimension_result__
#        define __Key_dimension_string__ __Key_shape_string__
#        ifndef __Key_default__
#            define __Key_default__ reshape([__Key_type__ :: ],spread(0,1,__Key_rank))
#        endif
#    endif
#    define __Key_dimension_dummy__ __Key_dimension_component__


#else
! Scalar
#    define __Key_dimension_result__
#    define __Key_dimension_component__
#    define __Key_dimension_dummy__
#    define __Key_dimension_string__ ""
#    ifdef __Key_default_scalar__
#        define __Key_default__ __Key_default_scalar__
#    endif
#endif

#if defined(__Key_deferred) && !defined(__Key_deferred__)
#   define __T_deferred__
#endif

#if defined(__Key_deferred__) || defined(__Key_polymorphic__) || (__Key_rank > 0)
#else
#    define __Key_listable__
#endif

#if defined(__Key_deferred__) || defined(__Key_polymorphic__) || (defined(__Key_rank) && !defined(__Key_shape))
#    define __Key_allocatable__
#    define __Key_allocatable_attr__ , allocatable
#    define __Key_allocatable_string__ ", allocatable"
#else
#    define __Key_allocatable_attr__
#    define __Key_allocatable_string__ ""
#endif

! Intel fpp has issues with comma in a macro argument, so we do something a bit brute force here
#ifdef __Key_allocatable__
#    define __Key_declare_component__ __Key_DECLARE__(__Key_type__,__Key_kindlen_component__)__Key_dimension_component__, allocatable
#else
#    define __Key_declare_component__ __Key_DECLARE__(__Key_type__,__Key_kindlen_component__)__Key_dimension_component__
#endif
#define __Key_declare_result__ __Key_DECLARE__(__Key_type__,__Key_kindlen_component__)__Key_dimension_result__
#define __Key_declare_dummy__ __Key_DECLARE__(__Key_type__,__Key_kindlen_dummy__)__Key_dimension_dummy__
#undef tmp

#ifdef __Key_name__
#    define __Key_declare_string__ __Key_NAME__(__Key_name__,__Key_kindlen_string__)//__Key_dimension_string__//__Key_allocatable_string__
#endif

! If user defines __Key_EQ we assume that it is elemental
! for use in array comparisons.   If there is ever a reasonable
! situation that violates this assumption, then a new token
! will need to be added to deactivate this assumption.
#ifdef __Key_EQ
#    define __Key_EQ__(lhs,rhs) __Key_EQ(lhs,rhs)
#elif defined(__Key_EQ_SCALAR__)
#    if __Key_rank == 0
#        define __Key_EQ__(lhs,rhs) __Key_EQ_SCALAR__(lhs,rhs)
#    elif defined(__Key_shape)
#        define __Key_EQ__(lhs,rhs) all(__Key_EQ_SCALAR__([lhs],[rhs]))
#    else
! Must be careful about lack of short-circuit rules in Fortran.   Can only compare
! arrays of same shape, so we use reshape to compare the first N elements (always safe) as well as comparing shapes.
#        define __Key_EQ__(lhs,rhs) all(shape(lhs)==shape(rhs)).and.all(reshape(lhs,[min(size(lhs),size(rhs))])==reshape(lhs,[min(size(lhs),size(rhs))]))
#    endif
#endif

#ifdef __Key_LT
#    define __Key_LT__(lhs,rhs) __Key_LT(lhs,rhs)
#elif defined(__Key_LT_SCALAR__)
#    if __Key_rank == 0
#        define __Key_LT__(lhs,rhs) __Key_LT_SCALAR__(lhs,rhs)
#    endif
#endif


#ifdef __Key_FREE
#    define __Key_FREE__(x)  __Key_FREE(x)
#else
#    ifdef __Key_allocatable__
#        define __Key_FREE__(x)  deallocate(x)
#    else
#        define __Key_FREE__(x)
#    endif
#endif

#ifdef __Key_MOVE
#    define  __Key_MOVE__(lhs,rhs)  __Key_MOVE(lhs,rhs)
#else
#    ifdef __Key_allocatable__
#        define  __Key_MOVE__(lhs,rhs)  call move_alloc(from=rhs,to=lhs)
#    else
#        define  __Key_MOVE__(lhs,rhs)  lhs=rhs
#    endif
#endif


#ifdef __Key_COPY
#    define  __Key_COPY__(lhs,rhs)  __Key_COPY(lhs,rhs)
#else
#    if defined(__Key_polymorphic__)
#        define __Key_COPY__(lhs,rhs) allocate(lhs, source=rhs)
#    else
#        define __Key_COPY__(lhs,rhs) lhs=rhs
#    endif
#endif

