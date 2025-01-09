#ifndef CHECKERSCORER_STABILITY_H_
#define CHECKERSCORER_STABILITY_H_

#include "auryn/auryn_definitions.h"
#include "auryn/AurynVector.h"
#include "auryn/System.h"
#include "auryn/Checker.h"
#include "auryn/SpikingGroup.h"

namespace auryn {

/*! \brief This class is adapted from the auryn RateChecker Class, for use by synapseek in the Stability innerloop.
 * It implements both a rate checker and computes the cumulative (firing rate - target)**2
 * The firing rate is computed as a moving average with time constant tau.
 * The loss returned needs to be normalized by the scoring duration
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

class CheckerScorer_Stability : public Checker
{
private:
	AurynFloat decay_multiplier;
	AurynDouble popmin;
	AurynDouble popmax;
	AurynDouble state;
	AurynFloat timeconstant;
    NeuronID size;
	void init(AurynFloat min, AurynFloat max, AurynFloat tau);
	
	virtual void virtual_serialize(boost::archive::binary_oarchive & ar, const unsigned int version );
	virtual void virtual_serialize(boost::archive::binary_iarchive & ar, const unsigned int version );
protected:
	SpikingGroup * src;

public:
	float target;
	double loss;
	double avg_rate;
	double time_blow_up;
	float cst;
	bool scoring_active;

	/*! A more elaborate constructor specifying also a minimum rate to guard against silent networks.
	 * @param source the source group to monitor.
	 * @param min the minimum firing rate below which the Checker signals a break of the simulation.
	 * @param max the maximum firing rate above which the Checker signals a break of the simulation.
	 * @param tau the time constant over which to compute the moving average of the rate.
	 */
	CheckerScorer_Stability(SpikingGroup * source, AurynFloat min, AurynFloat max, AurynFloat tau, AurynFloat r_target);
	virtual ~CheckerScorer_Stability();
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

#endif /*CHECKERSCORER_STABILITY_H_*/