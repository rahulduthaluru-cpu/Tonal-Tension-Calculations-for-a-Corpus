# Tonal-Tension-Calculations-for-a-Corpus
Python code for computational analysis of tonal tension across classical, jazz, rock, and pop music using Elaine Chew’s Spiral Array Model.
# Computational Analysis of Tonal Tension Across Musical Genres

This repository contains the Python code used to investigate differences in
tonal tension across classical, jazz, rock, and pop music.

The analysis uses Elaine Chew's Spiral Array Model to quantify three
components of tonal tension:

- Cloud Momentum
- Cloud Diameter
- Tensile Strain

MIDI files from each genre are processed using the Partitura Python
framework. The resulting tension measurements are aggregated and visualized
using violin plots to compare their distributions across genres.

## Research Question

How does tonal tension, measured using the Spiral Array Model, vary across
classical, jazz, rock, and pop music?

## Method

For each MIDI composition, the code:
1. Loads the symbolic score using Partitura.
2. Estimates pitch spelling and the global key using the
   Krumhansl-Schmuckler algorithm.
3. Calculates cloud momentum, cloud diameter, and tensile strain using
   Partitura's tonal tension implementation.
4. Aggregates the measurements across compositions within each genre.
5. Visualizes the resulting distributions using violin plots.
