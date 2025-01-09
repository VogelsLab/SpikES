/* 
* This file is adapted from auryn RateChecker class for Synapseek. 
* Copyright for auryn go to Friedemann Zenke
*/

#include "CheckerScorer_ReluFamiliarity.h"

using namespace auryn;


CheckerScorer_ReluFamiliarity::CheckerScorer_ReluFamiliarity(SpikingGroup* source, AurynFloat min, AurynFloat max, AurynFloat tau_glob, AurynFloat rate_cut_fam, AurynFloat rate_cut_new) : Checker()
{
	src = source;
	r_cut_fam = rate_cut_fam;
	r_cut_new = rate_cut_new;
	init(min, max, tau_glob);
	scoring_active = false;
	time_blow_up = -1.0; 
	loss = 0.0;
	familiar = true;

	// for loss computation of novel patterns
	cst1_new = 1/(100-r_cut_new);
	cst2_new = -r_cut_new/(100-r_cut_new);

	// for loss computation of familiar patterns
	cst1_fam = -1/r_cut_fam;
	cst2_fam = 1;
}

CheckerScorer_ReluFamiliarity::~CheckerScorer_ReluFamiliarity()
{
}

void CheckerScorer_ReluFamiliarity::init(AurynFloat min, AurynFloat max, AurynFloat tau_glob)
{
	if ( src->evolve_locally() )
		auryn::sys->register_checker(this);
	timeconstant_pop = tau_glob;
	size = src->get_size();
	popmin = min;
	popmax = max;
	decay_multiplier_pop = exp(-auryn_timestep/tau_glob);
	reset();
}


bool CheckerScorer_ReluFamiliarity::propagate()
{
	// update population firing rate
	state *= decay_multiplier_pop;
	state += 1.*src->get_spikes()->size()/timeconstant_pop/size;

	if ( state>popmin && state<popmax ) // if network hasn't blown up 
	{ 
		if (scoring_active == true) // update loss if we are in scoring phase
		{	
			if (familiar == false) // if we are currently scoring a novel trial
			{
				if (state >= r_cut_new) // novel stim but we have high firing rate
				{	
					loss += cst1_new*state + cst2_new;
				}
				// no else, the loss is 0 if the pop rate is small enough for novel pattern
			}
			else // if we are scoring a familiar pattern
			{
				if (state <= r_cut_fam) // familiar pattern but rate is low
				{	
					loss += cst1_fam*state + cst2_fam;
				}
				// no else, the loss is 0 if the pop rate is high enough for familiar pattern
			}
		}
		return true; 
	}
	else  {
		//network has blown up, monitor when the network blew up for loss computation
		time_blow_up = sys->get_time();
		return false;
		}
}

AurynFloat CheckerScorer_ReluFamiliarity::get_property()
{
	return get_rate();
}

AurynFloat CheckerScorer_ReluFamiliarity::get_rate()
{
	return state;
}

void CheckerScorer_ReluFamiliarity::set_rate(AurynFloat r)
{
	state = r;
}

void CheckerScorer_ReluFamiliarity::reset()
{
	set_rate((popmax+popmin)/2);
}

void CheckerScorer_ReluFamiliarity::virtual_serialize(boost::archive::binary_oarchive & ar, const unsigned int version ) 
{
	ar & state;
}

void CheckerScorer_ReluFamiliarity::virtual_serialize(boost::archive::binary_iarchive & ar, const unsigned int version ) 
{
	ar & state;
}