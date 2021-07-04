import os
import math
import torch
import random

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, DistributedSampler
from torch.distributed import is_initialized
from torch.nn.utils.rnn import pad_sequence

import sentencepiece
import sacrebleu
from tqdm.auto import tqdm
import editdistance
import fairseq
from argparse import Namespace
from .S3prl_SpeechToTextTask import S3prl_SpeechToTextTask
from .dataset import DummyDataset
from .AdditionalDataset import AdditionalDataset
from fairseq.models.speech_to_text.s2t_transformer import TransformerDecoderScriptable, S2TTransformerModel
from fairseq.models.transformer import Embedding
from fairseq.data import Dictionary, encoders

class DownstreamExpert(nn.Module):
    """
    Used to handle downstream-specific operations
    eg. downstream forward, metric computation, contents to log
    """

    def __init__(self, upstream_dim, upstream_rate, downstream_expert, expdir, **kwargs):
        """
        Args:
            upstream_dim: int
                Different upstream will give different representation dimension
                You might want to first project them to the same dimension

            upstream_rate: int
                160: for upstream with 10 ms per frame
                320: for upstream with 20 ms per frame
            
            downstream_expert: dict
                The 'downstream_expert' field specified in your downstream config file
                eg. downstream/example/config.yaml

            expdir: string
                The expdir from command-line argument, you should save all results into
                this directory, like some logging files.

            **kwargs: dict
                All the arguments specified by the argparser in run_downstream.py
                and all the other fields in config.yaml, in case you need it.
                
                Note1. Feel free to add new argument for __init__ as long as it is
                a command-line argument or a config field. You can check the constructor
                code in downstream/runner.py
        """

        super(DownstreamExpert, self).__init__()


        self.src_lang = downstream_expert['src_lang']
        self.tgt_lang = downstream_expert['tgt_lang']
        self.post_process = downstream_expert['post_process']
        self.upstream_rate = upstream_rate

        self.datarc = downstream_expert['datarc']
        self.datarc['max_positions'] = downstream_expert['modelrc']['max_source_positions']


        self.task = S3prl_SpeechToTextTask.setup_task(Namespace(**downstream_expert['taskrc']))
        self.task.upstream_rate = upstream_rate

        self.data_dir = downstream_expert['taskrc']['data']

        self.criterion = self.task.build_criterion(Namespace(**downstream_expert['criterionrc']))
        self.model = self.task.build_model(Namespace(**downstream_expert['modelrc']), upstream_dim)
        self.generator = self.task.build_generator([self.model], Namespace(**downstream_expert['generatorrc']))
        self.batch_itr = {}
        # self.connector = nn.Linear(upstream_dim, self.modelrc['config']['d_model'])
        
        self.use_asr = downstream_expert['taskrc']['use_asr']

        if self.use_asr:

            rc = downstream_expert['asrrc']

            self.asr_datarc = rc['datarc']
            self.asr_weight = rc['weight']
            self.asr_dict = Dictionary.load(f"{self.data_dir}/{rc['vocab_file']}")
            rc['bpe_tokenizer']['sentencepiece_model'] = f"{self.data_dir}/{rc['bpe_tokenizer']['sentencepiece_model']}" 
            self.asr_bpe = encoders.build_bpe(Namespace(**rc['bpe_tokenizer']))
            self.asr_decoder = TransformerDecoderScriptable(
                self.model.decoder.args,
                self.asr_dict,
                Embedding(len(self.asr_dict), self.model.decoder.embed_dim, self.asr_dict.pad())
            )
            self.asr_model = S2TTransformerModel(self.model.encoder, self.asr_decoder)

            self.additional_dataset = {}


        self.register_buffer('best_score', torch.zeros(1))

    # Interface
    def get_dataloader(self, mode):
        """
        Args:
            mode: string
                'train', 'dev' or 'test'

        Return:
            a torch.utils.data.DataLoader returning each batch in the format of:

            [wav1, wav2, ...], your_other_contents1, your_other_contents2, ...

            where wav1, wav2 ... are in variable length
            each wav is torch.FloatTensor in cpu with:
                1. dim() == 1
                2. sample_rate == 16000
                3. directly loaded by torchaudio
        """


        split = self.datarc[mode]
        if split not in self.batch_itr:
            self.task.load_dataset(split=split)
            self.batch_itr[split] = self.task.get_batch_iterator(
                self.task.dataset(split),
                max_tokens=self.datarc['max_tokens'],
                max_positions=self.datarc['max_positions'],
                num_workers=self.datarc['num_workers'],
                ignore_invalid_inputs = True, ## should be more conceren
            )

        ## temperary dataloader
        return self.batch_itr[split].next_epoch_itr()

        if mode == 'train':
            return self._get_train_dataloader(split)
        else: 
            return self._get_eval_dataloader(split)

    def _get_train_dataloader(self, split):
        
        batch_itr = self.task.get_batch_iterator(
            self.task.dataset(split),
            max_tokens=self.datarc['max_tokens'],
            num_workers=self.datarc['num_workers'],
        )

        dataset = DummyDataset(
            batch_itr.dataset,
            batch_itr.batch_sampler,
            num_workers=batch_itr.num_workers,
        )

        return DataLoader(
            dataset,
            batch_size=1,
            shuffle=True,
            collate_fn = dataset.collate_fn,
        )

        # return batch_itr

        # sampler = DistributedSampler(dataset) if is_initialized() else None
        # return DataLoader(
        #     dataset, batch_size=self.datarc['train_batch_size'],
        #     shuffle=(sampler is None),
        #     sampler=sampler,
        #     num_workers=self.datarc['num_workers'],
        #     collate_fn=dataset.collate_fn
        # )


    def _get_eval_dataloader(self, split):

        batch_itr = self.task.get_batch_iterator(
            self.task.dataset(split),
            max_tokens=self.datarc['max_tokens'],
            num_workers=self.datarc['num_workers'],
        )

        dataset = DummyDataset(
            batch_itr.dataset,
            batch_itr.batch_sampler,
            num_workers=batch_itr.num_workers,
        )

        return DataLoader(
            dataset,
            batch_size=1,
            shuffle=False,
            collate_fn = dataset.collate_fn,
        )

        # return batch_itr
        # return DataLoader(
        #     dataset, batch_size=self.datarc['eval_batch_size'],
        #     shuffle=False, num_workers=self.datarc['num_workers'],
        #     collate_fn=dataset.collate_fn
        # )


    # Interface
    def forward(self, mode, features, input_dict, records, **kwargs):
        """
        Args:
            mode: string
                'train', 'dev' or 'test' for this forward step

            features:
                list of unpadded features [feat1, feat2, ...]
                each feat is in torch.FloatTensor and already
                put in the device assigned by command-line args

            your_other_contents1, ... :
                in the order defined by your dataloader (dataset + collate_fn)
                these are all in cpu, and you can move them to the same device
                as features

            records:
                defaultdict(list), by appending contents into records,
                these contents can be averaged and logged on Tensorboard
                later by self.log_records (also customized by you)

                Note1. downstream/runner.py will call self.log_records
                    1. every `log_step` during training
                    2. once after evalute the whole dev/test dataloader

                Note2. `log_step` is defined in your downstream config
                eg. downstream/example/config.yaml

        Return:
            loss:
                the loss to be optimized, should not be detached
                a single scalar in torch.FloatTensor
        """
        device = features[0].device
        features_length = torch.LongTensor([len(feature) for feature in features])
        features = pad_sequence(features, batch_first=True, padding_value=0.0)

        input_dict['net_input']['src_tokens'] = features
        input_dict['net_input']['src_lengths'] = features_length

        input_dict = fairseq.utils.move_to_cuda(input_dict, device=device)

        loss = torch.FloatTensor(0)

        if mode in ['train', 'dev']:

            encoder_out = self.model.encoder(
                src_tokens=input_dict['net_input']['src_tokens'], src_lengths=input_dict['net_input']['src_lengths']
            )

            st_decoder_out = self.model.decoder(
                prev_output_tokens=input_dict['net_input']['prev_output_tokens'],
                encoder_out=encoder_out
            )

            st_loss, _ = self.criterion.compute_loss(
                self.model,
                st_decoder_out,
                input_dict,
            )

            # st_loss, st_sample_size, st_logging_out = self.criterion(self.model, input_dict)
            # st_loss /= st_sample_size

            loss = st_loss

            if self.use_asr:

                if mode not in self.additional_dataset:
                    dataset = AdditionalDataset.from_tsv(
                        f'{self.data_dir}/{self.datarc[mode]}.tsv',
                        self.asr_datarc['key'],
                        self.asr_dict,
                        self.asr_bpe,
                    )
                    self.additional_dataset[mode] = dataset

                additional_data = self.additional_dataset[mode].get_addtional_input(input_dict['id'])
                additional_data = fairseq.utils.move_to_cuda(additional_data, device=device)

                asr_input_dict = input_dict.copy()
                asr_input_dict['net_input']['prev_output_tokens'] = additional_data['prev_output_tokens']
                asr_input_dict['target'] = additional_data['target']
                asr_input_dict['target_lengths'] = additional_data['target_lengths']
                asr_input_dict['ntokens'] = additional_data['ntokens']

                asr_decoder_out = self.asr_model.decoder(
                    prev_output_tokens=asr_input_dict['net_input']['prev_output_tokens'],
                    encoder_out=encoder_out
                )

                asr_loss, _ = self.criterion.compute_loss(
                    self.asr_model,
                    asr_decoder_out,
                    asr_input_dict
                )

                # asr_loss, asr_sample_size, asr_logging_out = self.criterion(self.asr_model, input_dict)
                # asr_loss /= asr_sample_size

                # print(input_dict['id'])
                # print(self._decode(additional_data['target'], self.asr_dict))
                # print(self._decode(input_dict['target']))

                loss = (1-self.asr_weight) * st_loss + self.asr_weight * asr_loss


            # loss, sample_size, logging_out = self.criterion(self.model, input_dict)
            loss /= input_dict['nsentences']
            records['loss'].append(loss.item())

            if self.use_asr:

                records['st_loss'].append(st_loss.item())
                records['asr_loss'].append(asr_loss.item())


        if mode in ['dev', 'test']:
            hyps, refs = self._inference_step(input_dict, self.model, self.task.target_dictionary)
            records['hyps'] += hyps
            records['refs'] += refs

            if mode in ['dev'] and self.use_asr:
                asr_hyps, asr_refs = self._inference_step(asr_input_dict, self.asr_model, self.asr_dict)
                records['asr_hyps'] += asr_hyps
                records['asr_refs'] += asr_refs

        return loss

    def _decode(self, toks, dictionary):

        toks = toks[toks != dictionary.pad()]

        s = dictionary.string(
            toks.int().cpu(),
            self.post_process,
        )

        return s if s else "<unk>"

    def _inference_step(self, input_dict, model, dictionary):
        output = self.generator.generate([model], input_dict)

        hyps = []
        refs = []

        for i in range(len(output)):

            hyps.append(
                self._decode(output[i][0]["tokens"], dictionary)
            )

            refs.append(
                self._decode(input_dict['target'][i], dictionary)
            )

        return hyps, refs

    def _metric(self, hyps, refs):

        tok = 'zh' if self.tgt_lang == 'zh' else '13a'
        bleu = sacrebleu.corpus_bleu(hyps, [refs], tokenize=tok)

        return bleu

    def _asr_metric(self, hyps, refs):

        ce = 0
        c_total = 0
        we = 0
        w_total = 0

        for hyp, ref in zip(hyps, refs):

            ce += editdistance.eval(hyp, ref)
            c_total += len(ref)

            we += editdistance.eval(hyp.split(), ref.split())
            w_total += len(ref.split())

        cer = ce / c_total
        wer = we / w_total

        return cer, wer

    # interface
    def log_records(self, mode, records, logger, global_step, batch_ids, total_batch_num, **kwargs):
        """
        Args:
            mode: string
                'train':
                    records and batchids contain contents for `log_step` batches
                    `log_step` is defined in your downstream config
                    eg. downstream/example/config.yaml

                'dev' or 'test' :
                    records and batchids contain contents for the entire evaluation dataset

            records:
                defaultdict(list), contents already prepared by self.forward

            logger:
                Tensorboard SummaryWriter
                please use f'{your_task_name}/{mode}-{key}' as key name to log your contents,
                preventing conflict with the logging of other tasks

            global_step:
                The global_step when training, which is helpful for Tensorboard logging

            batch_ids:
                The batches contained in records when enumerating over the dataloader

            total_batch_num:
                The total amount of batches in the dataloader
        
        Return:
            a list of string
                Each string is a filename we wish to use to save the current model
                according to the evaluation result, like the best.ckpt on the dev set
                You can return nothing or an empty list when no need to save the checkpoint
        """
        save_names = []

        if mode in ['train', 'dev']:

            ave_loss = sum(records['loss'])/len(records['loss'])
            logger.add_scalar(
                f'st/{mode}-loss',
                ave_loss,
                global_step=global_step
            )

            if self.use_asr:

                ave_st_loss = sum(records['st_loss'])/len(records['st_loss'])
                logger.add_scalar(
                    f'st/{mode}-st_loss',
                    ave_st_loss,
                    global_step=global_step
                )

                ave_asr_loss = sum(records['asr_loss'])/len(records['asr_loss'])
                logger.add_scalar(
                    f'st/{mode}-asr_loss',
                    ave_asr_loss,
                    global_step=global_step
                )

        if mode in ['dev', 'test']:

            bleu = self._metric(records['hyps'], records['refs'])
            logger.add_scalar(
                f'st/{mode}-bleu',
                bleu.score,
                global_step=global_step
            )
            for i in range(4):
                logger.add_scalar(
                    f'st/{mode}-bleu{i+1}',
                    bleu.precisions[i],
                    global_step=global_step
                )

            if bleu.score > self.best_score:
                self.best_score = torch.ones(1) * bleu.score
                save_names.append(f'{mode}-best.ckpt') 
        
            for i in range(5):
                tqdm.write(f"{i}")
                tqdm.write(f"[hyp]{records['hyps'][i]}")
                tqdm.write(f"[ref]{records['refs'][i]}")
            tqdm.write(f'[BLEU] {bleu.score}')
            print(bleu)

            if self.use_asr and mode in ['dev']:

                cer, wer = self._asr_metric(records['hyps'], records['refs'])
                logger.add_scalar(
                    f'st/{mode}-asr_cer',
                    cer,
                    global_step=global_step
                )
                logger.add_scalar(
                    f'st/{mode}-asr_wer',
                    wer,
                    global_step=global_step
                )
                print(f'[cer]:{cer}, [wer]:{wer}')
        return save_names