安装
==================================

Linux
----------------------------------

1. 克隆 main 分支。

.. prompt:: bash

    git clone https://github.com/CPU-DS/UniKE.git
    cd UniKE/
    uv pip install dgl
    uv sync

2. 快速开始。

.. prompt:: bash

    uv run examples/TransE/single_gpu_transe_FB15K.py
