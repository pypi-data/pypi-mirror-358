# -*- coding: utf-8 -*-
# file: abstract_dataset.py
# time: 14:13 06/04/2024
# author: YANG, HENG <hy345@exeter.ac.uk> (杨恒)
# github: https://github.com/yangheng95
# huggingface: https://huggingface.co/yangheng
# google scholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# Copyright (C) 2019-2024. All Rights Reserved.
import json

import numpy as np
import torch

from ..abc.abstract_dataset import OmniGenomeDataset
from ..misc.utils import fprint
from ... import __name__, __version__


class OmniGenomeDatasetForTokenClassification(OmniGenomeDataset):
    def __init__(self, data_source, tokenizer, max_length=None, **kwargs):
        super(OmniGenomeDatasetForTokenClassification, self).__init__(
            data_source, tokenizer, max_length, **kwargs
        )
        self.metadata.update(
            {
                "library_name": __name__,
                "omnigenome_version": __version__,
                "task": "genome_token_classification",
            }
        )

        for key, value in kwargs.items():
            self.metadata[key] = value

    def prepare_input(self, instance, **kwargs):
        labels = -100
        if isinstance(instance, str):
            sequence = instance
        elif isinstance(instance, dict):
            sequence = (
                instance.get("seq", None)
                if "seq" in instance
                else instance.get("sequence", None)
            )
            label = instance.get("label", None)
            labels = instance.get("labels", None)
            labels = labels if labels is not None else label
            if not sequence:
                raise Exception(
                    "The input instance must contain a 'seq' or 'sequence' key."
                )
        else:
            raise Exception("Unknown instance format.")

        tokenized_inputs = self.tokenizer(
            sequence,
            padding=kwargs.get("padding", "do_not_pad"),
            truncation=kwargs.get("truncation", True),
            max_length=self.max_length,
            return_tensors="pt",
        )
        for col in tokenized_inputs:
            tokenized_inputs[col] = tokenized_inputs[col].squeeze()

        if labels is not None:
            if len(set(self.label2id.keys()) | set([str(l) for l in labels])) != len(
                set(self.label2id.keys())
            ):
                fprint(
                    f"Warning: The labels <{labels}> in the input instance do not match the label2id mapping."
                )
            labels = (
                [-100]
                + [self.label2id.get(str(l), -100) for l in labels][
                    : self.max_length - 2
                ]
                + [-100]
            )

        tokenized_inputs["labels"] = torch.tensor(labels)
        return tokenized_inputs


class OmniGenomeDatasetForSequenceClassification(OmniGenomeDataset):
    def __init__(self, data_source, tokenizer, max_length=None, **kwargs):
        super(OmniGenomeDatasetForSequenceClassification, self).__init__(
            data_source, tokenizer, max_length, **kwargs
        )

        self.metadata.update(
            {
                "library_name": __name__,
                "omnigenome_version": __version__,
                "task": "genome_sequence_classification",
            }
        )
        for key, value in kwargs.items():
            self.metadata[key] = value

    def prepare_input(self, instance, **kwargs):
        labels = -100
        if isinstance(instance, str):
            sequence = instance
        elif isinstance(instance, dict):
            sequence = (
                instance.get("seq", None)
                if "seq" in instance
                else instance.get("sequence", None)
            )
            label = instance.get("label", None)
            labels = instance.get("labels", None)
            labels = labels if labels is not None else label
        else:
            raise Exception("Unknown instance format.")

        tokenized_inputs = self.tokenizer(
            sequence,
            padding=kwargs.get("padding", "do_not_pad"),
            truncation=kwargs.get("truncation", True),
            max_length=self.max_length,
            return_tensors="pt",
        )
        for col in tokenized_inputs:
            tokenized_inputs[col] = tokenized_inputs[col].squeeze()

        if labels is not None:
            if len(set(self.label2id.keys()) | set([str(labels)])) != len(
                set(self.label2id.keys())
            ):
                fprint(
                    f"Warning: The labels <{labels}> in the input instance do not match the label2id mapping."
                )
            labels = self.label2id.get(str(labels), -100) if self.label2id else labels
            try:
                labels = int(labels)
            except Exception as e:
                # Will be error if your misused data class,
                # check if you are looking for a token classification task
                raise Exception(
                    "The input instance must contain a 'label' or 'labels' key. And the label must be an integer."
                )
        tokenized_inputs["labels"] = torch.tensor(labels)
        return tokenized_inputs


class OmniGenomeDatasetForTokenRegression(OmniGenomeDataset):
    def __init__(self, data_source, tokenizer, max_length=None, **kwargs):
        super(OmniGenomeDatasetForTokenRegression, self).__init__(
            data_source, tokenizer, max_length, **kwargs
        )

        self.metadata.update(
            {
                "library_name": __name__,
                "omnigenome_version": __version__,
                "task": "genome_token_regression",
            }
        )

        for key, value in kwargs.items():
            self.metadata[key] = value

    def prepare_input(self, instance, **kwargs):
        labels = -100
        if isinstance(instance, str):
            sequence = instance
        elif isinstance(instance, dict):
            sequence = (
                instance.get("seq", None)
                if "seq" in instance
                else instance.get("sequence", None)
            )
            label = instance.get("label", None)
            labels = instance.get("labels", None)
            labels = labels if labels is not None else label
        else:
            raise Exception("Unknown instance format.")

        tokenized_inputs = self.tokenizer(
            sequence,
            padding=kwargs.get("padding", "do_not_pad"),
            truncation=kwargs.get("truncation", True),
            max_length=self.max_length,
            return_tensors="pt",
        )
        for col in tokenized_inputs:
            tokenized_inputs[col] = tokenized_inputs[col].squeeze()

        if labels is not None:
            # Will be error if your misused data class,
            # check if you are looking for a sequence classification task
            try:
                _labels = json.loads(labels)
            except:
                seps = [" ", ",", ";", "\t"]
                for sep in seps:
                    _labels = labels.split(sep)
                    if len(_labels) > 1:
                        break
                labels = [l for l in _labels]
            labels = np.array(labels, dtype=np.float32)[: self.max_length - 2]
            if labels.ndim == 1:
                labels = labels.reshape(-1)
                labels = np.concatenate([[-100], labels, [-100]])
            elif labels.ndim == 2:
                labels = labels.reshape(1, -1)
                labels = np.zeros(
                    (labels.shape[0] + 2, labels.shape[1]), dtype=np.float32
                )
                for i, label in enumerate(labels):
                    labels[i] = np.concatenate(
                        [[-100] * label.shape[1], label, [-100] * label.shape[1]]
                    )
        tokenized_inputs["labels"] = torch.tensor(labels, dtype=torch.float32)
        return tokenized_inputs


class OmniGenomeDatasetForSequenceRegression(OmniGenomeDataset):
    def __init__(self, data_source, tokenizer, max_length=None, **kwargs):
        super(OmniGenomeDatasetForSequenceRegression, self).__init__(
            data_source, tokenizer, max_length, **kwargs
        )

        self.metadata.update(
            {
                "library_name": __name__,
                "omnigenome_version": __version__,
                "task": "genome_sequence_regression",
            }
        )

        for key, value in kwargs.items():
            self.metadata[key] = value

    def prepare_input(self, instance, **kwargs):
        labels = -100
        if isinstance(instance, str):
            sequence = instance
        elif isinstance(instance, dict):
            sequence = (
                instance.get("seq", None)
                if "seq" in instance
                else instance.get("sequence", None)
            )
            label = instance.get("label", None)
            labels = instance.get("labels", None)
            labels = labels if labels is not None else label
        else:
            raise Exception("Unknown instance format.")

        tokenized_inputs = self.tokenizer(
            sequence,
            padding=kwargs.get("padding", "do_not_pad"),
            truncation=kwargs.get("truncation", True),
            max_length=self.max_length,
            return_tensors="pt",
        )
        for col in tokenized_inputs:
            tokenized_inputs[col] = tokenized_inputs[col].squeeze()

        if labels is not None:
            labels = np.array(labels, dtype=np.float32)
            if labels.ndim == 1:
                labels = labels.reshape(-1)
            elif labels.ndim == 2:
                labels = labels.reshape(1, -1)

        tokenized_inputs["labels"] = torch.tensor(labels, dtype=torch.float32)

        return tokenized_inputs
