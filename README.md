A Digital Sound Processing project, a simple software written in Python which allows the user to click in a position in space to place a virtual sound source, 
both by using loudspeakers or headphones, and allows the dynamic motion of the sound source.

The user can upload an mp3 or wav sound file to the software, select the preferred output (speakers or headphones), the preferred spatialization mode (dynamic or static)
and the position of the sound source in the surrounding space.

For the headphone mode, a binaural spatialization algorithm is implemented, using Head Related Impulse Responses (HRIRs) from the SOFA repository.
For the speaker mode, a space with the 5.0 speaker configuration is simulated, and the output audio is generated with the help of the 2D vector-based amplitude panning (VBAP) algorithm.
