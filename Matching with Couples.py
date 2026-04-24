import random


class Resident:
    def __init__(self, resident_id):
        self.resident_id = resident_id
        # List of preferred hospital IDs (for single residents)
        self.preferences = []
        # Current match (Hospital object or None)
        self.current_match = None
        # Flag to check if this resident is part of a couple
        self.is_coupled = False

    def __repr__(self):
        return f"Resident({self.resident_id})"


class Hospital:
    def __init__(self, hospital_id, capacity):
        self.hospital_id = hospital_id
        self.capacity = capacity
        # List of resident IDs in order of preference
        self.preferences = []
        # Optimization: Map resident_id to rank for O(1) lookup
        # Lower rank index means higher preference (0 is best)
        self.ranking_map = {}
        # Currently matched residents (List of Resident objects)
        self.current_matches = []

    def set_preferences(self, pref_list):
        """
        Sets the preference list and builds a ranking map for fast comparison.
        """
        self.preferences = pref_list
        # Create a dictionary for fast lookups: {resident_id: rank_index}
        self.ranking_map = {res_id: i for i, res_id in enumerate(pref_list)}

    def get_rank(self, resident_id):
        """
        Returns the rank of a resident. 
        If resident is not in the list, returns infinity (least preferred).
        """
        return self.ranking_map.get(resident_id, float('inf'))

    def __repr__(self):
        return f"Hospital({self.hospital_id}, Cap:{self.capacity})"


class Couple:
    def __init__(self, resident1, resident2):
        self.member1 = resident1
        self.member2 = resident2

        # Mark them as coupled
        resident1.is_coupled = True
        resident2.is_coupled = True

        # --- NEW: Link resident to the couple object ---
        resident1.couple_obj = self
        resident2.couple_obj = self
        # -----------------------------------------------

        self.joint_preferences = []
        self.proposal_index = 0

    def __repr__(self):
        return f"Couple({self.member1.resident_id} & {self.member2.resident_id})"


# We assume the classes Resident, Hospital, and Couple are already defined as per the previous step.
def generate_test_data(num_hospitals, num_singles, num_couples):
    """
    Generates random test data for the Hospital-Resident problem with couples.

    Args:
        num_hospitals (int): Number of hospitals to create.
        num_singles (int): Number of single residents.
        num_couples (int): Number of couples (creates 2 * num_couples residents).

    Returns:
        tuple: (hospitals_list, singles_list, couples_list)
    """

    # 1. Create Hospitals with random capacities (e.g., 1 to 7 slots)
    hospitals = []
    for i in range(num_hospitals):
        cap = random.randint(1, 7)
        h_id = f"H{i+1}"
        hospitals.append(Hospital(h_id, cap))

    # 2. Create Single Residents
    singles = []
    for i in range(num_singles):
        s_id = f"S{i+1}"
        singles.append(Resident(s_id))

    # 3. Create Couples (and their constituent residents)
    couples = []
    coupled_residents = []  # We need this list for hospitals' preferences
    for i in range(num_couples):
        # Create two residents for the couple
        r1 = Resident(f"C{i+1}_M1")  # Couple i, Member 1
        r2 = Resident(f"C{i+1}_M2")  # Couple i, Member 2

        new_couple = Couple(r1, r2)
        couples.append(new_couple)
        coupled_residents.extend([r1, r2])

    # Combine all residents into one list for hospital rankings
    all_residents = singles + coupled_residents

    # --- GENERATE PREFERENCES ---

    # 4. Generate Hospital Preferences
    # Each hospital ranks ALL residents randomly
    for h in hospitals:
        # Create a copy of residents list to shuffle
        res_pool = all_residents[:]
        random.shuffle(res_pool)
        # Store only IDs as per our class design
        pref_ids = [r.resident_id for r in res_pool]
        h.set_preferences(pref_ids)

    # 5. Generate Single Resident Preferences
    # Singles rank ALL hospitals randomly
    for s in singles:
        h_pool = hospitals[:]
        random.shuffle(h_pool)
        s.preferences = [h.hospital_id for h in h_pool]

    # 6. Generate Couple Preferences (Joint Preferences)
    # Couples rank a random subset of hospital pairs (e.g., 10 pairs)
    for c in couples:
        joint_prefs = []
        # Let's generate 10 random preferred pairs for each couple
        # Note: In a real scenario, they might prefer (H1, H1) over (H1, H2).
        # Here we just generate random pairs.
        for _ in range(10):
            h1 = random.choice(hospitals).hospital_id
            h2 = random.choice(hospitals).hospital_id

            # Avoid duplicates in the preference list
            if (h1, h2) not in joint_prefs:
                joint_prefs.append((h1, h2))

        c.joint_preferences = joint_prefs

    print("\n" + "="*50)
    print("   GENERATED PREFERENCES (FOR VERIFICATION)   ")
    print("="*50)

    print("\n--- SINGLE RESIDENTS PREFERENCES ---")
    for s in singles:
        print(f"Resident {s.resident_id} wants: {s.preferences}")

    print("\n--- COUPLE JOINT PREFERENCES ---")
    for i, c in enumerate(couples):
        m1_id = c.member1.resident_id
        m2_id = c.member2.resident_id
        print(f"Couple {i+1} ({m1_id} & {m2_id}) preferences:")
        for rank, (h1, h2) in enumerate(c.joint_preferences):
            print(f"   Rank {rank}: ({h1}, {h2})")

    print("\n--- HOSPITAL PREFERENCES & CAPACITIES ---")
    for h in hospitals:
        print(
            f"Hospital {h.hospital_id} (Cap: {h.capacity}) ranks residents as:")
        print(f"   {h.preferences}")

    print("="*50 + "\n")

    return hospitals, singles, couples


def match_all(hospitals, singles, couples):
    """
    Executes the matching algorithm handling both singles and couples.
    Similar to Roth-Peranson algorithm used in NRMP.

    Args:
        hospitals (list): List of Hospital objects.
        singles (list): List of Resident objects (singles).
        couples (list): List of Couple objects.
    """

    # 1. Initialize data structures
    # example: 'H1' : Hospital(H1, cap:7)
    hospital_map = {h.hospital_id: h for h in hospitals}

    # Unified queue of applicants to process
    # Contains both Single Resident objects and Couple objects
    free_candidates = []
    free_candidates.extend(singles)
    free_candidates.extend(couples)

    print(
        f"--- Starting Joint Matching for {len(free_candidates)} candidates ---")

    while free_candidates:
        candidate = free_candidates.pop(0)

        # --- PATH A: Processing a SINGLE Resident ---
        if isinstance(candidate, Resident):
            resident = candidate

            if not hasattr(resident, 'proposal_index'):
                resident.proposal_index = 0

            if resident.proposal_index >= len(resident.preferences):
                continue

            h_id = resident.preferences[resident.proposal_index]
            hospital = hospital_map[h_id]

            if check_and_place_single(hospital, resident, free_candidates):
                print(
                    f"Single {resident.resident_id} accepted at {hospital.hospital_id}")
            else:
                # Rejected, increment index and put back in queue
                resident.proposal_index += 1
                free_candidates.append(resident)

        # --- PATH B: Processing a COUPLE ---
        elif isinstance(candidate, Couple):
            couple = candidate
            r1 = couple.member1
            r2 = couple.member2

            if couple.proposal_index >= len(couple.joint_preferences):
                continue  # Exhausted all joint options

            # Get the pair of hospitals they want next
            h1_id, h2_id = couple.joint_preferences[couple.proposal_index]

            # Handle 'None' if one partner is willing to be unemployed (optional logic)
            # For this code, we assume valid hospital IDs are always provided.
            h1 = hospital_map.get(h1_id)
            h2 = hospital_map.get(h2_id)

            # --- CRITICAL: COUPLE STABILITY CHECK ---
            # Both hospitals must be willing to take them simultaneously.
            # We "simulate" the check without modifying state first.

            can_place_r1, victim_r1 = simulate_acceptance(h1, r1)
            can_place_r2, victim_r2 = simulate_acceptance(h2, r2)

            # Special Case: If both want the SAME hospital
            if h1 == h2:
                # Need 2 slots in the same hospital
                can_place_both, victims = simulate_acceptance_same_hospital(
                    h1, r1, r2)
                if can_place_both:
                    # Execute the placement
                    place_candidate(h1, r1, victims[0] if len(
                        victims) > 0 else None, free_candidates)
                    place_candidate(h1, r2, victims[1] if len(
                        victims) > 1 else None, free_candidates)
                    print(
                        f"Couple {r1.resident_id}&{r2.resident_id} accepted at SAME {h1.hospital_id}")
                else:
                    # Rejected
                    couple.proposal_index += 1
                    free_candidates.append(couple)

            # Standard Case: Different hospitals
            elif can_place_r1 and can_place_r2:
                # Execute the placement logic (actually modify the lists)
                place_candidate(h1, r1, victim_r1, free_candidates)
                place_candidate(h2, r2, victim_r2, free_candidates)
                print(
                    f"Couple {r1.resident_id}&{r2.resident_id} accepted at {h1.hospital_id} & {h2.hospital_id}")

            else:
                # If either hospital rejects, the WHOLE couple is rejected
                couple.proposal_index += 1
                free_candidates.append(couple)

    print("--- Joint Matching Completed ---")

# --- Helper Functions to keep main loop clean ---


def simulate_acceptance(hospital, resident):
    """
    Checks if a hospital would accept a resident.
    Returns: (bool accepted, Resident victim_if_any)
    """
    rank = hospital.get_rank(resident.resident_id)
    if rank == float('inf'):
        return False, None

    # If there is space
    if len(hospital.current_matches) < hospital.capacity:
        return True, None

    # If full, check if new resident is better than the worst current
    # Sort by rank (descending) -> worst is at index -1
    sorted_matches = sorted(hospital.current_matches,
                            key=lambda r: hospital.get_rank(r.resident_id))
    worst_resident = sorted_matches[-1]

    if rank < hospital.get_rank(worst_resident.resident_id):
        return True, worst_resident  # Accepted, but this guy gets fired

    return False, None


def simulate_acceptance_same_hospital(hospital, r1, r2):
    """
    Checks if a hospital can take BOTH residents.
    Returns: (bool, [list_of_victims])
    """
    # Logic: Hospital needs 2 spots.
    # It can be 2 empty spots, 1 empty + 1 replacement, or 2 replacements.
    # This is complex, simplified version:
    # 1. Add both to current list temporarily
    # 2. Sort list
    # 3. Check if both are within the top (capacity)

    current_plus_new = hospital.current_matches + [r1, r2]
    # Filter out those not in pref list
    valid_candidates = [r for r in current_plus_new if hospital.get_rank(
        r.resident_id) != float('inf')]

    # Sort by rank (ascending = better)
    valid_candidates.sort(key=lambda r: hospital.get_rank(r.resident_id))

    # Who makes the cut?
    admitted = valid_candidates[:hospital.capacity]

    if r1 in admitted and r2 in admitted:
        # Determine victims (those who were in current_matches but not in admitted)
        victims = [r for r in hospital.current_matches if r not in admitted]
        return True, victims

    return False, []


def place_candidate(hospital, resident, victim, free_queue):
    """
    Finalizes the placement. Adds resident, removes victim.
    Victim is added back to free_queue.
    """
    # Add new
    hospital.current_matches.append(resident)
    resident.current_match = hospital

    # Remove victim if exists
    if victim:
        hospital.current_matches.remove(victim)
        victim.current_match = None

        handle_rejection_chain(victim, free_queue)


def check_and_place_single(hospital, resident, free_queue):
    # Wrapper for single logic using simulate_acceptance
    accepted, victim = simulate_acceptance(hospital, resident)
    if accepted:
        place_candidate(hospital, resident, victim, free_queue)
        return True
    return False


def handle_rejection_chain(resident, free_queue):
    """
    Handles the logic when a resident is fired.
    """
    if not resident.is_coupled:
        # Simple case: Just add single resident back to queue
        free_queue.append(resident)
        print(f"   -> Single {resident.resident_id} added back to queue.")
    else:
        # Complex case: Coupled resident fired
        couple = resident.couple_obj
        partner = couple.member2 if couple.member1 == resident else couple.member1

        print(
            f"   -> Coupled {resident.resident_id} displaced. Triggering partner withdrawal...")

        # If partner is currently matched, force them to resign
        if partner.current_match:
            print(
                f"   -> Force resignation: Partner {partner.resident_id} leaving {partner.current_match.hospital_id}")
            partner.current_match.current_matches.remove(partner)
            partner.current_match = None

        # Add the COUPLE object back to the queue (not just the resident)
        # We must make sure we don't add duplicates if it's already there
        if couple not in free_queue:
            free_queue.append(couple)
            print(
                f"   -> Couple {couple} added back to queue to try next preference.")


def verify_stability(hospitals, singles, couples):
    """
    Checks the stability of the final matching.
    Returns a list of blocking pairs (instabilities).
    If the list is empty, the matching is stable.
    """
    blocking_pairs = []
    hospital_map = {h.hospital_id: h for h in hospitals}

    print("\n--- Verifying Stability ---")

    # 1. Check Single Residents
    for resident in singles:
        # Iterate through hospitals preferred over current match
        # We look at preferences from index 0 up to current match index

        # Default: matched with nothing (worst)
        current_rank_idx = len(resident.preferences)
        if resident.current_match:
            try:
                current_rank_idx = resident.preferences.index(
                    resident.current_match.hospital_id)
            except ValueError:
                pass

        # Check all hospitals strictly better than current match
        for i in range(current_rank_idx):
            better_h_id = resident.preferences[i]
            better_hospital = hospital_map[better_h_id]

            # Does the hospital also want this resident?
            if would_hospital_accept(better_hospital, resident):
                blocking_pairs.append(
                    f"Single Blocking Pair: {resident.resident_id} prefers {better_h_id}, and {better_h_id} wants them.")

    # 2. Check Couples
    for couple in couples:
        r1 = couple.member1
        r2 = couple.member2

        # Determine index of current match in joint preferences
        current_joint_idx = len(couple.joint_preferences)

        # Construct current match tuple to find its index
        current_match_tuple = (
            r1.current_match.hospital_id if r1.current_match else None,
            r2.current_match.hospital_id if r2.current_match else None
        )

        # Note: In a real implementation, we should store the index in the couple object
        # to avoid searching. Here we search for simplicity.
        if current_match_tuple in couple.joint_preferences:
            current_joint_idx = couple.joint_preferences.index(
                current_match_tuple)

        # Check all joint preferences strictly better than current match
        for i in range(current_joint_idx):
            h1_id, h2_id = couple.joint_preferences[i]
            h1 = hospital_map.get(h1_id)
            h2 = hospital_map.get(h2_id)

            # Check logic: Both hospitals must be willing to accept the switch simultaneously

            # Case A: Same Hospital (Both want to go to H1)
            if h1_id == h2_id:
                if would_hospital_accept_pair(h1, r1, r2):
                    blocking_pairs.append(
                        f"Couple Blocking Pair: {r1.resident_id}&{r2.resident_id} prefer {h1_id} (together), and hospital accepts.")

            # Case B: Different Hospitals
            else:
                # IMPORTANT: When checking H1, we must ignore R1 if they are already there?
                # Usually blocking pairs imply a move.

                accept_r1 = would_hospital_accept(h1, r1)
                accept_r2 = would_hospital_accept(h2, r2)

                if accept_r1 and accept_r2:
                    blocking_pairs.append(
                        f"Couple Blocking Pair: {r1.resident_id}&{r2.resident_id} prefer ({h1_id}, {h2_id}) and both hospitals accept.")

    return blocking_pairs

# --- Helper Functions for Verification ---


def would_hospital_accept(hospital, resident):
    """
    Returns True if hospital would accept 'resident', 
    potentially firing someone WORSE than 'resident'.
    """
    if not hospital:
        return False  # Handles None hospitals

    res_rank = hospital.get_rank(resident.resident_id)
    if res_rank == float('inf'):
        return False  # Not on pref list

    # If there is free space
    if len(hospital.current_matches) < hospital.capacity:
        return True

    # If full, check if resident is better than the worst current match
    # We look at all current matches
    worst_rank = -1
    for curr in hospital.current_matches:
        r_rank = hospital.get_rank(curr.resident_id)
        if r_rank > worst_rank:
            worst_rank = r_rank

    # If new resident has lower rank index (better) than the worst existing one
    return res_rank < worst_rank


def would_hospital_accept_pair(hospital, r1, r2):
    """
    Returns True if hospital can take BOTH r1 and r2.
    It needs 2 slots (either empty or by firing worse candidates).
    """
    if not hospital:
        return False

    rank1 = hospital.get_rank(r1.resident_id)
    rank2 = hospital.get_rank(r2.resident_id)

    if rank1 == float('inf') or rank2 == float('inf'):
        return False

    # Calculate how many slots are needed vs available
    # This is a simplified check.
    # Logic: Merge current residents + new pair, sort, and see if both new ones make the cut.

    current_residents = hospital.current_matches[:]
    candidates = current_residents + [r1, r2]

    # Remove duplicates if they are already there (edge case)
    candidates = list(set(candidates))

    # Filter valid
    valid = [c for c in candidates if hospital.get_rank(
        c.resident_id) != float('inf')]

    # Sort by rank
    valid.sort(key=lambda r: hospital.get_rank(r.resident_id))

    # Top N make it
    top_n = valid[:hospital.capacity]

    return (r1 in top_n) and (r2 in top_n)


if __name__ == "__main__":
    # 1. Setup Simulation
    N_HOSPITALS = 5
    N_SINGLES = 10
    N_COUPLES = 5

    print("==========================================")
    print("   HOSPITAL-RESIDENT MATCHING (COUPLES)   ")
    print("==========================================")

    # 2. Generate Data
    hospitals, singles, couples = generate_test_data(
        N_HOSPITALS, N_SINGLES, N_COUPLES)

    print(f"Generated {len(hospitals)} Hospitals.")
    print(f"Generated {len(singles)} Single Residents.")
    print(f"Generated {len(couples)} Couples.")

    # 3. Run Matching Algorithm
    match_all(hospitals, singles, couples)

    # 4. Print Final Results
    print("\n--- FINAL MATCHING RESULTS ---")
    for h in hospitals:
        matches = [r.resident_id for r in h.current_matches]
        print(f"{h.hospital_id} (Cap {h.capacity}): {matches}")

    unmatched_singles = [s.resident_id for s in singles if not s.current_match]
    unmatched_couples = [c for c in couples if not c.member1.current_match]

    print(f"\nUnmatched Singles: {unmatched_singles}")
    print(f"Unmatched Couples: {unmatched_couples}")

    # 5. Verify Stability
    instabilities = verify_stability(hospitals, singles, couples)

    if not instabilities:
        print("\nSUCCESS: The matching is STABLE.")
    else:
        print(
            f"\nWARNING: Found {len(instabilities)} instabilities (Blocking Pairs):")
        for inst in instabilities:
            print(f" - {inst}")
