"""# Typings for the bindings

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at <https://mozilla.org/MPL/2.0/>.
"""

from enum import Enum

class FitnessStatistics:
    def __init__(
        self,
        size: int,
        min: float,
        max: float,
        sum: float,
        mean: float,
        variance: float,
    ) -> None: ...

class Chromosome:
    def __init__(self, genes: list[int], fitness: float | None) -> None: ...

class Population:
    def __init__(self, chromosomes: list[Chromosome], generation: int) -> None: ...

class HallOfFame:
    def __init__(
        self, chromosomes: list[Chromosome], uniques: set[list[int]], capacity: int
    ) -> None: ...

class Lineage:
    def __init__(
        self,
        generations: list[Population],
        records: list[FitnessStatistics],
        hall_of_fame: HallOfFame,
        n_generations: int | None = None,
        n_records: int | None = None,
    ) -> None: ...

class ConvergenceKinds(Enum):
    Never = "Never"

class CrossoverKinds(Enum):
    IPX = "IPX"
    Point = "Point"
    Blend = "Blend"
    SimulatedBinary = "SimulatedBinary"

class CrossoverBlend:
    def __init__(self, alpha: float) -> None: ...

class CrossoverSimulatedBinary:
    def __init__(self, eta: float) -> None: ...

class EvaluatorKinds(Enum):
    FeedbackDistance = "FeedbackDistance"
    FeedbackMarks = "FeedbackMarks"
    LowerLeftDistance = "LowerLeftDistance"
    Value = "Value"

class EvaluatorMatrix:
    def __init__(
        self, kind: EvaluatorKinds, matrix: list[float], offset: int | None = None
    ) -> None: ...
    @staticmethod
    def kinds() -> set[EvaluatorKinds]: ...

class EvaluatorValue:
    def __init__(self, value: float) -> None: ...

class GeneratorKinds(Enum):
    RandomSequence = "RandomSequence"

class MutatorKinds(Enum):
    Swap = "Swap"

class MutatorSwap:
    def __init__(self, p_swap: float) -> None: ...

class RecorderKinds(Enum):
    FitnessStatistics = "FitnessStatistics"
    HdrHistogram = "HdrHistogram"

class RecorderHdrHistogram:
    def __init__(self, sigfig: int) -> None: ...

class SelectorKinds(Enum):
    Roulette = "Roulette"
    Random = "Random"

class SequencingSettings:
    def __init__(
        self,
        n_genes: int,
        p_crossover: float,
        p_mutation: float,
        n_chromosomes: int | None = None,
        n_generations: int | None = None,
        n_records: int | None = None,
        n_hall_of_fame: int | None = None,
    ) -> None: ...

def sequence_sga(
    settings: SequencingSettings,
    generator: GeneratorKinds,
    evaluator: EvaluatorMatrix | EvaluatorValue,
    recorder: RecorderHdrHistogram | RecorderKinds,
    selector: SelectorKinds,
    crossover: CrossoverBlend | CrossoverSimulatedBinary | CrossoverKinds,
    mutator: MutatorSwap,
) -> Lineage: ...
