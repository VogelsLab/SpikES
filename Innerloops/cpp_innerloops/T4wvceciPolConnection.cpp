/* 
* This is a part of Synapseek, written by Basile Confavreux. 
* It uses the spiking network simulator Auryn written by Friedemann Zenke.
It has 2 pre traces and 2 post traces (each with their own timescale).
on pre:  th0*(1 + th1 + th2*w_rctf + th3*w_rctf^2)
            *(1 + th4*V_rctf)
            *(1 + th5*Ce_rctf + th6*Ce_rctf^2)
            *(1 + th7*Ci_rctf)
            *(1 + th8*xpre2_rctf)
            *(1 + th9*xpost1_rctf)

on post:  th10*(1 + th11 + th12*w_rctf + th13*w_rctf^2)
            *(1 + th14*V_rctf)
            *(1 + th15*Ce_rctf + th16*Ce_rctf^2)
            *(1 + th17*Ci_rctf)
            *(1 + th18*xpre1_rctf)
            *(1 + th19*xpost2_rctf + + th20*xpost1_rctf^3)

Total of 21 parameters (time constants not learned here)
[th0, - , th9, th10, -, th20] coeffs

Total of 21 parameters (time constants not learned here)
[th0, - , th9, th10, -, th20] coeffs

Careful, all the values for synaptic variables are rescaled (to be in the ball park of 1-10 in absolute value, check the rescale factors).
*/

#include "T4wvceciPolConnection.h"

using namespace auryn;

void T4wvceciPolConnection::init(std::vector<float> coeffs_, AurynWeight maxweight)
{
	set_max_weight(maxweight);
	set_min_weight(0.0);

	stdp_active = true;

	if ( dst->get_post_size() == 0 ) return;

    //rescales inputs to the Pol for more useful scaling and comparison of palsticity rule parameters
    rescale_trace=2.; 
	rescale_v=15.;
	rescale_w=1.;
	rescale_cexc=15.;
	rescale_cinh=15.;

	tr_pre1 = src->get_pre_trace(0.02);
	tr_pre2 = src->get_pre_trace(0.1);
	tr_post1 = dst->get_post_trace(0.02);
	tr_post2 = dst->get_post_trace(0.1);

    coeffs = coeffs_;

    loss_reg = 0; //// FOR NOW, TO UPDATE WHEN NEEDED!!

    ///////////// DEBUG ///////////////////////////////////////////////
    // std::cout << "Inside Connection: " << std::endl;
    // std::cout << "coeffs: " << std::endl;
    // for (int i = 0; i < 21; i ++)
    // {
    //     std::cout << coeffs[i] << ", ";
    // }
    // std::cout << "; " << std::endl;
    ///////////////////////////////////////////////////////////////////
}

void T4wvceciPolConnection::free()
{
}

T4wvceciPolConnection::T4wvceciPolConnection(CVAIFGroup* source, CVAIFGroup* destination, 
			AurynWeight weight, AurynFloat sparseness, std::vector<float> coeffs_,
			AurynWeight maxweight, TransmitterType transmitter, string name) 
: DuplexConnection(source, destination, weight, sparseness, transmitter, name)
{
	init(coeffs_, maxweight);
    dst_cvaif = destination; //allows to access vtrace, cexh cinh from CVAIFGroup
}

T4wvceciPolConnection::~T4wvceciPolConnection()
{
	free();
}

inline AurynWeight T4wvceciPolConnection::dw_pre(NeuronID pre, NeuronID post, AurynWeight current_w, AurynFloat V, AurynFloat Cexc, AurynFloat Cinh)
{
    return forward_pre(tr_pre2->get(pre), tr_post1->get(post), current_w, V, Cexc, Cinh);
}

inline AurynWeight T4wvceciPolConnection::dw_post(NeuronID pre, NeuronID post, AurynWeight current_w, AurynFloat V, AurynFloat Cexc, AurynFloat Cinh)
{
    return forward_post(tr_pre1->get(pre), tr_post2->get(post), current_w, V, Cexc, Cinh);
}

inline void T4wvceciPolConnection::propagate_forward()
{
    // loop over all spikes: spike = pre_spike
    for (SpikeContainer::const_iterator spike = src->get_spikes()->begin(); spike != src->get_spikes()->end(); ++spike) 
    {
        // loop over all postsynaptic partners (c: untranslated post index)
        for (const NeuronID* c = w->get_row_begin(*spike); c != w->get_row_end(*spike); ++c) 
        {
            // transmit signal to target at postsynaptic neuron (no plasticity yet)
            AurynWeight* weight = w->get_data_ptr(c);
            transmit(*c, *weight);
 
            // handle plasticity
            if (stdp_active) 
            {
                // translate postsynaptic spike (required for mpi run)
                NeuronID trans_post_ind = dst->global2rank(*c);

                // perform weight update
                ////////////////////////////////////////////////////////////////////////////////////////////////////
                // std::cout << " " << std::endl;
                // std::cout << "Inside propagate forward:" << std::endl;
                // std::cout << "pre index " << *spike 
                //           << ", post index " << trans_post_ind
                //           << ", voltage trace " << dst_cvaif->vtrace->get(trans_post_ind)
                //           << ", cexc " << dst_cvaif->cexc->get(trans_post_ind) 
                //           << ", cinh " << dst_cvaif->cinh->get(trans_post_ind) << std::endl;
                // std::cout << " " << std::endl;
                ////////////////////////////////////////////////////////////////////////////////////////////////////
                *weight += dw_pre(*spike, trans_post_ind, *weight, dst_cvaif->vtrace->get(trans_post_ind),
                            dst_cvaif->cexc->get(trans_post_ind), dst_cvaif->cinh->get(trans_post_ind));
               
                // clip weights if needed
                if (*weight > get_max_weight()) *weight = get_max_weight();
                if (*weight < get_min_weight()) *weight = get_min_weight();
            }
        }
    }
}

inline void T4wvceciPolConnection::propagate_backward()
{
    if (stdp_active) 
    {
        SpikeContainer::const_iterator spikes_end = dst->get_spikes_immediate()->end();
        
        // loop over all spikes: spike = post_spike
        for (SpikeContainer::const_iterator spike = dst->get_spikes_immediate()->begin(); spike != spikes_end; ++spike) 
        {
            // translated id of the postsynaptic neuron that spiked
            NeuronID trans_post_ind = dst->global2rank(*spike);
 
            // loop over all presynaptic partners
            for (const NeuronID* c = bkw->get_row_begin(*spike); c != bkw->get_row_end(*spike); ++c) 
            {
                #if defined(CODE_ACTIVATE_PREFETCHING_INTRINSICS) && defined(CODE_USE_SIMD_INSTRUCTIONS_EXPLICITLY)
                // prefetches next memory cells to reduce number of last-level cache misses
                _mm_prefetch((const char *)bkw->get_data_begin()[c-bkw->get_row_begin(0)+2],  _MM_HINT_NTA);
                #endif
 
                // compute plasticity update
                AurynWeight* weight = bkw->get_data(c);
                *weight += dw_post(*c, trans_post_ind, *weight, dst_cvaif->vtrace->get(trans_post_ind),
                            dst_cvaif->cexc->get(trans_post_ind), dst_cvaif->cinh->get(trans_post_ind));
 
                // clip weights if needed
                if (*weight > get_max_weight()) *weight = get_max_weight();
                if (*weight < get_min_weight()) *weight = get_min_weight();
            }
        }
    }
}

void T4wvceciPolConnection::propagate()
{
	propagate_forward();
	propagate_backward();
}

float T4wvceciPolConnection::forward_pre(float xpre2, float xpost1, float w, float V, float Cexc, float Cinh) {
    // ////////////////////////////DEBUG//////////////////
    // std::cout << "inside forward pre" << std::endl;
    // std::cout << ", x_pre2=" << xpre2
    //         << ", x_post1=" << xpost1
    //         << ", w=" << w
    //         << ", V=" << V
    //         << ", Cexc=" << Cexc
    //         << ", Cinh=" << Cinh << std::endl;
    // //////////////////////////////////////////////
    
    return(coeffs[0]*(1 + coeffs[1] + rescale_w*w*(coeffs[2] + coeffs[3]*rescale_w*w))
    *(1 + coeffs[4]*rescale_v*V)
    *(1 + rescale_cexc*Cexc*(coeffs[5] + coeffs[6]*rescale_cexc*Cexc))
    *(1 + coeffs[7]*rescale_cinh*Cinh)
    *(1 + coeffs[8]*rescale_trace*xpre2)
    *(1 + coeffs[9]*rescale_trace*xpost1));
}

float T4wvceciPolConnection::forward_post(float xpre1, float xpost2, float w, float V, float Cexc, float Cinh) {
    // ////////////////////////////DEBUG//////////////////
    // std::cout << "inside forward post" << std::endl;
    // std::cout << ", x_pre2=" << xpre1
    //         << ", x_post1=" << xpost2
    //         << ", w=" << w
    //         << ", V=" << V
    //         << ", Cexc=" << Cexc
    //         << ", Cinh=" << Cinh << std::endl;
    // //////////////////////////////////////////////

    return(coeffs[10]*(1 + coeffs[11] + rescale_w*w*(coeffs[12]* + coeffs[13]*rescale_w*w))
    *(1 + coeffs[14]*rescale_v*V)
    *(1 + rescale_cexc*Cexc*(coeffs[15] + coeffs[16]*rescale_cexc*Cexc))
    *(1 + coeffs[17]*rescale_cinh*Cinh)
    *(1 + coeffs[18]*rescale_trace*xpre1)
    *(1 + rescale_trace*xpost2*(coeffs[19] + coeffs[20]*rescale_trace*xpost2*rescale_trace*xpost2)));
}