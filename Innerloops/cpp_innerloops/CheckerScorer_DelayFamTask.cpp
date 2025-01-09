/* 
* This file is adapted from auryn RateChecker class for Synapseek. 
* Copyright for auryn go to Friedemann Zenke
*/

#include "CheckerScorer_DelayFamTask.h"

using namespace auryn;


CheckerScorer_DelayFamTask::CheckerScorer_DelayFamTask(SpikingGroup* source, AurynFloat min, AurynFloat max, AurynFloat tau_pop, AurynFloat tau_ind, AurynFloat rate_cut_fam, AurynFloat rate_cut_new) : Checker()
{
	src = source;
	r_cut_fam = rate_cut_fam;
	r_cut_new = rate_cut_new;
	scoring_active = false;
	scoring_phase = false;
	time_blow_up = -1.0; 
	loss_pop = 0.0;
	loss_ind = 0.0;
	familiar = true;

	init(min, max, tau_pop, tau_ind);
	

	// for loss_pop computation of novel patterns
	cst1_new = 1/(100-r_cut_new);
	cst2_new = -r_cut_new/(100-r_cut_new);

	// for loss_pop computation of familiar patterns
	cst1_fam = -1/r_cut_fam;
	cst2_fam = 1;

	ind_rates.resize(size);
	state = (min + max)/2;
	for (itb = 0; itb < size; itb++) //initialize firing rates of individual neurons
	{
		ind_rates[0] = (min + max)/2;
	}
}

CheckerScorer_DelayFamTask::~CheckerScorer_DelayFamTask()
{
}

void CheckerScorer_DelayFamTask::init(AurynFloat min, AurynFloat max, AurynFloat tau_pop, AurynFloat tau_ind)
{
	if ( src->evolve_locally() )
		auryn::sys->register_checker(this);
	timeconstant_pop = tau_pop;
	timeconstant_ind = tau_ind;
	size = src->get_size();
	popmin = min;
	popmax = max;
	decay_multiplier_pop = exp(-auryn_timestep/tau_pop);
	decay_multiplier_ind = exp(-auryn_timestep/tau_ind);
	reset();
}


bool CheckerScorer_DelayFamTask::propagate()
{
	// update population firing rate
	state *= decay_multiplier_pop;
	state += 1.*src->get_spikes()->size()/timeconstant_pop/size;

	// update individual firing rates
	for (it = src->get_spikes_immediate()->begin() ; it < src->get_spikes_immediate()->end() ; ++it ) //loop over the spikes of current timestep
	{ 	
		ind_rates[*it] += 1/timeconstant_ind; //the neurons that fired
	}
	for (itb = 0; itb < size; itb++) //update firing rates of all individual neurons
	{
		ind_rates[itb] *= decay_multiplier_ind;

		if (scoring_phase == true) //update loss_ind if we are during scoring phase (not only during scoring window!)
		{
			/// DEBUG ///
			// std::cout << ind_rates[itb] << std::endl;
			/// END DEBUG ///
			
			if (ind_rates[itb] <= 1)
			{
				loss_ind += 1 - ind_rates[itb];
			}
			else if ( (ind_rates[itb] <= 100) && (ind_rates[itb] >= 60) )
			{
				loss_ind += ind_rates[itb]/40 - 1.5;
			}
		}
	}

	if ( state>popmin && state<popmax ) // if network hasn't blown up 
	{ 
		if (scoring_active == true) // update loss if we are in scoring phase
		{	
			if (familiar == false) // if we are currently scoring a novel trial
			{
				if (state >= r_cut_new) // novel stim but we have high firing rate
				{	
					loss_pop += cst1_new*state + cst2_new;
				}
				// no else, the loss is 0 if the pop rate is small enough for novel pattern
			}
			else // if we are scoring a familiar pattern
			{
				if (state <= r_cut_fam) // familiar pattern but rate is low
				{	
					loss_pop += cst1_fam*state + cst2_fam;
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

AurynFloat CheckerScorer_DelayFamTask::get_property()
{
	return get_rate();
}

AurynFloat CheckerScorer_DelayFamTask::get_rate()
{
	return state;
}

void CheckerScorer_DelayFamTask::set_rate(AurynFloat r)
{
	state = r;
}

void CheckerScorer_DelayFamTask::reset()
{
	set_rate((popmax+popmin)/2);
}

void CheckerScorer_DelayFamTask::virtual_serialize(boost::archive::binary_oarchive & ar, const unsigned int version ) 
{
	ar & state;
}

void CheckerScorer_DelayFamTask::virtual_serialize(boost::archive::binary_iarchive & ar, const unsigned int version ) 
{
	ar & state;
}