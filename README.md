# Matching-with-Couples-Hospitals-Residents-HR-

This project implements a simulation of the Hospital–Resident Matching Problem with Couples, an extension of the classic Stable Marriage / Gale–Shapley algorithm used in many real-world matching markets such as the National Resident Matching Program (NRMP).

Unlike the standard problem where each resident applies individually, this implementation supports couples who must be matched simultaneously to a pair of hospitals.

Overview
The program simulates a matching market consisting of:

Hospitals with limited capacities
Single residents with preference lists over hospitals
Couples who submit joint preferences over pairs of hospitals
The algorithm attempts to find a stable matching while respecting:

Hospital capacity constraints
Individual preferences
Joint preferences of couples
After the matching process finishes, the system also verifies stability by detecting possible blocking pairs.

Features
Implementation of a Gale–Shapley–style deferred acceptance algorithm
Support for single residents and couples
Random test data generation
Efficient hospital ranking lookup using hash maps
Handling of displacement chains when residents are replaced
Support for same-hospital couple assignments
Post-matching stability verification
Project Structure
Main components of the implementation:

Resident

Represents a resident with preferences and current match status.

Hospital

Represents a hospital with capacity, preference ranking, and current matches.

Couple

Represents two residents who must be matched together using joint preferences.

generate_test_data()

Creates random hospitals, residents, and preference lists for simulation.

match_all()

Runs the main matching algorithm handling both singles and couples.

simulate_acceptance()

Checks whether a hospital would accept a resident.

handle_rejection_chain()

Handles cascading effects when a resident is displaced.

verify_stability()

Detects blocking pairs to determine whether the final matching is stable.

Algorithmic Idea
The algorithm follows a deferred acceptance framework:

Free applicants (singles or couples) propose to hospitals according to their preferences.
Hospitals tentatively accept the best applicants up to their capacity.
If a better applicant arrives, the hospital may replace a currently matched resident.
Displaced residents (or couples) re-enter the queue and try their next preference.
The process continues until no applicant wants to propose further.
Couples introduce additional complexity because both partners must be accepted simultaneously.

Stability Verification
After matching completes, the program checks for blocking pairs:

A single blocking pair exists if a resident and a hospital prefer each other over their current assignments.
A couple blocking pair exists if both hospitals would accept the pair simultaneously.
If no blocking pairs are found, the matching is considered stable
