/* 
* This file is adapted from auryn RateChecker class for Synapseek. 
* Copyright for auryn go to Friedemann Zenke
*/

#include "CheckerScorer_FamDet_Lbasic.h"

using namespace auryn;


CheckerScorer_FamDet_Lbasic::CheckerScorer_FamDet_Lbasic(SpikingGroup* source, AurynFloat min, AurynFloat max, AurynFloat tau_pop, AurynFloat rate_cut_fam, AurynFloat rate_cut_new) : Checker()
{
	src = source;
	r_cut_fam = rate_cut_fam;
	r_cut_new = rate_cut_new;
	scoring_active = false;
	scoring_phase = false;
	time_blow_up = -1.0; 
	loss_pop = 0.0;
	familiar = true;

	init(min, max, tau_pop);
	

	// for loss_pop computation of novel patterns
	cst1_new = 1/(100-r_cut_new);
	cst2_new = -r_cut_new/(100-r_cut_new);

	// for loss_pop computation of familiar patterns
	cst1_fam = -1/r_cut_fam;
	cst2_fam = 1;

	state = (min + max)/2;
}

CheckerScorer_FamDet_Lbasic::~CheckerScorer_FamDet_Lbasic()
{
}

void CheckerScorer_FamDet_Lbasic::init(AurynFloat min, AurynFloat max, AurynFloat tau_pop)
{
	if ( src->evolve_locally() )
		auryn::sys->register_checker(this);
	timeconstant_pop = tau_pop;
	size = src->get_size();
	popmin = min;
	popmax = max;
	decay_multiplier_pop = exp(-auryn_timestep/tau_pop);
	reset();
}


bool CheckerScorer_FamDet_Lbasic::propagate()
{
	// update population firing rate
	state *= decay_multiplier_pop;
	state += 1.*src->get_spikes()->size()/timeconstant_pop/size;

	if ( state>popmin && state<popmax ) // if network hasn't blown up 
	{ 
		if (scoring_active == true) // update loss if we are in scoring phase
		{	
			///////////////////////////////// DEBUG ///////////////////////////////////
			// std::cout << "State " << state << std::endl;
			///////////////////////////////////////////////////////////////////////////
			if (familiar == false) // if we are currently scoring a novel trial
			{
				if (state >= r_cut_new) // novel stim but we have high firing rate
				{	
					loss_pop += cst1_new*state + cst2_new;
					///////////////////////////////// DEBUG ///////////////////////////////////
					// std::cout << "loss on new" << loss_pop << std::endl;
					///////////////////////////////////////////////////////////////////////////
				}
				// no else, the loss is 0 if the pop rate is small enough for novel pattern
			}
			else // if we are scoring a familiar pattern
			{
				if (state <= r_cut_fam) // familiar pattern but rate is low
				{	
					loss_pop += cst1_fam*state + cst2_fam;
					///////////////////////////////// DEBUG ///////////////////////////////////
					// std::cout << "loss on fam " << loss_pop << std::endl;
					///////////////////////////////////////////////////////////////////////////
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

AurynFloat CheckerScorer_FamDet_Lbasic::get_property()
{
	return get_rate();
}

AurynFloat CheckerScorer_FamDet_Lbasic::get_rate()
{
	return state;
}

void CheckerScorer_FamDet_Lbasic::set_rate(AurynFloat r)
{
	state = r;
}

void CheckerScorer_FamDet_Lbasic::reset()
{
	set_rate((popmax+popmin)/2);
}

void CheckerScorer_FamDet_Lbasic::virtual_serialize(boost::archive::binary_oarchive & ar, const unsigned int version ) 
{
	ar & state;
}

void CheckerScorer_FamDet_Lbasic::virtual_serialize(boost::archive::binary_iarchive & ar, const unsigned int version ) 
{
	ar & state;
}