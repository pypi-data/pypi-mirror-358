import numpy as np
from stim import Circuit
from xarray import DataArray, Dataset

from ..layouts.layout import Layout


def sample_memory_experiment(
    layout: Layout,
    experiment: Circuit,
    num_shots: int,
    num_rounds: int,
    seed: int | None = None,
) -> Dataset:
    """Samples the given memory experiment.

    Parameters
    ----------
    layout
        Layout of the qubits for the experiment.
    experiment
        ``stim`` circuit corresponding to a memory experiment.
    num_shots
        Number of shots to simulate.
    num_rounds
        Number of rounds that the memory experiment has.
    seed
        Random seed to give to the simulator.

    Returns
    -------
    dataset
        Dataset with variables ``anc_meas``, ``data_meas``, ``ideal_anc_meas``,
        and ``ideal_data_meas``; and with coordinates ``seed``, ``shot``,
        ``qec_round``, ``anc_qubit`` and ``data_qubit``.
    """
    anc_qubits = layout.anc_qubits
    data_qubits = layout.data_qubits
    num_anc = layout.num_anc_qubits

    shots = list(range(num_shots))
    qec_rounds = list(range(1, num_rounds + 1))

    # generate noisy data
    sampler = experiment.compile_sampler(seed=seed)
    outcome_vec = sampler.sample(shots=num_shots).astype(bool)

    outcomes = outcome_vec.reshape(num_shots, -1)
    anc_outcomes, data_outcomes = np.split(outcomes, [num_rounds * num_anc], axis=1)
    anc_outcomes = anc_outcomes.reshape(num_shots, num_rounds, num_anc)

    anc_meas = DataArray(data=anc_outcomes, dims=["shot", "qec_round", "anc_qubit"])
    data_meas = DataArray(data=data_outcomes, dims=["shot", "data_qubit"])

    # generate ideal data
    ideal_experimnet = experiment.without_noise()
    sampler = ideal_experimnet.compile_sampler(seed=seed)
    outcome_vec = sampler.sample(shots=1).astype(bool)

    outcomes = np.squeeze(outcome_vec)
    anc_outcomes, data_outcomes = np.split(outcomes, [num_rounds * num_anc])
    anc_outcomes = anc_outcomes.reshape(num_rounds, num_anc)

    ideal_anc_meas = DataArray(data=anc_outcomes, dims=["qec_round", "anc_qubit"])
    ideal_data_meas = DataArray(data=data_outcomes, dims=["data_qubit"])

    dataset = Dataset(
        data_vars=dict(
            anc_meas=anc_meas,
            data_meas=data_meas,
            ideal_data_meas=ideal_data_meas,
            ideal_anc_meas=ideal_anc_meas,
        ),
        coords=dict(
            seed=seed,
            shot=shots,
            qec_round=qec_rounds,
            anc_qubit=list(anc_qubits),
            data_qubit=list(data_qubits),
        ),
    )

    return dataset
