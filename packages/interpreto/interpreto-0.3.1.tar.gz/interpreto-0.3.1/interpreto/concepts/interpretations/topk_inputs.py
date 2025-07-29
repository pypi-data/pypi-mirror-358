# MIT License
#
# Copyright (c) 2025 IRT Antoine de Saint Exupéry et Université Paul Sabatier Toulouse III - All
# rights reserved. DEEL and FOR are research programs operated by IVADO, IRT Saint Exupéry,
# CRIAQ and ANITI - https://www.deel.ai/.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Base class for concept interpretation methods.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from enum import Enum
from typing import Any

import torch
from jaxtyping import Float

from interpreto import Granularity, ModelWithSplitPoints
from interpreto.concepts.interpretations.base import BaseConceptInterpretationMethod
from interpreto.model_wrapping.model_with_split_points import ActivationGranularity
from interpreto.typing import ConceptModelProtocol, ConceptsActivations, LatentActivations


class InterpretationSources(Enum):
    """Code [:octicons-mark-github-24: `concepts/interpretations/topk_inputs.py`](https://github.com/FOR-sight-ai/interpreto/blob/main/interpreto/concepts/interpretations/topk_inputs.py)

    Possible sources of inputs to use for the Top-K Inputs concept interpretation method.
    The activations do not need to take into account the granularity of the inputs. It is managed internally.

    Valid sources are:

    - `CONCEPTS_ACTIVATIONS`: also require `inputs` to return strings but assume that the `concepts_activations` are provided and correspond to the inputs. Hence it is the fastest source.

    - `LATENT_ACTIVATIONS`: also require `inputs` to return strings but assume that the `latent_activations` are provided and correspond to the inputs.
        The latent activations can be the one used to fit the `concepts_model`. Hence the easiest source to use.

    - `INPUTS`: requires `inputs` and compute activations on them to extract the most activating inputs. It is the slowest source.

    - `VOCABULARY`: each token of the tokenizer vocabulary is considered as an `inputs`, then activations are computed. This source has the least requirements.

    - `AUTO`: depending on the provided arguments, it will select the most appropriate source. Order of preference is:
        1. `CONCEPTS_ACTIVATIONS`
        2. `LATENT_ACTIVATIONS`
        3. `INPUTS`
        4. `VOCABULARY`
    """

    CONCEPTS_ACTIVATIONS = "concepts_activations"
    LATENT_ACTIVATIONS = "latent_activations"
    INPUTS = "inputs"
    VOCABULARY = "vocabulary"
    AUTO = "auto"  # TODO: test


class TopKInputs(BaseConceptInterpretationMethod):
    """Code [:octicons-mark-github-24: `concepts/interpretations/topk_inputs.py`](https://github.com/FOR-sight-ai/interpreto/blob/main/interpreto/concepts/interpretations/topk_inputs.py)

    Implementation of the Top-K Inputs concept interpretation method also called MaxAct.
    It associate to each concept the inputs that activates it the most.
    It is the most natural way to interpret a concept, as it is the most natural way to explain a concept.
    Hence several papers used it without describing it.
    Nonetheless, we can reference Bricken et al. (2023) [^1] from Anthropic for their post on transformer-circuits.

    [^1]:
        Trenton Bricken*, Adly Templeton*, Joshua Batson*, Brian Chen*, Adam Jermyn*, Tom Conerly, Nicholas L Turner, Cem Anil, Carson Denison, Amanda Askell, Robert Lasenby, Yifan Wu, Shauna Kravec, Nicholas Schiefer, Tim Maxwell, Nicholas Joseph, Alex Tamkin, Karina Nguyen, Brayden McLean, Josiah E Burke, Tristan Hume, Shan Carter, Tom Henighan, Chris Olah
        [Towards Monosemanticity: Decomposing Language Models With Dictionary Learning](https://transformer-circuits.pub/2023/monosemantic-features)
        Transformer Circuits, 2023.

    Attributes:
        model_with_split_points (ModelWithSplitPoints): The model with split points to use for the interpretation.
        split_point (str): The split point to use for the interpretation.
        concept_model (ConceptModelProtocol): The concept model to use for the interpretation.
        activation_granularity (ActivationGranularity): The granularity at which the interpretation is computed.
            Allowed values are `TOKEN`, `WORD`, `SENTENCE`, and `SAMPLE`.
            Ignored for source `VOCABULARY`.
        source (InterpretationSources): In any case, TopKInputs requires concept-activations and inputs.
            But depending on the available variable, you will or will not have to recompute all of this activations.
            The source correspond to starting from which activations should be computed.
            Supported sources are

                - `CONCEPTS_ACTIVATIONS`: if you already have the concept activations corresponding to the inputs, you can use this.

                - `LATENT_ACTIVATIONS`: in most case you have computed latent activation to fit the concept explainer, if the granularity is the same, you can use them and not recompute the whole thing.

                - `INPUTS`: activations are computed from the text inputs, you can specify the granularity freely.

                - `VOCABULARY`: consider the tokenizer vocabulary tokens as inputs. It forces a `TOKEN` granularity.
        k (int): The number of inputs to use for the interpretation.

    Examples:
        >>> from datasets import load_dataset
        >>> from interpreto import ModelWithSplitPoints
        >>> from interpreto.concepts import NeuronsAsConcepts
        >>> from interpreto.concepts.interpretations import TopKInputs
        >>> # load and split the model
        >>> split = "bert.encoder.layer.1.output"
        >>> model_with_split_points = ModelWithSplitPoints(
        ...     "hf-internal-testing/tiny-random-bert",
        ...     split_points=[split],
        ...     model_autoclass=AutoModelForMaskedLM,
        ...     batch_size=4,
        ... )
        >>> # NeuronsAsConcepts do not need to be fitted
        >>> concept_model = NeuronsAsConcepts(model_with_split_points=model_with_split_points, split_point=split)
        >>> # extracting concept interpretations
        >>> dataset = load_dataset("cornell-movie-review-data/rotten_tomatoes")["train"]["text"]
        >>> all_top_k_words = concept_model.interpret(
        ...     interpretation_method=TopKInputs,
        ...     activation_granularity=TopKInputs.activation_granularities.WORD,
        ...     source=TopKInputs.sources.INPUTS,
        ...     k=2,
        ...     concepts_indices="all",
        ...     inputs=dataset,
        ...     latent_activations=activations,
        ... )
    """

    activation_granularities = ActivationGranularity
    sources = InterpretationSources

    def __init__(
        self,
        *,
        model_with_split_points: ModelWithSplitPoints,
        concept_model: ConceptModelProtocol,
        activation_granularity: ActivationGranularity = ActivationGranularity.WORD,
        source: InterpretationSources,
        split_point: str | None = None,
        k: int = 5,
    ):
        super().__init__(
            model_with_split_points=model_with_split_points, concept_model=concept_model, split_point=split_point
        )

        if source not in InterpretationSources:
            raise ValueError(f"The source {source} is not supported. Supported sources: {InterpretationSources}")

        if activation_granularity not in (
            ActivationGranularity.TOKEN,
            ActivationGranularity.WORD,
            ActivationGranularity.SENTENCE,
            ActivationGranularity.SAMPLE,
        ):
            raise ValueError(
                f"The granularity {activation_granularity} is not supported. Supported `activation_granularities`: TOKEN, WORD, SENTENCE, and SAMPLE"
            )

        self.activation_granularity = activation_granularity
        self.source = source
        self.k = k

    def _concepts_activations_from_source(
        self,
        inputs: list[str] | None = None,
        latent_activations: Float[torch.Tensor, "nl d"] | None = None,
        concepts_activations: Float[torch.Tensor, "nl cpt"] | None = None,
    ) -> tuple[list[str], Float[torch.Tensor, "nl cpt"]]:
        # determine the automatic source
        source = self.source
        if source is InterpretationSources.AUTO:
            if concepts_activations is not None:
                source = InterpretationSources.CONCEPTS_ACTIVATIONS
            elif latent_activations is not None:
                source = InterpretationSources.LATENT_ACTIVATIONS
            elif inputs is not None:
                source = InterpretationSources.INPUTS
            else:
                source = InterpretationSources.VOCABULARY

        # vocabulary source: construct the inputs from the vocabulary and compute the latent activations
        if source is InterpretationSources.VOCABULARY:
            # extract and sort the vocabulary
            vocab_dict: dict[str, int] = self.model_with_split_points.tokenizer.get_vocab()
            input_ids: list[int]
            inputs, input_ids = zip(*vocab_dict.items(), strict=True)  # type: ignore

            # compute the vocabulary's latent activations
            input_tensor: Float[torch.Tensor, "v 1"] = torch.tensor(input_ids).unsqueeze(1)
            activations_dict: dict[str, LatentActivations] = self.model_with_split_points.get_activations(
                input_tensor, activation_granularity=ModelWithSplitPoints.activation_granularities.ALL_TOKENS
            )
            latent_activations = self.model_with_split_points.get_split_activations(
                activations_dict, split_point=self.split_point
            )

        # not vocabulary source: ensure that the inputs are provided
        if inputs is None:
            raise ValueError(f"The source {self.source} requires inputs to be provided. Please provide inputs.")

        # inputs source: compute the latent activations from the inputs
        if source is InterpretationSources.INPUTS:
            activations_dict: dict[str, LatentActivations] = self.model_with_split_points.get_activations(
                inputs, activation_granularity=self.activation_granularity
            )
            latent_activations = self.model_with_split_points.get_split_activations(
                activations_dict, split_point=self.split_point
            )

        # latent activation source: ensure that the latent activations are provided
        if source is InterpretationSources.LATENT_ACTIVATIONS:
            if latent_activations is None:
                raise ValueError(
                    f"The source {self.source} requires latent activations to be provided. Please provide latent activations."
                )

        # not concepts activation source: compute the concepts activations from the latent activations
        if source in [
            InterpretationSources.VOCABULARY,
            InterpretationSources.INPUTS,
            InterpretationSources.LATENT_ACTIVATIONS,
        ]:
            if hasattr(self.concept_model, "device"):
                latent_activations = latent_activations.to(self.concept_model.device)  # type: ignore
            concepts_activations = self.concept_model.encode(latent_activations)
            if isinstance(concepts_activations, tuple):
                concepts_activations = concepts_activations[1]  # temporary fix, issue #65

        # concepts activation source: ensure that the concepts activations are provided
        if concepts_activations is None:
            raise ValueError(
                f"The source {self.source} requires concepts activations to be provided. Please provide concepts activations."
            )

        return inputs, concepts_activations

    def _get_granular_inputs(self, inputs: list[str]) -> list[str]:
        if self.source is InterpretationSources.VOCABULARY:
            # no activation_granularity is needed
            return inputs

        tokens = self.model_with_split_points.tokenizer(
            inputs, return_tensors="pt", padding=True, return_offsets_mapping=True
        )
        if self.activation_granularity is ActivationGranularity.SAMPLE:
            granular_inputs: list[str] = inputs
        else:
            list_list_str: list[list[str]] = Granularity.get_decomposition(
                tokens,
                granularity=self.activation_granularity.value,  # type: ignore
                tokenizer=self.model_with_split_points.tokenizer,
                return_text=True,
            )  # type: ignore

            # flatten list of list of strings
            granular_inputs: list[str] = [string for list_str in list_list_str for string in list_str]

        return granular_inputs

    def _verify_concepts_indices(
        self,
        concepts_activations: ConceptsActivations,
        concepts_indices: int | list[int],
    ) -> list[int]:
        # take subset of concepts as specified by the user
        if isinstance(concepts_indices, int):
            concepts_indices = [concepts_indices]

        if not isinstance(concepts_indices, list) or not all(isinstance(c, int) for c in concepts_indices):
            raise ValueError(
                f"`concepts_indices` should be 'all', an int, or a list of int. Received {concepts_indices}."
            )

        if max(concepts_indices) >= concepts_activations.shape[1] or min(concepts_indices) < 0:
            raise ValueError(
                f"At least one concept index out of bounds. `max(concepts_indices)`: {max(concepts_indices)} >= {concepts_activations.shape[1]}."
            )

        return concepts_indices

    def _topk_inputs_from_concepts_activations(
        self,
        inputs: list[str],  # (nl,)
        concepts_activations: ConceptsActivations,  # (nl, cpt)
        concepts_indices: list[int],  # TODO: sanitize this previously
    ) -> Mapping[int, Any]:
        # increase the number k to ensure that the top-k inputs are unique
        k = self.k * max(Counter(inputs).values())
        k = min(k, concepts_activations.shape[0])

        # Shape: (n*l, cpt_of_interest)
        concepts_activations = concepts_activations.T[concepts_indices].T

        # extract indices of the top-k input tokens for each specified concept
        topk_output = torch.topk(concepts_activations, k=k, dim=0)
        all_topk_activations = topk_output[0].T  # Shape: (cpt_of_interest, k)
        all_topk_indices = topk_output[1].T  # Shape: (cpt_of_interest, k)

        # create a dictionary with the interpretation
        interpretation_dict = {}
        # iterate over required concepts
        for cpt_idx, topk_activations, topk_indices in zip(
            concepts_indices, all_topk_activations, all_topk_indices, strict=True
        ):
            interpretation_dict[cpt_idx] = {}
            # iterate over k
            for activation, input_index in zip(topk_activations, topk_indices, strict=True):
                # ensure that the input is not already in the interpretation
                if len(interpretation_dict[cpt_idx]) >= self.k:
                    break
                if inputs[input_index] in interpretation_dict[cpt_idx]:
                    continue
                if activation == 0:
                    break
                # set the kth input for the concept
                interpretation_dict[cpt_idx][inputs[input_index]] = activation.item()

            # if no inputs were found for the concept, set it to None
            # TODO: see if we should remove the concept completely
            if len(interpretation_dict[cpt_idx]) == 0:
                interpretation_dict[cpt_idx] = None
        return interpretation_dict

    def interpret(
        self,
        concepts_indices: int | list[int],
        inputs: list[str] | None = None,
        latent_activations: LatentActivations | None = None,
        concepts_activations: ConceptsActivations | None = None,
    ) -> Mapping[int, Any]:
        """
        Give the interpretation of the concepts dimensions in the latent space into a human-readable format.
        The interpretation is a mapping between the concepts indices and a list of inputs allowing to interpret them.
        The granularity of input examples is determined by the `activation_granularity` class attribute.

        The returned inputs are the most activating inputs for the concepts.

        The required arguments depend on the `source` class attribute.

        If all activations are zero, the corresponding concept interpretation is set to `None`.

        Args:
            concepts_indices (int | list[int]): The indices of the concepts to interpret.
            inputs (list[str] | None): The inputs to use for the interpretation.
                Necessary if the source is not `VOCABULARY`, as examples are extracted from the inputs.
            latent_activations (Float[torch.Tensor, "nl d"] | None): The latent activations to use for the interpretation.
                Necessary if the source is `LATENT_ACTIVATIONS`.
                Otherwise, it is computed from the inputs or ignored if the source is `CONCEPT_ACTIVATIONS`.
            concepts_activations (Float[torch.Tensor, "nl cpt"] | None): The concepts activations to use for the interpretation.
                Necessary if the source is not `CONCEPT_ACTIVATIONS`. Otherwise, it is computed from the latent activations.

        Returns:
            Mapping[int, Any]: The interpretation of the concepts indices.

        Raises:
            ValueError: If the arguments do not correspond to the specified source.
        """
        # compute the concepts activations from the provided source, can also create inputs from the vocabulary
        sure_inputs: list[str]  # Verified by concepts_activations_from_source
        sure_concepts_activations: Float[torch.Tensor, "ng cpt"]  # Verified by concepts_activations_from_source
        sure_inputs, sure_concepts_activations = self._concepts_activations_from_source(
            inputs, latent_activations, concepts_activations
        )

        concepts_indices = self._verify_concepts_indices(
            concepts_activations=sure_concepts_activations, concepts_indices=concepts_indices
        )

        granular_inputs: list[str]  # len: ng, inputs becomes a list of elements extracted from the examples
        granular_inputs = self._get_granular_inputs(sure_inputs)
        if len(granular_inputs) != len(sure_concepts_activations):
            if latent_activations is not None and len(granular_inputs) != len(latent_activations):
                raise ValueError(
                    f"The lengths of the granulated inputs do not match le number of provided latent activations {len(granular_inputs)} != {len(latent_activations)}"
                    "If you provide latent activations, make sure they have the same granularity as the inputs."
                )
            if concepts_activations is not None and len(granular_inputs) != len(concepts_activations):
                raise ValueError(
                    f"The lengths of the granulated inputs do not match le number of provided concepts activations {len(granular_inputs)} != {len(concepts_activations)}"
                    "If you provide concepts activations, make sure they have the same granularity as the inputs."
                )
            raise ValueError(
                f"The lengths of the granulated inputs do not match le number of concepts activations {len(granular_inputs)} != {len(sure_concepts_activations)}"
            )

        return self._topk_inputs_from_concepts_activations(
            inputs=granular_inputs,
            concepts_activations=sure_concepts_activations,
            concepts_indices=concepts_indices,
        )
