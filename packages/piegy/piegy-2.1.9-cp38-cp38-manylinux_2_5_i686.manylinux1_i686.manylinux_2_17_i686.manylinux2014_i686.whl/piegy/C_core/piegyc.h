// piegyc.h
// piegy simulation module written in c
#ifndef PIEGYC_H
#define PIEGYC_H

#include <stdbool.h>
#include <stdlib.h>


typedef struct model_t {
    size_t N;
    size_t M;
    double maxtime;
    double record_itv;
    size_t sim_time;

    bool boundary;

    // 3D arrays flattened to 1D for C
    // Sizes: N * M * 2, N * M * 4, N * M * 6
    uint32_t* I;
    double* X;
    double* P;

    int32_t print_pct; 
    int32_t seed;  // -1 for none

    // vars for data storage
    bool data_empty;
    size_t max_record;
    size_t arr_size;  // size of U, V, U_pi, V_pi, equals N * M * max_record
    uint32_t compress_itv;
    double* U1d;
    double* V;
    double* U_pi;
    double* V_pi;
} model_t;

bool mod_init(model_t* mod, size_t N, size_t M,
                double maxtime, double record_itv, size_t sim_time, bool boundary,
                const uint32_t* I, const double* X, const double* P,
                int32_t print_pct, int32_t seed);
void mod_free_py(model_t* mod);

void run(model_t* mod, char* message, size_t msg_len);



#endif  // PIEGYC_H
