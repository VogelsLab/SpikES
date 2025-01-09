/* 
* This is adapted from STPConnection, a part of Auryn (Friedemann Zenke)
*/

#include "RFConnection.h"

using namespace auryn;

RFConnection::RFConnection(SpikingGroup * source, NeuronGroup * destination, AurynWeight weight, 
						int radius, TransmitterType transmitter, std::string name) 
						: SparseConnection(source, destination, weight, 1.0, transmitter, name)
{
	// std::cout << "Hello1" << std::endl;
	w->set_all(0.0);

	// std::cout << "Hello2" << std::endl;
	std::vector< std::vector<int> > rf_matrix;
	rf_matrix = make_RFconnectivity(get_m_rows(), get_n_cols(), radius);

	// std::cout << "rf_matrix " << std::endl;
	for ( NeuronID i = 0 ; i < get_m_rows() ; ++i ) 
	{
		for ( NeuronID* j = w->get_row_begin(i) ; j != w->get_row_end(i) ; ++j )
		{
			w->get_data_begin()[j-w->get_row_begin(0)] = rf_matrix[i][*j]*weight;
			// std::cout << " " << rf_matrix[i][*j] << std::endl;
		}
	}
	w->prune();
	// std::cout << "Done with constructor" << std::endl;
}

std::vector< std::vector<int> > RFConnection::make_RFconnectivity(int N_pre, int N_post, int radius)
{
	std::vector< std::vector<int> > rf_matrix(N_pre, std::vector<int>(N_post));
	int N_pre_2D = (int) std::sqrt(N_pre); //ADD A CHECK IF N_pre is not a square
	// std::cout << "N_pre_2D " << N_pre_2D << std::endl;
	std::srand(std::time(0));
	int x, y;
	std::vector<int> coords(2);
	for (int post_ind = 0; post_ind < N_post; post_ind++)
	{
		//generate a random center for receptive field of the current post neuron
		int cx = std::rand() % N_pre_2D;
		int cy = std::rand() % N_pre_2D;
		// std::cout << "center coordinates, " << cx << ", "<< cy << std::endl;
		for (int pre_ind = 0; pre_ind < N_pre; pre_ind++)
		{
			coords = get_2D_coords(pre_ind, N_pre);
			x = coords[0];
			y = coords[1];
			// std::cout << "current coordinates, " << x << ", "<< y << std::endl;
			if ((x-cx)*(x-cx) + (y-cy)*(y-cy) < radius*radius)
			{
				rf_matrix[pre_ind][post_ind] = 1;
			}
			else{
				rf_matrix[pre_ind][post_ind] = 0;
			}
		}
	}
	return rf_matrix;
}

std::vector<int> RFConnection::get_2D_coords(int ind, int N_neuron)
{
	int N_2D = (int) std::sqrt(N_neuron);
	std::vector<int> coords(2);
	coords[0] = ind / N_2D;
	coords[1] = ind % N_2D;
	return coords;
}