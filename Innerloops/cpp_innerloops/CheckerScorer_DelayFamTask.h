#ifndef CHECKERSCORER_DELAYFAMTASK_H_
#define CHECKERSCORER_DELAYFAMTASK_H_

#include "auryn/auryn_definitions.h"
#include "auryn/AurynVector.h"
#include "auryn/System.h"
#include "auryn/Checker.h"
#include "auryn/SpikingGroup.h"

namespace auryn {

/*! \brief
\This class is adapted from the auryn RateChecker Class, from Auryn (Friedemann Zenke)
 * It implements both a rate checker and computes online the loss for the DelayFamTaskNet Innerloop in synapseek.
 * It computes the excitatory population firing rate and individual excitatory firing rates for the loss calculation
 * The firing rates are computed as a moving average with time constant tau_pop and tau_ind.
 * 
 * 
 * Copy paste from the RateChecker description (auryn)
 * The different constructors allow to specify different min and max firing
 * rates to guard against too active or quiet networks.  Also the timeconstant
 * (tau) over which the moving rate average is computed online can be specified.
 * Allow for 3-5 x tau for the estimate to settle to its steady state value.  To
 * avoid accidental breaking of a run due to this effect, at initialization the
 * rate estimate is assumed to  be the mean of the min and max. Note further
 * that this checker computes population averages over the fraction of a neuron
 * group which is simulated on a particular rank.  In highly parallel
 * simulations when the number of neurons per rank is very the rate estimate
 * might have a high variance accross ranks.  If highly parallel simulation is
 * anticipated tau should be chosen longer to avoid spurious breaks caused by a
 * noisy rate estimate or a different checker which computes the rate of entire
 * population (after a MINDELAY s minimal delay) should be used.
 */

class CheckerScorer_DelayFamTask : public Checker
{
private:
	AurynFloat decay_multiplier_pop;
	AurynFloat decay_multiplier_ind;
	AurynFloat timeconstant_pop;
	AurynFloat timeconstant_ind;
	AurynDouble popmin;
	AurynDouble popmax;
	AurynDouble state;
    NeuronID size;

	AurynFloat cst1_fam;
	AurynFloat cst2_fam;
	AurynFloat cst1_new;
	AurynFloat cst2_new;

	SpikeContainer::const_iterator it;
	int itb;
	void init(AurynFloat min, AurynFloat max, AurynFloat tau_pop, AurynFloat tau_ind);
	
	virtual void virtual_serialize(boost::archive::binary_oarchive & ar, const unsigned int version);
	virtual void virtual_serialize(boost::archive::binary_iarchive & ar, const unsigned int version);
protected:
	SpikingGroup * src;

public:

	bool familiar;
	AurynFloat r_cut_fam;
	AurynFloat r_cut_new;
	bool scoring_active;
	bool scoring_phase;
	AurynFloat time_blow_up;
	double loss_ind;
	double loss_pop;
	std::vector<float> ind_rates;

	/*! The only constructor for the class.
	 * @param source the source group to monitor.
	 * @param min the minimum firing rate below which the Checker signals a break of the simulation.
	 * @param max the maximum firing rate above which the Checker signals a break of the simulation.
	 * @param tau_pop the time constant over which to compute the moving average of the population rate.
	 * @param tau_ind the time constant over which to compute the moving average of the individual rates.
	 * @param rate_cut_fam cut of for loss computation for familiar pattern
	 * @param rate_cut_new cut of for loss computation for novel trial
	 */
	CheckerScorer_DelayFamTask(SpikingGroup* source, AurynFloat min, AurynFloat max, AurynFloat tau_pop, AurynFloat tau_ind, AurynFloat rate_cut_fam, AurynFloat rate_cut_new);
	virtual ~CheckerScorer_DelayFamTask();
	/*! The propagate function required for internal use. */
	virtual bool propagate();
	/*! The query function required for internal use. */
	virtual AurynFloat get_property();
	/*! Reads out the current rate estimate. */
	AurynFloat get_rate();
	/*! Sets the current rate estimate -- for instance to provide a reasonable guess upon init.
	 * ( per default this is (max+min)/2.) */
	void set_rate(AurynFloat r);
	void reset();
};

}

#endif /*CHECKERSCORER_DELAYFAMTASK_H_*/