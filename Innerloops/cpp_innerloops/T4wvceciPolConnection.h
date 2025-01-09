/* 
* This is a part of Synapseek, written by Basile Confavreux. 
* It uses the spiking network simulator Auryn written by Friedemann Zenke.
*/

#ifndef T4WVCECIPOLCONNECTION_H_
#define T4WVCECIPOLCONNECTION_H_

#include "auryn/auryn_definitions.h"
#include "auryn/AurynVector.h"
#include "auryn/DuplexConnection.h"
#include "auryn/Trace.h"
#include "auryn/LinearTrace.h"
#include "CVAIFGroup.h"
#include <vector>

namespace auryn {


/*! \brief Implements a STDP rule parameterized with a polynomial.
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

Careful, all the values for synaptic variables are rescaled (to be in the ball park of 1-10 in absolute value, check the rescale factors).
*/

class T4wvceciPolConnection : public DuplexConnection
{

public:
	std::vector<AurynFloat> coeffs;

	//rescale inputs to the Pol for more useful computation with sigmoid
	float rescale_trace;
	float rescale_v;
	float rescale_w;
	float rescale_cexc;
	float rescale_cinh;

	CVAIFGroup* dst_cvaif; //pointer to destination neuron group that has to be a CVAIF group

	Trace * tr_pre1;
	Trace * tr_pre2;
	Trace * tr_post1;
	Trace * tr_post2;

	inline AurynWeight dw_pre(NeuronID pre, NeuronID post, AurynWeight current_w, AurynFloat V, AurynFloat Cexc, AurynFloat Cinh);
	inline AurynWeight dw_post(NeuronID pre,NeuronID post, AurynWeight current_w, AurynFloat V, AurynFloat Cexc, AurynFloat Cinh);

	inline void propagate_forward();
	inline void propagate_backward();

	bool stdp_active;

	double loss_reg; //// FOR NOW 0, TO UPDATE WHEN NEEDED!! COMPUTE HEAVY

	/*! Constructor to create a random sparse connection object and set up plasticity.
	 * @param sourceAurynWeight  the source group from where spikes are coming.
	 * @param destination the destination group where spikes are going.
	 * @param weight the initial weight of all connections.
	 * @param sparseness the connection probability for the sparse random set-up of the connections.
	 * @param coeffs_ parameters of the learning rule: [th0, -, th20]
	 * @param maxweight the maxium allowed weight.
	 * @param transmitter the transmitter type of the connection - by default GABA for inhibitory connection.
	 * @param name a meaningful name of the connection which will appear in debug output.
	 */
	T4wvceciPolConnection(CVAIFGroup* source, CVAIFGroup* destination, 
			AurynWeight weight, AurynFloat sparseness, std::vector<float> coeffs_,
			AurynWeight maxweight=1.5 , TransmitterType transmitter=GABA, string name="T4wvceciPolConnection");

	virtual ~T4wvceciPolConnection();
	void init(std::vector<float> coeffs_, AurynWeight maxweight);
	void free();

	virtual void propagate();

	float forward_pre(float xpre2,
					float xpost1,
                    float w, 
                    float V, 
                    float Cexc,
					float Cinh);

	float forward_post(float xpre1,
					float xpost2,
                    float w, 
                    float V, 
                    float Cexc,
					float Cinh);

};
}

#endif /*T4WVCECIPOLCONNECTION_H_*/