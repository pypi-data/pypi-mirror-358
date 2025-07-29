安装
==================================

普通安装
----------------------------------

1.1 使用 `pip` 安装：

.. prompt:: bash

    pip install dgl
    pip install unike

1.2 或使用 `uv` 安装：

.. prompt:: bash

    uv pip install dgl
    uv add unike

2. 验证：

::

    >>> import unike
    >>> unike.__version__
    '3.0.2'
    >>>

开发
----------------------------------

1. 克隆 main 分支：

.. prompt:: bash

    git clone https://github.com/CPU-DS/UniKE.git
    cd UniKE/
    uv pip install dgl
    uv sync

2. 快速开始：

.. prompt:: bash

    cd examples/TransE/
    python single_gpu_transe_FB15K.py