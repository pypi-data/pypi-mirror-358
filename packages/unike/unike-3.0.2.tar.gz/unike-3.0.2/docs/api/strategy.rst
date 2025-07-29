unike.module.strategy
===================================

.. automodule:: unike.module.strategy

.. contents:: unike.module.strategy
    :depth: 3
    :local:
    :backlinks: top

策略基类
----------------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: classtemplate.rst
    
    Strategy

策略子类
----------------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: classtemplate.rst
    
    NegativeSampling
    RGCNSampling
    CompGCNSampling

超参数优化默认搜索范围
----------------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: functiontemplate.rst

    get_negative_sampling_hpo_config
    get_rgcn_sampling_hpo_config
    get_compgcn_sampling_hpo_config