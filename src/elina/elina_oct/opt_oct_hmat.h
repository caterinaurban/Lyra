/*
 *
 *  This source file is part of ELINA (ETH LIbrary for Numerical Analysis).
 *  ELINA is Copyright © 2018 Department of Computer Science, ETH Zurich
 *  This software is distributed under GNU Lesser General Public License Version 3.0.
 *  For more information, see the ELINA project website at:
 *  http://elina.ethz.ch
 *
 *  THE SOFTWARE IS PROVIDED "AS-IS" WITHOUT ANY WARRANTY OF ANY KIND, EITHER
 *  EXPRESS, IMPLIED OR STATUTORY, INCLUDING BUT NOT LIMITED TO ANY WARRANTY
 *  THAT THE SOFTWARE WILL CONFORM TO SPECIFICATIONS OR BE ERROR-FREE AND ANY
 *  IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
 *  TITLE, OR NON-INFRINGEMENT.  IN NO EVENT SHALL ETH ZURICH BE LIABLE FOR ANY     
 *  DAMAGES, INCLUDING BUT NOT LIMITED TO DIRECT, INDIRECT,
 *  SPECIAL OR CONSEQUENTIAL DAMAGES, ARISING OUT OF, RESULTING FROM, OR IN
 *  ANY WAY CONNECTED WITH THIS SOFTWARE (WHETHER OR NOT BASED UPON WARRANTY,
 *  CONTRACT, TORT OR OTHERWISE).
 *
 */


#ifndef __OPT_OCT_HMAT_H
#define __OPT_OCT_HMAT_H

#ifdef __cplusplus
extern "C" {
#endif



#include "opt_oct_internal.h"
#include "opt_oct_closure_comp_sparse.h"
#include "opt_oct_incr_closure_comp_sparse.h"


#if defined(VECTOR)

#include "opt_oct_closure_dense.h"
#include "opt_oct_incr_closure_dense.h"


#else

#include "opt_oct_closure_dense_scalar.h"
#include "opt_oct_incr_closure_dense_scalar.h"

#endif

#if defined(TIMING)
	#define start_timing()				\
		tsc_counter start, end;				\
		double cycles;					\
		CPUID();					\
		RDTSC(start)						

  	#define record_timing(counter)		\
		RDTSC(end);				\
  		CPUID();				\
  		cycles = (double)(COUNTER_DIFF(end, start));	\
  		counter += cycles	
	extern double closure_time;
	extern double copy_time;
	extern double is_equal_time;
	extern double is_lequal_time;
	extern double permute_dimension_time;
	extern double top_time;
	extern double meet_time;
	extern double join_time;
	extern double add_dimension_time;
	extern double widening_time;
	extern double free_time;
	extern double forget_array_time;
	extern double meet_lincons_time;
	extern double oct_to_box_time;
	extern double alloc_time;
	extern double is_top_time;
	extern double expand_time;
	extern double fold_time;
	extern double sat_lincons_time;
	extern double assign_linexpr_time;
	extern double oct_is_unconstrained_time;
        extern double narrowing_time;
#endif

#define min fmin
#define max fmax



void opt_hmat_free(opt_oct_mat_t *m);
opt_oct_mat_t * opt_hmat_alloc_top(int dim);
opt_oct_mat_t *opt_hmat_copy(opt_oct_mat_t * src, int size);
void opt_hmat_set_array(double *dest, double *src, int size);
bool opt_hmat_strong_closure(opt_oct_mat_t *m, int dim);
bool is_top_half(opt_oct_mat_t *m, int dim);
bool is_equal_half(opt_oct_mat_t *m1, opt_oct_mat_t *m2, int dim);
bool is_lequal_half(opt_oct_mat_t *m1, opt_oct_mat_t *m2, int dim);
void meet_half(opt_oct_mat_t *m, opt_oct_mat_t *m1, opt_oct_mat_t *m2, int dim, bool destructive);
void forget_array_half(opt_oct_mat_t *m, elina_dim_t *arr,int dim, int arr_dim, bool project);
void opt_hmat_forget_var(opt_oct_mat_t* oo, size_t dim, size_t d);
void join_half(opt_oct_mat_t *m, opt_oct_mat_t *m1, opt_oct_mat_t *m2, int dim, bool destructive);
void opt_hmat_addrem_dimensions(opt_oct_mat_t * dst, opt_oct_mat_t* src,elina_dim_t* pos, int nb_pos,int mult, int dim, bool add);
void opt_hmat_permute(opt_oct_mat_t* dst, opt_oct_mat_t* src,int dst_dim, int src_dim,elina_dim_t* permutation);
opt_oct_t* opt_oct_expand(elina_manager_t* man, bool destructive, opt_oct_t* o, elina_dim_t dim, size_t n);
opt_oct_t* opt_oct_fold(elina_manager_t* man,bool destructive, opt_oct_t* o,elina_dim_t* tdim,size_t size);
void widening_half(opt_oct_mat_t *oo, opt_oct_mat_t *oo1, opt_oct_mat_t *oo2, int dim);
void widening_thresholds_half(opt_oct_mat_t *oo, opt_oct_mat_t *oo1, opt_oct_mat_t *oo2, double *thresholds, int num_thresholds, int dim);
void narrowing_half(opt_oct_mat_t *oo, opt_oct_mat_t *oo1, opt_oct_mat_t *oo2, int dim);
opt_uexpr opt_oct_uexpr_of_linexpr(opt_oct_internal_t* pr, double* dst, elina_linexpr0_t* e, int intdim, int dim);
bool opt_hmat_add_lincons(opt_oct_internal_t* pr, opt_oct_mat_t* oo, int intdim, int dim, elina_lincons0_array_t* ar, bool* exact, bool* respect_closure);
void opt_oct_fprint(FILE* stream, elina_manager_t* man, opt_oct_t * a,char** name_of_dim);
opt_oct_mat_t* opt_hmat_alloc(int size);
void opt_hmat_assign(opt_oct_internal_t* pr, opt_uexpr u, opt_oct_mat_t* oo, size_t dim, size_t d, bool* respect_closure);

void convert_to_dense_mat(opt_oct_mat_t * oo, int dim,bool flag);

static inline void ini_relation(double *m, int i, int j, int dim){
	if((i>=dim) || (j >= dim)){
		return;
	}
	int ind1 = opt_matpos2(2*i,2*j);
	int ind2 = opt_matpos2(2*i+1, 2*j+1);
	if(i==j){
		m[ind1] = 0;
		m[ind2] = 0;
	}
	else{
		m[ind1] = INFINITY;
		m[ind2] = INFINITY;
	}
	int ind3 = opt_matpos2(2*i, 2*j+1);
	m[ind3] = INFINITY;
	int ind4 = opt_matpos2(2*i+1, 2*j);
	m[ind4] = INFINITY;
}

static inline void ini_self_relation(double *m, int i, int dim){
	if((i>=dim)){
		return;
	}
	
	int ind1 = opt_matpos2(2*i,2*i);
	int ind2 = opt_matpos2(2*i+1, 2*i+1);
	//if(m[ind1] != INFINITY){
		m[ind1] = 0;
	//}
	//if(m[ind2] != INFINITY){
		m[ind2] = 0;
	//}
	int ind3 = opt_matpos2(2*i, 2*i+1);
	m[ind3] = INFINITY;
	int ind4 = opt_matpos2(2*i+1, 2*i);
	m[ind4] = INFINITY;
}


static inline void ini_comp_relations(double * result, comp_list_t * cl1, comp_list_t *cl2,int dim){
	comp_t *c1 = cl1->head;
	while(c1!=NULL){
		comp_t *c2 = cl2->head;
		int i = c1->num;
		while(c2!=NULL){
			int j = c2->num;
			if(i!=j){
				ini_relation(result,i,j,dim);
			}
			c2 = c2->next;
		}
		c1 = c1->next;
	}
}

static inline void ini_comp_elem_relation(double * m, comp_list_t * cl1, int j,int dim){
	comp_t *c1 = cl1->head;
	while(c1!=NULL){
		int i = c1->num;
		if(i!=j){
			ini_relation(m,i,j,dim);
		}
		c1 = c1->next;
	}
}

static inline void handle_binary_relation(double *m,array_comp_list_t *acl, int i, int j, int dim ){
	comp_list_t * li = find(acl,i);
	comp_list_t * lj = find(acl,j);
	if(li==NULL){
		ini_relation(m,i,i,dim);
		if(lj==NULL){
			ini_relation(m,j,j,dim);
			ini_relation(m,i,j,dim);
		}
		else{
			ini_comp_elem_relation(m,lj,i,dim);
		}
	}
	else{
		if(lj==NULL){
			ini_relation(m,j,j,dim);
			ini_comp_elem_relation(m,li,j,dim);
		}
		else{
			if(li!=lj){
				ini_comp_relations(m,li,lj,dim);
			}
		}
	}

} 

static inline bool check_trivial_relation(double *m, int i, int j){
	int ind1 = opt_matpos2(2*i,2*j);
	int ind2 = opt_matpos2(2*i+1, 2*j+1);
	if(i==j){
		if(m[ind1] != 0){
			return false;
		}
		if(m[ind2] != 0){
			return false;
		}
	}
	else{
		if(m[ind1] != INFINITY){
			return false;
		}
		if(m[ind2] != INFINITY){
			return false;
		}
	}
	int ind3 = opt_matpos2(2*i, 2*j+1);
	if(m[ind3] != INFINITY){
		return false;
	}
	int ind4 = opt_matpos2(2*i+1, 2*j);
	if(m[ind4] != INFINITY){
		return false;
	}
	return true;
}



static inline void handle_binary_relation_list(double *m,array_comp_list_t *acl, comp_list_t *cl, int i, int j, int dim ){
	comp_list_t * li = find(acl,i);
	comp_list_t * lj = find(acl,j);
	if(li==NULL){
		ini_relation(m,i,i,dim);
		if(lj==NULL){
			ini_relation(m,j,j,dim);
			ini_comp_elem_relation(m,cl,j,dim);
		}
		else{
			ini_comp_elem_relation(m,lj,i,dim);
		}
	}
	else{
		if(lj==NULL){
			ini_relation(m,j,j,dim);
			ini_comp_elem_relation(m,li,j,dim);
		}
		else{
			if(li!=lj){
				ini_comp_relations(m,li,lj,dim);
			}
		}
	}

} 


static inline void print_opt_oct_mat(opt_oct_mat_t *oo,int dim){
	double *m = oo->mat;
	print_array_comp_list(oo->acl,dim);
	comp_list_t *cl = oo->acl->head;
	while(cl != NULL){
		int comp_size = cl->size;
		unsigned short int * ca = to_sorted_array(cl,dim);
		for(int i = 0; i < 2*comp_size; i++){
			int i1 = (i%2==0)? 2*ca[i/2] : 2*ca[i/2]+1;
			for(int j = 0; j < 2*comp_size; j++){
				int j1 = (j%2==0)? 2*ca[j/2] : 2*ca[j/2]+1;
				int ind = opt_matpos2(i1,j1);
				fprintf(stdout,"%g\t",m[ind]);
			}
			fprintf(stdout,"\n");
		}		
		fprintf(stdout,"\n");
		free(ca);
		cl = cl->next;
	}
	fprintf(stdout,"\n");
	fprintf(stdout,"\n");
	fprintf(stdout,"\n");
	fflush(stdout);
}

static inline void print_opt_hmat(double* d, int dim){
  
  if (!d) {
    printf("0\n");
    return;
  }
  printf("%d\n",dim);

 for (int i=0;i<2*dim;i++) {
    for (int j=0;j<2*dim;j++) {
     if (j) fprintf(stdout,"\t");
     fprintf(stdout,"%g",d[opt_matpos2(i,j)]);
    }
    fprintf(stdout,"\n");
  }
  //fprintf(stdout,"\n");
}

static inline void print_hmat(opt_oct_mat_t* oo, int dim){
	if(oo->is_dense){
		print_opt_hmat(oo->mat,dim);		
	}
	else{
		print_opt_oct_mat(oo,dim);
	}
}


#ifdef __cplusplus
}
#endif

#endif
