# Tilting Train Simulator
Simulator of a tilting train over a curve in Massif Central (France) based on data from the French railway company (SNCF). The goal was to compute the speed gain tilting the train could bring about. This project was part of my work for the Concours des Grandes Écoles and was my TIPE (Travail d'initiative personnelle encadré = Supervised self-initiated work).

# Validation of the simulator
Based on real data from the SNCF for a 50km part of the railroad in Massif Central.

## Railroad validation
Based on theorical railroad design documentation.
![](images/validation_trace.png)

## Cant deficiency validation
Based on cant deficiency measured by [Mauzin car](https://fr.wikipedia.org/wiki/Voiture_Mauzin).
![](images/validation_devers.png)

## Acceleration validation
Based on acceleration and speed measured by a [BB26000 locomotive](https://en.wikipedia.org/wiki/SNCF_Class_BB_26000).
![](images/validation_acceleration.png)

# Simulation of tilting train
## Same speed comparison
![](images/simulation_same_speed.png)

## Same passenger acceleration (increased speed for tilting train)
![](images/simulation_increased_speed.png)

## Conclusion
While keeping the same acceleration for the passenger, speed can be increased by 23%.
Hence a gain of 19% in the trip duration.
