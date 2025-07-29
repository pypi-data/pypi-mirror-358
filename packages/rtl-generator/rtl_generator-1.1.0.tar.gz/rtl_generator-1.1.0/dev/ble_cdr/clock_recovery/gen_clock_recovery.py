f"""
Generate Clock Recovery RTL code
"""

import sys
from pathlib import Path
from typing import Dict, Generator

sys.path.append(str(Path(__file__).resolve().parent.parent))
from rtl_generator import *
from gen_ble_cdr import *


# User-defined imports, functions, and globals
import numpy as np


@generator_context
def include_clock_recovery(mf_clock_rec: bool, **kwargs) -> Generator[str, None, Dict]:
    rtl = matched_filter_clock_rec(**kwargs) if mf_clock_rec else paper_clock_rec(**kwargs)
    yield rtl.strip()
    return {}


@generator_context
def matched_filter_clock_rec(**kwargs) -> Generator[str, None, Dict]:
    """
    Include clock recovery computed using matched filter outputs
    """

    rtl = """
    localparam int PIPELINE_STAGES = 1;
    
    logic [$clog2(SAMPLE_RATE-1):0] sample_counter;
    logic p_mf_bit;
    
    always_ff @(posedge clk or negedge resetn) begin : detect_transition
        if (~resetn) begin
            sample_counter <= 0;
            p_mf_bit <= 0;
        end else if (en) begin
            if ((mf_bit ^ p_mf_bit) || (sample_counter == SAMPLE_RATE - 1)) begin
                sample_counter <= 0;
            end else begin
                sample_counter <= sample_counter + 1;
            end
            
            p_mf_bit <= mf_bit;
        end
    end
    
    assign symbol_clk = (sample_counter == ((SAMPLE_RATE - 1) >> 1));
    """.strip()

    yield rtl
    return {}


@generator_context
def paper_clock_rec(**kwargs) -> Generator[str, None, Dict]:
    """
    Include clock recovery computed using baseband samples (see 1990 paper)
    """
    rtl = """
    localparam int PIPELINE_STAGES = 1;
    localparam int E_K_SHIFT = /* #{(ek_shift)} */ 2 /* #{/(ek_shift)} */;
    localparam int TAU_SHIFT = /* #{(tau_shift)} */ 11 /* #{/(tau_shift)} */;
    localparam int SAMPLE_POS = /* #{sample_pos)} */ 2 /* #{/(sample_pos)} */;
    
    // Counter to schedule error calc due to preamble detection
    // Normally, error_calc_counter = 0, but when a preamble is detected, error_calc_counter = (SAMPLE_POS >> 1) + 1
    // Error calc is then scheduled to happen in the middle of the current symbol (when error_calc_counter == 1)
    logic [$clog2(SAMPLE_RATE):0] error_calc_counter, shift_counter;
    
    // Sample buffers to store samples used in error calculation
    // Samples are indexed as below, samples used are labeled with x. Start of symbol is marked with |, S is sample rate
    // S+2 S+1 S ... 2 1 0
    //  x   |  x     x | x
    localparam int BUFFER_SIZE = SAMPLE_RATE + 3;
    logic signed [BUFFER_SIZE-1:0][DATA_WIDTH-1:0] I_k, Q_k;
    
    // Variables to store the inputs to error calculation
    logic signed [DATA_WIDTH-1:0] i_1, q_1, i_2, q_2, i_3, q_3, i_4, q_4;
    
    // Variables to store error calculation results
    // #{(calculate_error_res)}
    localparam int  ERROR_RES = 18 + 0;
    // #{/(calculate_error_res)}
    localparam int TAU_RES = ERROR_RES - TAU_SHIFT;
    localparam int E_K_RES = ERROR_RES - E_K_SHIFT;
    localparam int D_TAU_RES = $clog2(SAMPLE_RATE + 1);
    logic signed [ERROR_RES-1:0] e_k, tau_int, tau_int_1, re1, re2, im1, im2, y1, y2;
    logic signed [E_K_RES-1:0] e_k_shifted;
    logic signed [TAU_RES-1:0] tau, tau_1;
    logic signed [D_TAU_RES-1:0] dtau;
    logic signed [ERROR_RES-1:0] i_1_sqr, q_1_sqr, i_2_sqr, q_2_sqr, i_3_sqr, q_3_sqr, i_4_sqr, q_4_sqr, iq_12, iq_34;
    
    integer re_correction = /* #{(re_correction)} */ 0 /* #{/(re_correction)} */;
    integer im_correction = /* #{(im_correction)} */ 0 /* #{/(im_correction)} */;
    logic do_error_calc;
    logic [D_TAU_RES-1:0] shift_counter_p1;
    
    always_comb begin : error_calculation
        // Combinational logic to assign buffer values to error calculation inputs
        i_1 = I_k[0 + SAMPLE_RATE];
        q_1 = Q_k[0 + SAMPLE_RATE];
        i_2 = I_k[0];
        q_2 = Q_k[0];
        i_3 = I_k[2 + SAMPLE_RATE];
        q_3 = Q_k[2 + SAMPLE_RATE];
        i_4 = I_k[2];
        q_4 = Q_k[2];
        
        // Combinational logic to compute error calculation
        i_1_sqr = i_1 * i_1;
        q_1_sqr = q_1 * q_1;
        i_2_sqr = i_2 * i_2;
        q_2_sqr = q_2 * q_2;
        i_3_sqr = i_3 * i_3;
        q_3_sqr = q_3 * q_3;
        i_4_sqr = i_4 * i_4;
        q_4_sqr = q_4 * q_4;
        iq_12 = i_1 * q_1 * i_2 * q_2;
        iq_34 = i_3 * q_3 * i_4 * q_4;
        
        re1 = (i_1_sqr - q_1_sqr) * (i_2_sqr - q_2_sqr) + (iq_12 << 2);
        re2 = (i_3_sqr - q_3_sqr) * (i_4_sqr - q_4_sqr) + (iq_34 << 2);
        im1 = ((i_2_sqr * i_1 * q_1) + (q_1_sqr * i_2 * q_2) - (i_1_sqr * i_2 * q_2) - (q_2_sqr * i_1 * q_1)) << 1;
        im2 = ((i_4_sqr * i_3 * q_3) + (q_3_sqr * i_4 * q_4) - (i_3_sqr * i_4 * q_4) - (q_4_sqr * i_3 * q_3)) << 1;
        
        // Compute y1 and y2 using correction factor
        y1 = (re_correction * re1) + (im_correction * im1);
        y2 = (re_correction * re2) + (im_correction * im2);
        
        // Compute error term
        e_k = y1 - y2;
        e_k_shifted = e_k[ERROR_RES-1:E_K_SHIFT];
        /* verilator lint_off WIDTHEXPAND */
        tau_int = tau_int_1 - e_k_shifted;
        /* verilator lint_on WIDTHEXPAND */
        tau = tau_int[ERROR_RES-1:TAU_SHIFT];
        
        // Determine if error calculation is scheduled
        shift_counter_p1 = (shift_counter + 1);
        do_error_calc = (error_calc_counter == 1) | (shift_counter_p1[D_TAU_RES-2:0] == dtau[D_TAU_RES-2:0]);
        
        // Output the symbol clock
        symbol_clk = (shift_counter == SAMPLE_POS);
    end
    
    always_ff @(posedge clk or negedge resetn) begin : update_state
        if (~resetn) begin
            tau_int_1 <= 0;
            tau_1 <= 0;
            dtau <= 0;
            shift_counter <= -PIPELINE_STAGES;
            error_calc_counter <= 0;
            I_k <= 0;
            Q_k <= 0;
        end else if (en) begin
            if (do_error_calc) begin
                // Store tau estimates and calculate dtau. Reset shift counter
                tau_int_1 <= tau_int;
                tau_1 <= tau;
                /* verilator lint_off WIDTHTRUNC */
                dtau <= (tau_1 - tau) >>> /* #{(correction_shift)} */ 0 /* #{/(correction_shift)} */;
                /* verilator lint_on WIDTHTRUNC */
                shift_counter <= 0;
            end else begin
                // Increment shift counter
                shift_counter <= shift_counter + 1;
            end
            
            // Decrement error calculation counter if error calculation is scheduled. Otherwise, schedule error calculation if preamble is detected
            if (error_calc_counter != 0) begin
                error_calc_counter <= error_calc_counter - 1;
            end else if (preamble_detected) begin
                error_calc_counter <= (SAMPLE_RATE >> 1) - SAMPLE_POS;
            end
            
            // Shift samples in buffer
            I_k <= {i_data, I_k[BUFFER_SIZE-1:1]};
            Q_k <= {q_data, Q_k[BUFFER_SIZE-1:1]};
        end
    end
    """.strip()

    yield rtl
    return {}


@generator_context
def calculate_error_res(**kwargs) -> Generator[str, None, Dict]:
    yield fill_in_template("localparam int ERROR_RES = #{(error_res)} + #{(correction_shift)};", **kwargs)
    return vars().get("__returned_dict__", {})


@generator_context
def error_res(adc_width: int, **kwargs) -> Generator[str, None, Dict]:
    """
    Calculate the error resoultion
    """
    error_res = 2 * (2 * adc_width + 1)
    yield str(error_res)
    return dict(error_res=error_res)


@generator_context
def re_correction(re_correction: Generator | str, **kwargs) -> Generator[str, None, Dict]:
    if callable(re_correction):
        if_correction(**kwargs)
        re_correction = vars().get("__returned_dict__", {}).get("re_correction", re_correction)
    yield str(re_correction)
    return vars().get("__returned_dict__", {})


@generator_context
def im_correction(im_correction: Generator | str, **kwargs) -> Generator[str, None, Dict]:
    if callable(im_correction):
        if_correction(**kwargs)
        im_correction = vars().get("__returned_dict__", {}).get("im_correction", im_correction)
    yield str(im_correction)
    return vars().get("__returned_dict__", {})


@generator_context
def correction_shift(correction_shift: Generator | str, **kwargs) -> Generator[str, None, Dict]:
    if callable(correction_shift):
        if_correction(**kwargs)
        correction_shift = vars().get("__returned_dict__", {}).get("correction_shift", correction_shift)
    yield str(correction_shift)
    return vars().get("__returned_dict__", {})


@generator_context
def if_correction(fsym, clk_freq, ifreq, **kwargs) -> Generator[str, None, Dict]:
    """
    Compute the correction factor for the given intermediate frequency
    """
    
    assert clk_freq % fsym == 0, "Clock rate must be an integer multiple of symbol rate"
    samples_per_symbol = clk_freq // fsym
    scum_if = ifreq / fsym

    re_mult, im_mult = clock_recovery_if_correction(scum_if, samples_per_symbol)
    print(f'Correction coefficients: ({re_mult}, {im_mult})')

    # Scale the coefficients by powers of two until both are sufficiently close to an integer
    mults = np.array([re_mult, im_mult], dtype=np.float64)
    shift_amt = 0
    while np.max(np.abs(mults - mults.astype(int))) > 0.001:
        mults *= 2
        shift_amt += 1

    mults = mults.astype(int)

    print(f"Shift Amount: {shift_amt}")
    print(f"Final linear combination coefficients: ({mults[0]}, {mults[1]})")

    yield ""
    return dict(
        re_correction=mults[0],
        im_correction=mults[1],
        correction_shift=shift_amt,
    )
