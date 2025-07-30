/**
 * This .h defines the simulation functions in piegy.simulation
*/

#ifndef SIM_FUNCS
#define SIM_FUNCS

#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include "patch.h"
#include "model.h"



// upper bound for RNG is 2^24 + 1
#define RAND_UPPER_PLUS_2 (double) (0xffffffu + 2)

// directions of migration
// so that 3 - mig_dir = reflection of it. Used to track neighbors
// the actual implementation of signals still uses this order: up, down, left, right
#define MIG_UP 0
#define MIG_DOWN 1
#define MIG_LEFT 2
#define MIG_RIGHT 3

// results of single_test
#define SUCCESS 0
#define GENERAL_FAILURE 1
#define SMALL_MAXTIME 2
#define OVERFLOW 3

// where exp(x) reaches overflow bound (just below it)
#define EXP_OVERFLOW_BOUND 700


static uint64_t pcg_state = 0;
static uint64_t pcg_inc = 0;

 


/**
 * index of patch in find_patch
*/
typedef struct patch_picked_t {
    size_t i;
    size_t j;
    double current_sum;
} patch_picked_t;

/**
 * index & event number in make_signal_*
*/
typedef struct signal_t {
    // does the signal only have the first patch?
    bool only_first;

    // the first patch
    size_t i1;
    size_t j1;
    size_t ij1;  // i1 * M + j1
    uint8_t e1;

    // the second patch
    size_t i2;
    size_t j2;
    size_t ij2;
    uint8_t e2;
} signal_t;



/**
 * Defined in .c
*/
static void find_nb_zero_flux(size_t* restrict nb, size_t i, size_t j, size_t N, size_t M, size_t NM);
static void find_nb_periodical(size_t* restrict nb, size_t i, size_t j, size_t N, size_t M, size_t NM);
static double single_init(const model_t* mod, patch_t* world, size_t* nb_indices, 
                    double* patch_rates, double* sum_rates_by_row, double* sum_rates, signal_t* sig_p, patch_picked_t* picked_p) ;
static void single_test(model_t* restrict mod, uint32_t update_sum_frequency, uint32_t* result, char* message);
static void single_test_free(patch_t* world, size_t* nb_indices, double* patch_rates, double* sum_rates_by_row);
void run(model_t* mod, char* message, size_t msg_len);


/**
 * Inline Functions
*/

static inline double random01() {
    // generate a 24 bit random int, then convert to a (0, 1) ranged double
    uint32_t r1 = rand() & 0x7fff;  // RAND_MAX is different across machines, ensure 15 bits
    uint32_t r2 = rand() & 0x7fff;

    double r_combined = ((r1 >> 3) << 12) + (r2 >> 3);  // discard the lower 3 bits, which are unstable
    return (r_combined + 1) / RAND_UPPER_PLUS_2;
}

/**
 * patch functions
*/

static inline void update_pi_k(patch_t* restrict p, const double* restrict M_start, const double* restrict P_kappa_start) {
    // M_start: start index of patch (i, j)'s matrix
    // P_kappa_start: start index of patch (i, j)'s kappa values (the 4th and 5th, 0-indexed)

    double U = (double) p->U;
    double V = (double) p->V;
    double sum_minus_1 = U + V - 1.0;

    if (sum_minus_1 > 0) {
        if (U != 0) {
            p->U_pi = ((U - 1) / sum_minus_1) * M_start[0] +
                      (V / sum_minus_1) * M_start[1];
        } else {
            p->U_pi = 0.0;
        }

        if (V != 0) {
            p->V_pi = (U / sum_minus_1) * M_start[2] +
                      ((V - 1) / sum_minus_1) * M_start[3];
        } else {
            p->V_pi = 0.0;
        }

    } else {
        p->U_pi = 0.0;
        p->V_pi = 0.0;
    }

    p->pi_death_rates[0] = fabs(U * p->U_pi);
    p->pi_death_rates[1] = fabs(V * p->V_pi);

    p->pi_death_rates[2] = P_kappa_start[0] * U * (sum_minus_1 + 1.0);
    p->pi_death_rates[3] = P_kappa_start[1] * V * (sum_minus_1 + 1.0);

    p->sum_pi_death_rates = 0.0;
    for (size_t i = 0; i < 4; i++) {
        p->sum_pi_death_rates += p->pi_death_rates[i];
    }
}


static inline void update_mig_one(patch_t* restrict p, const double* restrict P_start, uint8_t nb_loc) {
    // update mig rate for one direction
    // P_start: start index of p's patch variables, i.e., ij * 6
    // nb_loc: location of neighbor, up, down, left, right

    double mu1_U = P_start[0] * (double)p->U;
    double mu2_V = P_start[1] * (double)p->V;
    double* p_U_weight = p->U_weight;
    double* p_V_weight = p->V_weight;

    patch_t* nbi = p->nb[nb_loc];
    p->sum_U_weight -= p_U_weight[nb_loc];
    p->sum_V_weight -= p_V_weight[nb_loc];

    switch(nb_loc) {
        case MIG_UP:
            p_U_weight[MIG_UP] = 1.0 + exp(P_start[2] * nbi->U_pi);
            p_V_weight[MIG_UP] = 1.0 + exp(P_start[3] * nbi->V_pi);
            break;
        case MIG_DOWN:
            p_U_weight[MIG_DOWN] = 1.0 + exp(P_start[2] * nbi->U_pi);
            p_V_weight[MIG_DOWN] = 1.0 + exp(P_start[3] * nbi->V_pi);
            break;
        case MIG_LEFT:
            p_U_weight[MIG_LEFT] = 1.0 + exp(P_start[2] * nbi->U_pi);
            p_V_weight[MIG_LEFT] = 1.0 + exp(P_start[3] * nbi->V_pi);
            break;
        default:
            p_U_weight[MIG_RIGHT] = 1.0 + exp(P_start[2] * nbi->U_pi);
            p_V_weight[MIG_RIGHT] = 1.0 + exp(P_start[3] * nbi->V_pi);
            break;
    }
    p->sum_U_weight += p_U_weight[nb_loc];
    p->sum_V_weight += p_V_weight[nb_loc];

    double mu1_U_divide_sum = mu1_U / p->sum_U_weight;
    double mu2_V_divide_sum = mu2_V / p->sum_V_weight;

    for (size_t i = 0; i < 4; i++) {
        p->mig_rates[i] = mu1_U_divide_sum * p_U_weight[i];
        p->mig_rates[i + 4] = mu2_V_divide_sum * p_V_weight[i];
    }

}



static inline void update_mig_all(patch_t* restrict p, const double* restrict P_start) {
    // update migration rate for all directions
    double mu1_U = P_start[0] * (double)p->U;
    double mu2_V = P_start[1] * (double)p->V;

    double* p_U_weight = p->U_weight;
    double* p_V_weight = p->V_weight;

    p->sum_U_weight = 0.0;
    p->sum_V_weight = 0.0;

    double w1 = P_start[2];
    double w2 = P_start[3];

    for (uint8_t i = 0; i < 4; i++) {
        patch_t* nbi = p->nb[i];

        if (nbi) {
            // not NULL
            p_U_weight[i] = 1.0 + exp(w1 * nbi->U_pi);
            p_V_weight[i] = 1.0 + exp(w2 * nbi->V_pi);

            p->sum_U_weight += p_U_weight[i];
            p->sum_V_weight += p_V_weight[i];
        }
    }

    double mu1_U_divide_sum = mu1_U / p->sum_U_weight;
    double mu2_V_divide_sum = mu2_V / p->sum_V_weight;

    for (uint8_t i = 0; i < 4; i++) {
        p->mig_rates[i] = mu1_U_divide_sum * p_U_weight[i];
        p->mig_rates[i + 4] = mu2_V_divide_sum * p_V_weight[i];
    }

    p->sum_mig_rates = mu1_U + mu2_V;
}



static inline size_t find_event(const patch_t* restrict p, double expected_sum) {
    size_t event = 0;
    double current_sum;

    //if (expected_sum > (p->sum_pi_death_rates + p->sum_mig_rates)) {
    //    fprintf(stderr, "Bug: patch rate not enough in find_event.\n");
    //}

    if (expected_sum < p->sum_pi_death_rates) {
        // First 4 events (payoff and death)
        current_sum = 0.0;
        while (current_sum < expected_sum) {
            current_sum += p->pi_death_rates[event];
            event++;
        }
        event--;  // step back to correct event index
    } else {
        // Last 8 events (migration)2
        current_sum = p->sum_pi_death_rates;
        while (current_sum < expected_sum) {
            current_sum += p->mig_rates[event];
            event++;
        }
        event += 3;  // -1 and then +4
    }

    return event;
}


static inline void change_popu(patch_t* restrict p, uint8_t s) {
    switch (s) {
        case 0:
            // Migration IN for U
            p->U += 1;
            return;
        case 1:
            // Migration OUT / death due to carrying capacity for U
            p->U -= (p->U > 0);
            return;
        case 2:
            // Natural birth/death for U due to payoff
            if (p->U_pi > 0.0) {
                p->U += 1;
            } else if (p->U > 0) {
                p->U -= 1;
            }
            return;
        case 3:
            // Migration IN for V
            p->V += 1;
            return;
        case 4:
            // Migration OUT / death due to carrying capacity for V
            p->V -= (p->V > 0);
            return;
        default:
            // Natural birth/death for V due to payoff
            if (p->V_pi > 0.0) {
                p->V += 1;
            } else if (p->V > 0) {
                p->V -= 1;
            }
            return;
        //default:
        //    fprintf(stderr, "Bug: invalid event number in change_popu: %hhu\n", s);
        //    return;
    }
}


/**
 * Main Simulation Functions
*/

static inline void find_patch(patch_picked_t* restrict picked, double expected_sum, const double* restrict patch_rates, const double* restrict sum_rates_by_row, double sum_rates, size_t N, size_t M) {
    double current_sum = 0;
    size_t row = 0;
    size_t col = 0;

    // Find row
    if (expected_sum < sum_rates * 0.5) {
        current_sum = 0.0;
        row = 0;
        while (current_sum < expected_sum) {
            current_sum += sum_rates_by_row[row];
            row++;
        }
        row--;
        current_sum -= sum_rates_by_row[row];
    } else {
        current_sum = sum_rates;
        row = N - 1;
        while (current_sum > expected_sum) {
            current_sum -= sum_rates_by_row[row];
            row--;
        }
        row++;
    }

    size_t row_M = row * M;

    // Find col in that row
    if ((expected_sum - current_sum) < sum_rates_by_row[row] * 0.5) {
        col = 0;
        while (current_sum < expected_sum) {
            current_sum += patch_rates[row_M + col];
            col++;
        }
        col--;
        current_sum -= patch_rates[row_M + col];
    } else {
        current_sum += sum_rates_by_row[row];
        col = M - 1;
        while (current_sum > expected_sum) {
            current_sum -= patch_rates[row_M + col];
            col--;
        }
        col++;
    }

    picked->i = row;
    picked->j = col;
    picked->current_sum = current_sum;
}



static inline void make_signal_zero_flux(size_t i, size_t j, uint8_t e, signal_t* restrict signal) {
    // this is always the case for the first one
    signal->i1 = i;
    signal->j1 = j;

    switch (e) {
        case 0:
            signal->e1 = 2;
            signal->only_first = true;
            return;
        case 1:
            signal->e1 = 5;
            signal->only_first = true;
            return;
        case 2:
            signal->e1 = 1;
            signal->only_first = true;
            return;
        case 3:
            signal->e1 = 4;
            signal->only_first = true;
            return;
        case 4:
            signal->e1 = 1;
            signal->i2 = i - 1;
            signal->j2 = j;
            signal->e2 = 0;
            signal->only_first = false;
            return;
        case 5:
            signal->e1 = 1;
            signal->i2 = i + 1;
            signal->j2 = j;
            signal->e2 = 0;
            signal->only_first = false;
            return;
        case 6:
            signal->e1 = 1;
            signal->i2 = i;
            signal->j2 = j - 1;
            signal->e2 = 0;
            signal->only_first = false;
            return;
        case 7:
            signal->e1 = 1;
            signal->i2 = i;
            signal->j2 = j + 1;
            signal->e2 = 0;
            signal->only_first = false;
            return;
        case 8:
            signal->e1 = 4;
            signal->i2 = i - 1;
            signal->j2 = j;
            signal->e2 = 3;
            signal->only_first = false;
            return;
        case 9:
            signal->e1 = 4;
            signal->i2 = i + 1;
            signal->j2 = j;
            signal->e2 = 3;
            signal->only_first = false;
            return;
        case 10:
            signal->e1 = 4;
            signal->i2 = i;
            signal->j2 = j - 1;
            signal->e2 = 3;
            signal->only_first = false;
            return;
        default:
            signal->e1 = 4;
            signal->i2 = i;
            signal->j2 = j + 1;
            signal->e2 = 3;
            signal->only_first = false;
            return;
        //default:
        //    fprintf(stderr, "Bug: invalid case in make_signal_zf, i, j, e: %zu, %zu, %hhu\n", i, j, e);
        //    return;
    }
}



static inline void make_signal_periodical(size_t N, size_t M, size_t i, size_t j, uint8_t e, signal_t* restrict signal) {
    // this is always the case for the first one
    signal->i1 = i;
    signal->j1 = j;

    switch (e) {
        case 0:
            signal->e1 = 2;
            signal->only_first = true;
            return;
        case 1:
            signal->e1 = 5;
            signal->only_first = true;
            return;
        case 2:
            signal->e1 = 1;
            signal->only_first = true;
            return;
        case 3:
            signal->e1 = 4;
            signal->only_first = true;
            return;
        case 4:
            signal->e1 = 1;
            signal->i2 = i != 0 ? i - 1 : N - 1;
            signal->j2 = j;
            signal->e2 = 0;
            signal->only_first = false;
            return;
        case 5:
            signal->e1 = 1;
            signal->i2 = i != N - 1 ? i + 1 : 0;
            signal->j2 = j;
            signal->e2 = 0;
            signal->only_first = false;
            return;
        case 6:
            signal->e1 = 1;
            signal->i2 = i;
            signal->j2 = j != 0 ? j - 1 : M - 1;
            signal->e2 = 0;
            signal->only_first = false;
            return;
        case 7:
            signal->e1 = 1;
            signal->i2 = i;
            signal->j2 = j != M - 1 ? j + 1 : 0;
            signal->e2 = 0;
            signal->only_first = false;
            return;
        case 8:
            signal->e1 = 4;
            signal->i2 = i != 0 ? i - 1 : N - 1;
            signal->j2 = j;
            signal->e2 = 3;
            signal->only_first = false;
            return;
        case 9:
            signal->e1 = 4;
            signal->i2 = i != N - 1 ? i + 1 : 0;
            signal->j2 = j;
            signal->e2 = 3;
            signal->only_first = false;
            return;
        case 10:
            signal->e1 = 4;
            signal->i2 = i;
            signal->j2 = j != 0 ? j - 1 : M - 1;
            signal->e2 = 3;
            signal->only_first = false;
            return;
        default:
            signal->e1 = 4;
            signal->i2 = i;
            signal->j2 = j != M - 1 ? j + 1 : 0;
            signal->e2 = 3;
            signal->only_first = false;
            return;
        //default:
        //    fprintf(stderr, "Bug: invalid case in make_signal_pr, i, j, e: %zu, %zu, %hhu\n", i, j, e);
        //    return;
    }
}


static inline bool nb_need_change(size_t nb_idx, size_t sij1, size_t sij2) {
    // a nb doesn't need change only if two patches are updated

    // or, can try this 1-line version
    // return (nb_idx != sij1) && (nb_idx != sij2);
    if ((nb_idx == sij1) || (nb_idx == sij2)) {
        return false;
    }
    return true;  // need to change
}


#endif
