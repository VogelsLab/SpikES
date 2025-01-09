/* 
* This is adapted from STPConnection, a part of Auryn (Friedemann Zenke)
*/

#ifndef RFCONNECTION_H_
#define RFCONNECTION_H_

#include "auryn/auryn_definitions.h"
#include "auryn/AurynVector.h"
#include "auryn/SparseConnection.h"

namespace auryn {

/*! \brief This class implements a receptive field connectivity
 * 
 * Each post neuron will be connected to a random neuron in the input layer, and all neurons in a given radius and fixed weight. 
 * (input layer considered to be sqrt(N)*sqrt(N) 2D layer
 *
 */

class RFConnection : public SparseConnection
{

public:

	/*! Default constructor to initialize connection with random recptive field connectivity
	 * \param source The presynaptic SpikingGroup
	 * \param destination the postsynaptic NeuronGroup
	 * \param weight The default weight for connections 
	 * \param radius radius of the receptive field
	 * \param transmitter The transmitter type
	 * \param name The connection name as it appears in debugging output
	 */
	RFConnection(SpikingGroup * source, NeuronGroup * destination, AurynWeight weight, int radius=8, TransmitterType transmitter=GLUT, string name="RFConnection");

	/*! returns 2D vector which will have binary weights with RFconnectivity
	 * \param N_pre number of pre neurons
	 * \param N_post number of post neurons 
	 * \param radius radius of the receptive field (unit = number of neurons)
	 */
	std::vector< std::vector<int> > make_RFconnectivity(int N_pre, int N_post, int radius);

	/*! returns the 2D coordinates of a neuron index in a 1D layer (N neurons), 2D coordinates in a sqrt(N)*sqrt(N) 2D layer
	 * \param N_neuron total number of neuron in the layer
	 * \param ind 1D index of the neuron
	 */
	std::vector<int> get_2D_coords(int ind, int N_neuron);

};

}

#endif /*RFCONNECTION_H_*/
