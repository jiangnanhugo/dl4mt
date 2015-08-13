#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from argparse import ArgumentParser

from utils import load_data, load_datagivendict
from lm import NeuralLM
from deepy.trainers import SGDTrainer, LearningRateAnnealer, AdamTrainer
from deepy.layers import LSTM
from layers import FullOutputLayer
import theano.tensor as T

logging.basicConfig(level=logging.INFO)

default_model = os.path.join(os.path.dirname(__file__), "models", "lstm_rnnlm2.gz")
default_dict  = os.path.join(os.path.dirname(__file__), "resources", "vocab.xinhua_u8.en.pkl")

if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument("--model", default='')
    ap.add_argument("--dictpath", default=default_dict)
    ap.add_argument("--small", action="store_true")
    args = ap.parse_args()

    vocab, lmdata = load_datagivendict(dictpath=args.dictpath, small=args.small, history_len=5, batch_size=16)
    inputx=T.imatrix('x')
    model = NeuralLM(len(vocab), test_data=None, input_tensor=inputx)
    model.stack(LSTM(hidden_size=100, output_type="sequence",
                    persistent_state=True, batch_size=lmdata.size,
                    reset_state_for_input=0),
                FullOutputLayer(len(vocab)))

    if os.path.exists(args.model):
        model.load_params(args.model)

    trainer = SGDTrainer(model, {"learning_rate": LearningRateAnnealer.learning_rate(1.2),
                                 "weight_l2": 1e-7})
    annealer = LearningRateAnnealer(trainer)

    trainer.run(lmdata, controllers=[annealer])

    model.save_params(default_model)