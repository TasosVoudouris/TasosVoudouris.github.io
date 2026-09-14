import multiprocessing
import random
import time
from vssKZG import setup_kzg, participant_work, verify_kzg_commitment, n

def serialize_G1(point):
    """Serialize a G1 point to a tuple of integers."""
    return (point[0], point[1], point[2])

def deserialize_G1(data):
    """Deserialize a tuple of integers to a G1 point."""
    return (int(data[0]), int(data[1]), int(data[2]))

def simulate_participant(index, num_participants, threshold, secret, g1_powers, g2_powers, return_dict):
    start_time = time.time()
    shares, commitments, alphas = participant_work(num_participants, threshold, secret, g1_powers, g2_powers)
    alpha = alphas[index]
    share = shares[index]
    proof = commitments[index]  # Simplification for example
    valid = verify_kzg_commitment(commitments[index], proof, alpha, g2_powers)
    end_time = time.time()
    # Serialize the commitment and proof
    return_dict[index] = (share, alpha, valid, end_time - start_time, serialize_G1(commitments[index]), serialize_G1(proof))

def reconstruct_secret(shares, alphas, threshold):
    from sympy import symbols, simplify
    x = symbols('x')
    lagrange_basis = []
    for i in range(threshold):
        numer = 1
        denom = 1
        for j in range(threshold):
            if i != j:
                numer *= (x - alphas[j])
                denom *= (alphas[i] - alphas[j])
        lagrange_basis.append(numer / denom)
    secret = 0
    for i in range(threshold):
        secret += shares[i] * lagrange_basis[i]
    secret = simplify(secret)
    return int(secret.evalf(subs={x: 0}) % n)

if __name__ == "__main__":
    num_participants = 3  # Number of participants
    threshold = 2  # Threshold to reconstruct the secret
    secret = random.randint(1, n-1)

    # Setup KZG commitments
    max_degree = threshold - 1
    g1_powers, g2_powers, _ = setup_kzg(max_degree)

    # Step 1: Generate keys (not used in KZG)
    # private_keys, public_keys = generate_keys(num_participants)

    # Step 2: Simulate participants
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []

    for i in range(num_participants):
        p = multiprocessing.Process(target=simulate_participant, args=(i, num_participants, threshold, secret, g1_powers, g2_powers, return_dict))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total_verification_time = 0
    shares = []
    alphas = []

    for i in range(num_participants):
        share, alpha, valid, time_taken, commitment_data, proof_data = return_dict[i]
        commitment = deserialize_G1(commitment_data)
        proof = deserialize_G1(proof_data)
        if valid:
            shares.append(share)
            alphas.append(alpha)
        print(f"Participant {i+1}: Share = {share}, Alpha = {alpha}, Verification = {'Valid' if valid else 'Invalid'}, Time taken = {time_taken:.4f} seconds")
        total_verification_time += time_taken

    print(f"Total time for verification: {total_verification_time:.4f} seconds")

    # Reconstruct the secret using a subset of valid shares
    reconstruction_start_time = time.time()
    reconstructed_secret = reconstruct_secret(shares[:threshold], alphas[:threshold], threshold)
    reconstruction_end_time = time.time()

    print(f"Reconstructed Secret: {reconstructed_secret}")
    print(f"Time taken to reconstruct the secret: {reconstruction_end_time - reconstruction_start_time:.4f} seconds")
