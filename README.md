# 🦜 The S3PRL Toolkit
- The **S**elf-**S**upervised **S**peech **P**re-training and **R**epresentation **L**earning Toolkit
- Official Implementation in PyTorch

[![GitHub](https://img.shields.io/github/license/andi611/Self-Supervised-Speech-Pretraining-and-Representation-Learning)](https://en.wikipedia.org/wiki/MIT_License)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Bitbucket open issues](https://img.shields.io/bitbucket/issues/andi611/Self-Supervised-Speech-Pretraining-and-Representation-Learning)](https://github.com/andi611/Self-Supervised-Speech-Pretraining-and-Representation-Learning/issues)

Introduction
------------------------------------
This is an open source project called S3PRL, which stands for **S**elf-**S**upervised **S**peech **P**re-training and **R**epresentation **L**earning. In this toolkit, various *upstream* self-supervised speech models are implemented with easy-to-load setups, and *downstream* evaluation tasks are available with easy-to-use scripts.

**Upstream Models:**
- **Mockingjay**
    - Described in ["Mockingjay: Unsupervised Speech Representation Learning with Deep Bidirectional Transformer Encoders"](https://arxiv.org/abs/1910.12638)
    - *Transformer based, BERT-style masked reconstruction loss*
    - These papers used our implementations: [Adversarial Defense](https://arxiv.org/abs/2006.03214), [Understanding Self-attention](https://arxiv.org/abs/2006.03265)
    - Oral Lecture in [ICASSP 2020](https://2020.ieeeicassp.org/).
- **TERA**
    - Described in ["TERA: Self-Supervised Pre-training of Transformer Encoders for Speech"]()
    - *Transformer based, multi-target alteration reconstruction loss*
    - Paper are coming soon.
- **Audio ALBERT**
    - Described in ["Audio ALBERT: A Lite BERT for Self-supervised Learning of Audio Representation"](https://arxiv.org/abs/2005.08575)
    - *Transformer based, BERT-style masked reconstruction loss*
    - Submitted to [INTERSPEECH 2020](http://www.interspeech2020.org/).
- **APC**
    - Described in ["An Unsupervised Autoregressive Model for Speech Representation Learning"](https://arxiv.org/abs/1904.03240)
    - *RNN based, unidirectional reconstruction loss*
    - Accepted by [INTERSPEECH 2019](https://interspeech2019.org/).

**Downstream Tasks:**
- **Phone classification:** 
    - *Linear* classifiers
    - *1 Hidden* classifiers
    - *Concat* classifiers
    - 41 phone classes on LibriSpeech `train-clean-100` with fixed train/test splits
    - Proposed and used in the [CPC](https://arxiv.org/abs/1807.03748) and [TERA]() paper.
- **Speaker recognition:** 
    - *Frame-wise* linear classifier
    - *Utterance-wise* linear classifier
    - 251 speaker classes on LibriSpeech `train-clean-100` with fixed train/test splits
    - Proposed and used in the [CPC](https://arxiv.org/abs/1807.03748), [AALBERT](https://arxiv.org/abs/2005.08575) and [TERA]() paper.
- **ASR speech recognition:** 
    - *Hybrid DNN/HMM* speech recognition systems with the [PyTorch-Kaldi Toolkit](https://github.com/mravanelli/pytorch-kaldi)
    - We provide pre-trained models (as the DNN part of hybrid DNN/HMM) with initializers that are PyTorch-Kaldi ready.
- **Sentiment classification on spoken content:** 
    - simple *one-layer RNN* classifier on MOSEI dataset
    - Proposed and used in [Mockingjay](https://arxiv.org/abs/1910.12638).

**Usage Highlight:**
- **Acoustic feature extraction scripts:**
    - LibriSpeech and TIMIT:
        - Pre-processing with [Lirbosa](https://librosa.github.io/librosa/): *mfcc, fbank, mel, linear*
        - Pre-processing with the [Kaldi](https://github.com/kaldi-asr/kaldi) s5 recipe: *mfcc, fbank, fmllr*
    - WSJ: coming soon
    - Extracted features can be directly download from: [S3PRL Drive](http://www.bit.ly/drive-S3PRL)
    - see section: *Data preporation*
- **Pre-train your own self-supervised models:**
    - Implementation of various upstream algorithms.
    - Pre-train them on your own data.
    - see section: *Train upstream models*
- **Evaluate your own pre-trained model:**
    - Easy-to-use downstream evaluation scripts.
    - Incorporate any pre-trained model of your own.
    - see section: *Evaluating your own model*
- **Apply pre-trained models on your own task:**
    - Easy-to-use pre-trained model initialization.
    - Incorporate any downstream task with the provided pre-trained models.
    - Implemented as [PyTorch-Kaldi](https://github.com/mravanelli/pytorch-kaldi) ready DNNs.
    - Pre-trained checkpoints can be directly download from: [S3PRL Drive](http://www.bit.ly/drive-S3PRL)
    - see section: *Using upstream models with your own task*
- **Knowledge transfer of pre-trained model to downstream task:**
    - We support various methods of incoporating the pre-trained model with downstream models:
        - Extracting from the last layer
        - Learnable weighted sum extraction from all layers (similar to ELMo)
        - Fine-tuning
    - See section: *Apply different knowledge transfer methods*

Feel free to use or modify them, any bug report or improvement suggestion will be appreciated. If you have any questions, please contact tingweiandyliu@gmail.com. If you find this project helpful for your research, please do consider to cite [our papers](#Citation), thanks!

Installation
------------------------------------

#### Prerequisite
- **Python** 3 or above
- **PyTorch** 1.3.0 or above
- Computing power (**high-end GPU**) and memory space (both RAM/GPU's RAM) is extremely important if you'd like to train your own model.
- Required packages and their use are listed below, and also in [requirements.txt](requirements.txt):
```
joblib           # parallel feature extraction & decoding
librosa          # feature extraction
scipy            # feature extraction
tqdm             # verbosity
yaml             # config parser
numpy            # array computation
pandas           # data management
tensorboardX     # logger & monitor
torch            # model & learning
matplotlib       # visualization
Pillow           # visualization
```
The above packages can be installed by the command: `pip install -r requirements.txt`

- Here we list optional packages that need special attention, and we recommand you to install them manually:
```
ipdb             # debugger (Optional)
apex             # faster optimization (Optional and non-essential, only needed if enabled in config)
pydub            # audio segmentation (Optional, for MOSEI dataset preprocessing only)
Kaldi            # feature extraction (Optional, if you want to extract features by yourself)
PyTorch-Kaldi    # for hybrid ASR training (Optional)
```
For the installation and usage of Kaldi and PyTorch-Kaldi, see our supplementary wiki page: [Extracting with Kaldi](https://github.com/andi611/Self-Supervised-Speech-Pretraining-and-Representation-Learning/wiki/Extracting-with-Kaldi) and [ASR with PyTorch-Kalid](https://github.com/andi611/Self-Supervised-Speech-Pretraining-and-Representation-Learning/wiki/ASR-with-PyTorch-Kaldi)

#### Getting Started
- Clone this repo:
`git clone https://github.com/andi611/Self-Supervised-Speech-Pretraining-and-Representation-Learning.git`

#### Setting PYTHONPATH
##### Linux
- If you have any importing errors, try the following.
- Also, to use the codes in this repo from another project (e.g. PyTorch-Kaldi), you have to set a global path.
- Open the file `~/.bashrc` in your text editor – e.g. `subl ~/.bashrc`;
- Add the following line to the end:
```bash
export PYTHONPATH=/your_abs_path/Self-Supervised-Speech-Pretraining-and-Representation-Learning
```
*Make sure you change it to your own path.*
- Restart your terminal application to read in the new settings, and type this to check if everything is working: `echo $PYTHONPATH`
- Now in any python environment or .py file, we can do the following in any directory:
```python
from transformer.nn_transformer import TRANSFORMER
```
- Read the [documentations](https://bic-berkeley.github.io/psych-214-fall-2016/using_pythonpath.html) if you run in to any problem.

##### Windows
- For Windows, add the following lines to your .py code:
```python
import sys
# set this to your own path
S3PRL_PATH = "C:\\Users\\ANDYLIU\\Self-Supervised-Speech-Pretraining-and-Representation-Learning"
if S3PRL_PATH not in sys.path:
    sys.path.append(S3PRL_PATH)
```


Data preporation
------------------------------------
#### Download extracted features (RECOMMENDED):
- We provide the features we extracted for you to download directly: [S3PRL Drive](http://www.bit.ly/drive-S3PRL)
```bash
Structure of S3PRL Drive:
data/
    libri_mfcc_cmvn.zip 
    libri_fbank_cmvn.zip 
    libri_fmllr_cmvn.zip # features used for TERA
    timit_fmllr_cmvn.zip
    libri_mel160_subword5000 # features used for Mockingjay
```
- Download then unzip them, for example:
```bash
cd data/
unzip libri_fmllr_cmvn.zip
```
- Modify the setting in config files: [`config/downstream.yaml`](config/downstream.yaml), and others if needed:
```yaml
data_path: 'data/libri_fmllr_cmvn'
```

#### Preprocessing with Librosa:
##### LibriSpeech
- Download the [LibriSpeech](http://www.openslr.org/12) dataset and place under [`data/`](data/): `data/LibriSpeech`. 
- The extracted data, which is ready for training, will be stored under the same [`data/`](data/) directory by default. 
```bash
# features used for Mockingjay
python preprocess/preprocess_libri.py --feature_type=mel --data_path=../data/LibriSpeech # 160-dim
# To preprocess different acoustic features, options are:
python preprocess/preprocess_libri.py --feature_type=linear --delta=False # 1025-dim
python preprocess/preprocess_libri.py --feature_type=mfcc --delta=True --delta_delta=True # 39-dim
python preprocess/preprocess_libri.py --feature_type=fbank --delta=False # 80-dim
```

##### TIMIT
- Download the [TIMIT](https://catalog.ldc.upenn.edu/LDC93S1) dataset and place under [`data/`](data/): `data/timit`. 
- Follow the command used above:
```bash
python preprocess/preprocess_timit.py --feature_type=mel --data_path=../data/LibriSpeech # 160-dim
python preprocess/preprocess_timit.py --feature_type=linear --delta=False # 1025-dim
python preprocess/preprocess_timit.py --feature_type=mfcc --delta=True --delta_delta=True # 39-dim
python preprocess/preprocess_timit.py --feature_type=fbank --delta=False # 80-dim
```

#### Preprocessing with Kaldi:
- To extract with Kaldi, see the supplementary wiki page for detailed instructions: [Extracting with Kaldi](https://github.com/andi611/Self-Supervised-Speech-Pretraining-and-Representation-Learning/wiki/Extracting-with-Kaldi)
- Or download the extracted features from here: [S3PRL Drive](http://www.bit.ly/drive-S3PRL)
- Place the downloaded `*.zip` files under [`data/`](data/):
```bash
cd data/
unzip libri_fmllr_cmvn.zip # features used for TERA
```

#### Downstream Task Preprocessing:

##### Kaldi Phone Set (RECOMMENDED)
- 41 phone classes, this set is considered in the CPC, TERA papers.
- To use the CPC phone alignment data, use the following command:
```bash
cd data/cpc_phone
unzip converted_aligned_phones.zip
```
- Make sure that in [`config/downstream.yaml`](config/downstream.yaml), phone path is set to:
```yaml
phone_path: 'data/cpc_phone'
```
- ***Warning:** these phone alignments correspond to a feature/label for every 10ms, you need to use features with windows of 25 ms and an overlap of 10 ms, we recommand the [Kaldi extracted features](http://www.bit.ly/drive-S3PRL).*

##### Montreal Phone Set
- 72 phone classes, this set is considered in the Mockingjay paper.
- To use the [Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/) phone alignment data, download the `libri_alignment.zip` from [S3PRL Drive](http://www.bit.ly/drive-S3PRL) and place under the [`data/`](data/) directory:
```bash
cd data
unzip libri_alignment.zip
cd ..
python preprocess/preprocess_alignment.py
```
- Change the setting in [`config/downstream.yaml`](config/downstream.yaml):
```yaml
phone_path: 'data/libri_phone'
```
- ***Warning:** we recommand you use `preprocess/preprocess_libri.py --feature_type=mel` to extract matching features.*

Train upstream models
------------------------------------
- For the pre-training of each model, we provide default configs files `*.yaml` under the [`config/`](config/) directory. However, you may change them according to your needs.
- *Warning*: the parameters may not strickly follow the original papers, please verify carefully if you need them to be identical.
- The argument `--name` is used for distinction only, you can use whatever name you want.

#### Train your own Mockingjay:
```python
# Mockingjay LARGE (mel->linear), 360 hr
python run_upstream.py --run=transformer --config=config/mockingjay_libri_linearLarge.yaml --name=mockingjay_linearLarge
# Mockingjay BASE (mel->mel), 360 hr
python run_upstream.py --run=transformer --config=config/mockingjay_libri_linearLarge.yaml --name=mockingjay_linearLarge
```
#### Train your own TERA:
```python
# TERA-Base: time + channel + mag, 960 hr
python run_upstream.py --run=transformer --config=config/tera_libri_fmllrBase.yaml --name=tera_fmllrBase
# TERA-Medium: time + channel + mag, 960 hr
python run_upstream.py --run=transformer --config=config/tera_libri_fmllrMedium.yaml --name=tera_fmllrMedium
# TERA-Large: time + channel + mag, 960 hr
python run_upstream.py --run=transformer --config=config/tera_libri_fmllrLarge.yaml --name=tera_fmllrLarge
```
#### Train your own AALBERT:
```python
# AALBERT-3L, 100 hr
python run_upstream.py --run=transformer --config=config/aalbert_libri_fbank3L.yaml --name=aalbert_fbank3L
# AALBERT-6L, 360 hr
python run_upstream.py --run=transformer --config=config/aalbert_libri_fbank6L.yaml --name=aalbert_fbank6L
```
#### Train your own APC:
```python
python run_upstream.py --run=apc
```

Downstream evaluations
------------------------------------
- The below commands are used for evaluating the transformer models, where we specify `--upstream=transformer`.
- The type of pre-trained transformers (Mockingjay, AALBERT, TERA) will be decided by the pre-trained checkpoint: `--ckpt`.

#### 1) Evaluating upstream models with phone classification
```python
# **Phone Linear** Frame-wise Classification on LibriSpeech
python run_downstream.py --run=phone_linear --upstream=transformer --ckpt=path_to_ckpt/states-1000000.ckpt

# **Phone 1 Hidden** Frame-wise Classification on LibriSpeech
python run_downstream.py --run=phone_1hidden --upstream=transformer --ckpt=path_to_ckpt/states-1000000.ckpt

# **Phone Concat** Frame-wise Classification on LibriSpeech
python run_downstream.py --run=phone_concat --upstream=transformer --ckpt=path_to_ckpt/states-1000000.ckpt
```

#### 2) Evaluating upstream models with speaker recognition
```python
# **Speaker Frame**-wise Classification on LibriSpeech
python run_downstream.py --run=speaker_frame --upstream=transformer --ckpt=path_to_ckpt/states-1000000.ckpt

# **Speaker Utterance**-wise Classification on LibriSpeech
python run_downstream.py --run=speaker_utterance --upstream=transformer --ckpt=path_to_ckpt/states-1000000.ckpt
```

#### 3) Apply different knowledge transfer methods
##### 3-1) Weighted sum from all layers:
- Simply add `--weighted_sum` to the above commands.
- For example, phone linear frame-wise classification on LibriSpeech:
```python
python run_downstream.py --weighted_sum --run=phone_linear --upstream=transformer --ckpt=path_to_ckpt/states-1000000.ckpt
```

##### 3-2) Fine-tuning:
- Simply add `--fine_tune` to the above commands.
- For example, phone linear frame-wise classification on LibriSpeech:
```python
python run_downstream.py --fine_tune --run=phone_linear --upstream=transformer --ckpt=path_to_ckpt/states-1000000.ckpt
```

#### 4) Evaluating baseline features
- Simply change the `--upstream=transformer` to `--upstream=baseline`, and we no longer need to specify `--ckpt`.
- For example, phone linear frame-wise classification on LibriSpeech:
```python
python run_downstream.py --run=phone_linear --upstream=baseline
```

#### 5) Evaluating ASR with PyTorch-Kaldi scripts:
- See the supplementary wiki page for detailed instructions: [ASR with PyTorch-Kalid](https://github.com/andi611/Self-Supervised-Speech-Pretraining-and-Representation-Learning/wiki/ASR-with-PyTorch-Kaldi)

Evaluating your own model
------------------------------------
- You can easily insert your own upstream models to the evaluation script [`run_downstream.py`](run_downstream.py).
- There are only three simple requirements for each upstream model:
    1) Implement the `forward` method of `nn.Module`,
    2) Contains the `out_dim` attribute.
    3) Takes input and output in the shape of: (batch_size, time_steps, feature_dim)
- Initialize your model at the function `get_upstream_model` in [`run_downstream.py`](run_downstream.py):
```python
elif args.upstream == 'your_model':
    example_options = {'ckpt_file' : args.ckpt,
                       'input_dim' : args.input_dim,
                       'load_pretrain' : True}
    upstream_model = YOUR_MODEL(example_options)
```
- Now you can evaluate your model with `--upstream=your_model`.
- Make sure the input acoustic features align with your pre-trained model.

Using upstream models with your own task
------------------------------------
- You can also fine-tune or extract from the pre-trained upstream model on your own dataset and tasks! 
- ***IMPORTANT:** you must use input acoustic features with the **same preprocessing settings and pipeline** as pre-trained models!!!* 
- Pre-trained checkpoints can be download from: [S3PRL Drive](http://www.bit.ly/drive-S3PRL)
- Below we show an [example code](src/example_extract_finetune.py) of fine-tuning a upstream model with your own downstream model, by using the wrapper class in [nn_transformer.py](transformer/nn_transformer.py):
```python
import torch
from transformer.nn_transformer import TRANSFORMER
from downstream.model import example_classifier
from downstream.solver import get_optimizer

# setup the transformer model
options = {
    'ckpt_file'     : './result/result_transformer/tera/fmllrBase960-F-N-K-libri/states-1000000.ckpt',
    'load_pretrain' : 'True',
    'no_grad'       : 'True',
    'dropout'       : 'default',
    'spec_aug'      : 'False',
    'spec_aug_prev' : 'True',
    'weighted_sum'  : 'False',
    'select_layer'  : -1,
}
transformer = TRANSFORMER(options=options, inp_dim=40)

# setup your downstream class model
classifier = example_classifier(input_dim=768, hidden_dim=128, class_num=2).cuda()

# construct the optimizer
params = list(transformer.named_parameters()) + list(classifier.named_parameters())
optimizer = get_optimizer(params=params, lr=4e-3, warmup_proportion=0.7, training_steps=50000)

# forward
example_inputs = torch.zeros(1200, 3, 40) # A batch of spectrograms: (time_step, batch_size, dimension)
reps = transformer(example_inputs) # returns: (time_step, batch_size, hidden_size)
reps = reps.permute(1, 0, 2) # change to: (batch_size, time_step, feature_size)
labels = torch.LongTensor([0, 1, 0]).cuda()
loss = classifier(reps, labels)

# update
loss.backward()
optimizer.step()

# save
PATH_TO_SAVE_YOUR_MODEL = 'example.ckpt'
states = {'Classifier': classifier.state_dict(), 'Transformer': transformer.state_dict()}
# torch.save(states, PATH_TO_SAVE_YOUR_MODEL)
```

Development pattern for contributors
------------------------------------
1. [Create a personal fork](https://help.github.com/articles/fork-a-repo/) of the [main S3PRL repository](https://github.com/andi611/Self-Supervised-Speech-Pretraining-and-Representation-Learning) in GitHub.
2. Make your changes in a named branch different from `master`, e.g. you create a branch `new-awesome-feature`.
3. [Generate a pull request](https://help.github.com/articles/creating-a-pull-request/) through the Web interface of GitHub.
4. Please verify that your code is free of basic mistakes, we appreciate any contribution!
   
Reference
------------------------------------
1. [Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/), McAuliffe et. al.
2. [CMU MultimodalSDK](https://github.com/A2Zadeh/CMU-MultimodalSDK/blob/master/README.md), Amir Zadeh.
3. [PyTorch Transformers](https://github.com/huggingface/transformers), Hugging Face.
4. [Autoregressive Predictive Coding](https://github.com/iamyuanchung/Autoregressive-Predictive-Coding), Yu-An Chung.
5. [Contrastive Predictive Coding](https://arxiv.org/abs/1807.03748), Aaron van den Oord.
5. [End-to-end ASR Pytorch](https://github.com/Alexander-H-Liu/End-to-end-ASR-Pytorch), Alexander-H-Liu.
6. [Tacotron Preprocessing](https://github.com/r9y9/tacotron_pytorch), Ryuichi Yamamoto (r9y9)
7. [PyTorch-Kaldi](https://github.com/mravanelli/pytorch-kaldi), Mirco Ravanelli
8. [Kaldi](https://github.com/kaldi-asr/kaldi), Kaldi-ASR

Citation
------------------------------------
Here we list all papers that use our toolkit.
- Mockingjay:
```
@article{mockingjay,
   title={Mockingjay: Unsupervised Speech Representation Learning with Deep Bidirectional Transformer Encoders},
   ISBN={9781509066315},
   url={http://dx.doi.org/10.1109/ICASSP40776.2020.9054458},
   DOI={10.1109/icassp40776.2020.9054458},
   journal={ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
   publisher={IEEE},
   author={Liu, Andy T. and Yang, Shu-wen and Chi, Po-Han and Hsu, Po-chun and Lee, Hung-yi},
   year={2020},
   month={May}
}
```
- TERA:
```
@article{coming2020soon
}
```
- Mockingjay for Adversarial Defense
```
@misc{mockingjay_defense,
    title={Defense for Black-box Attacks on Anti-spoofing Models by Self-Supervised Learning},
    author={Haibin Wu and Andy T. Liu and Hung-yi Lee},
    year={2020},
    eprint={2006.03214},
    archivePrefix={arXiv},
    primaryClass={eess.AS}
}
```
- Understanding SAT:
```
@misc{understandingSAT,
    title={Understanding Self-Attention of Self-Supervised Audio Transformers},
    author={Shu-wen Yang and Andy T. Liu and Hung-yi Lee},
    year={2020},
    eprint={2006.03265},
    archivePrefix={arXiv},
    primaryClass={cs.CL}
}
```
