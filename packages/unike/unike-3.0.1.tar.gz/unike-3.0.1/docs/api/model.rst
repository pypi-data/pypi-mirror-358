unike.module.model
===================================

.. automodule:: unike.module.model

.. contents:: unike.module.model
    :depth: 3
    :local:
    :backlinks: top

基础模块
----------------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: classtemplate.rst
    
    CompGCNCov

模型基类
----------------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: classtemplate.rst
    
    Model

平移模型
----------------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: classtemplate.rst
    
    TransE
    TransH
    TransR
    TransD
    RotatE

语义匹配模型
----------------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: classtemplate.rst
    
    RESCAL
    DistMult
    HolE
    ComplEx
    Analogy
    SimplE

图神经网络模型
----------------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: classtemplate.rst
    
    RGCN
    CompGCN

平移模型超参数优化默认搜索范围
----------------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: functiontemplate.rst

    get_transe_hpo_config
    get_transh_hpo_config
    get_transr_hpo_config
    get_transd_hpo_config
    get_rotate_hpo_config

语义匹配模型超参数优化默认搜索范围
----------------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: functiontemplate.rst

    get_rescal_hpo_config
    get_distmult_hpo_config
    get_hole_hpo_config
    get_complex_hpo_config
    get_analogy_hpo_config
    get_simple_hpo_config

图神经网络模型超参数优化默认搜索范围
----------------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: functiontemplate.rst

    get_rgcn_hpo_config
    get_compgcn_hpo_config