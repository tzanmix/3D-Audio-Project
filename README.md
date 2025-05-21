Digital Sound Processing Project

This is a simple software application written in Python that allows the user to place a virtual sound source in a 3D space by clicking on a desired location. The sound can be rendered either through loudspeakers or headphones, and the software supports dynamic motion of the sound source.

Installation & Setup:
Unzip the files into a folder of your choice. Then, run the file setup.py to install all necessary dependencies. Finally, execute 3D AUDIO APP.py to launch the application.

Usage:
The user can upload an MP3 or WAV audio file into the software, select the preferred output device (speakers or headphones), choose the desired spatialization mode (dynamic or static), and set the position of the sound source in the virtual environment.
In headphone mode, binaural spatialization is achieved using a Head-Related Impulse Response (HRIR) algorithm, with data sourced from the SOFA repository.
In speaker mode, the software simulates a 5.0 speaker setup, generating spatial audio output using the 2D Vector-Based Amplitude Panning (VBAP) algorithm.


Εργασία Ψηφιακής Επεξεργασίας Ήχου

Πρόκειται για μία απλή εφαρμογή γραμμένη σε Python, η οποία επιτρέπει στον χρήστη να τοποθετεί μία εικονική πηγή ήχου σε έναν τρισδιάστατο χώρο, κάνοντας κλικ στο επιθυμητό σημείο. Ο ήχος μπορεί να αποδίδεται είτε μέσω ηχείων είτε μέσω ακουστικών, και υποστηρίζεται η δυναμική κίνηση της ηχητικής πηγής.

Εγκατάσταση:
Αποσυμπιέστε τα αρχεία σε έναν φάκελο της επιλογής σας. Στη συνέχεια, εκτελέστε το αρχείο setup.py για την εγκατάσταση όλων των απαραίτητων εξαρτήσεων. Τέλος, εκτελέστε το 3D AUDIO APP.py για να ξεκινήσετε την εφαρμογή.

Χρήση:
Ο χρήστης μπορεί να ανεβάσει ένα αρχείο ήχου τύπου MP3 ή WAV, να επιλέξει την προτιμώμενη έξοδο (ηχεία ή ακουστικά), τη λειτουργία χωρικής απεικόνισης (δυναμική ή στατική), καθώς και τη θέση της ηχητικής πηγής στον εικονικό χώρο.
Στη λειτουργία ακουστικών, η χωρική απεικόνιση επιτυγχάνεται με τη χρήση Συναρτήσεων Μεταφορών Κεφαλής (HRTFs), χρησιμοποιώντας δεδομένα από το αποθετήριο SOFA.
Στη λειτουργία ηχείων, προσομοιώνεται μία διάταξη ηχείων 5.0 και η έξοδος του ήχου παράγεται με τη βοήθεια του αλγορίθμου δισδιάστατου Vector Based Amplitude Panning (VBAP).
