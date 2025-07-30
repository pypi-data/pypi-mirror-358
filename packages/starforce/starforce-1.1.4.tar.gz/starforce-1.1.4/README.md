# StarForce

Dual system training framework for robotics.

The overall structure borrowed from GR00T, with these modifications:

- Simplifer VLM model, introduced more advanced VLM and larger slow system;
- Connecting fast system without cross-attention, using text encoder instead;



## Slow thought system

will goes `starforce/model/backbone` contains various VLMs. Provides a unified interface connect with fast system (action expert)



## Fast action system

Currently support:

- DiT: diffusion transformer
- QwenFlow: flowmatching based action expert



## Env install

```
pip install -e .[base]
```




## Training

training scripts goes to `scripts/xxx.sh`

training fast system:

```
sh scripts/v0/sl_0.sh

```

training slow thinking system:






