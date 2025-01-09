/* 
* This file is part of Synapseek, written by Basile Confavreux
* This file is adapted from Auryn and the RateChecker class. 
*/

#include "CheckerScorer_Stability.h"

using namespace auryn;



CheckerScorer_Stability::CheckerScorer_Stability(SpikingGroup * source, AurynFloat min, AurynFloat max, AurynFloat tau, AurynFloat r_target) : Checker()
{
	src = source;
	init(min,max,tau);
	loss = 0;
	target = r_target;
	time_blow_up = -1;
	cst = 2;
	scoring_active = false;
	avg_rate = 0;
	state = (min + max)/2;
}

CheckerScorer_Stability::~CheckerScorer_Stability()
{
}

void CheckerScorer_Stability::init(AurynFloat min, AurynFloat max, AurynFloat tau)
{
	if ( src->evolve_locally() )
		auryn::sys->register_checker(this);
	timeconstant = tau;
	size = src->get_size();
	popmin = min;
	popmax = max;
	decay_multiplier = exp(-auryn_timestep/tau);
	reset();
}


bool CheckerScorer_Stability::propagate()
{
	state *= decay_multiplier;
	state += 1.*src->get_spikes()->size()/timeconstant/size; //updated current population firing rate
	if ( state>popmin && state<popmax ) { //network hasn't blown up
		if (scoring_active == true) //update loss if we are in scoring phase
		{
			loss += (state - target)*(state - target)/(state + cst);
			// avg_rate += state;
		}
		return true; 
		}
	else  {
		time_blow_up = sys->get_time(); //network has blown up, remember when network blew up and stop simulation
		return false;

		}
}

AurynFloat CheckerScorer_Stability::get_property()
{
	return get_rate();
}

AurynFloat CheckerScorer_Stability::get_rate()
{
	return state;
}

void CheckerScorer_Stability::set_rate(AurynFloat r)
{
	state = r;
}

void CheckerScorer_Stability::reset()
{
	set_rate((popmax+popmin)/2);
}

void CheckerScorer_Stability::virtual_serialize(boost::archive::binary_oarchive & ar, const unsigned int version ) 
{
	ar & state;
}

void CheckerScorer_Stability::virtual_serialize(boost::archive::binary_iarchive & ar, const unsigned int version ) 
{
	ar & state;
}