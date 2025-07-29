"""
`TransE-FB15K-single-gpu <single_gpu_transe_FB15K.html>`_ ||
`TransE-FB15K-single-gpu-wandb <single_gpu_transe_FB15K_wandb.html>`_ ||
`TransE-FB15K-single-gpu-hpo <single_gpu_transe_FB15K_hpo.html>`_ ||
**TransE-FB15K-accelerate** ||
`TransE-FB15K-accelerate-wandb <accelerate_transe_FB15K_wandb.html>`_ ||
`TransE-FB15K237-single-gpu-wandb <single_gpu_transe_FB15K237_wandb.html>`_ ||
`TransE-WN18RR-single-gpu-adv-wandb <single_gpu_transe_WN18_adv_sigmoidloss_wandb.html>`_

TransE-FB15K-accelerate
====================================================================

.. Note:: created by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 7, 2023

.. Note:: updated by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 11, 2024

.. Note:: last run by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 11, 2024

这一部分介绍如何用多个 GPU 在 ``FB15k`` 知识图谱上训练 ``TransE`` :cite:`TransE`。

由于多 GPU 设置依赖于 `accelerate <https://github.com/huggingface/accelerate>`_ ，
因此，您需要首先需要创建并保存一个配置文件（如果想获得更详细的配置文件信息请访问 :ref:`多GPU配置 <accelerate-config>` ）：

.. prompt:: bash

	accelerate config
    
然后，您可以开始训练：

.. prompt:: bash

	accelerate launch accelerate_transe_FB15K.py

导入数据
-----------------
UniKE 有 1 个工具用于导入数据: :py:class:`unike.data.KGEDataLoader`。
"""

from unike.data import KGEDataLoader, BernSampler, TradTestSampler
from unike.module.model import TransE
from unike.module.loss import MarginLoss
from unike.module.strategy import NegativeSampling
from unike.config import accelerator_prepare
from unike.config import Trainer, Tester

######################################################################
# pybind11-KE 提供了很多数据集，它们很多都是 KGE 原论文发表时附带的数据集。
# :py:class:`unike.data.KGEDataLoader` 包含 ``in_path`` 用于传递数据集目录。

# dataloader for training
dataloader = KGEDataLoader(
    in_path = "../../benchmarks/FB15K/",
    batch_size = 8192,
    neg_ent = 25,
    test = True,
    test_batch_size = 256,
    num_workers = 16,
    train_sampler = BernSampler,
    test_sampler = TradTestSampler
)

######################################################################
# --------------
#

################################
# 导入模型
# ------------------
# UniKE 提供了很多 KGE 模型，它们都是目前最常用的基线模型。我们下面将要导入
# :py:class:`unike.module.model.TransE`，它是最简单的平移模型。

# define the model
transe = TransE(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim = 50, 
	p_norm = 1, 
	norm_flag = True
)

######################################################################
# --------------
#


#####################################################################
# 损失函数
# ----------------------------------------
# 我们这里使用了 ``TransE`` :cite:`TransE` 原论文使用的损失函数：:py:class:`unike.module.loss.MarginLoss`，
# :py:class:`unike.module.strategy.NegativeSampling` 对
# :py:class:`unike.module.loss.MarginLoss` 进行了封装，加入权重衰减等额外项。

# define the loss function
model = NegativeSampling(
	model = transe, 
	loss = MarginLoss(margin = 1.0)
)

######################################################################
# --------------
#

######################################################################
# 训练模型
# -------------
# 为了进行多 GPU 训练，需要先调用 :py:meth:`unike.config.accelerator_prepare` 对数据和模型进行包装。
#
# UniKE 将训练循环包装成了 :py:class:`unike.config.Trainer`，
# 可以运行它的 :py:meth:`unike.config.Trainer.run` 函数进行模型学习；
# 也可以通过传入 :py:class:`unike.config.Tester`，
# 使得训练器能够在训练过程中评估模型。

dataloader, model, accelerator = accelerator_prepare(
    dataloader,
    model
)

# test the model
tester = Tester(model = transe, data_loader=dataloader)

# train the model
trainer = Trainer(model = model, data_loader = dataloader.train_dataloader(),
	epochs = 1000, lr = 0.01, accelerator = accelerator,
	tester = tester, test = True, valid_interval = 100,
	log_interval = 100, save_interval = 100,
	save_path = '../../checkpoint/transe.pth', delta = 0.01)
trainer.run()

######################################################################
# .. Note:: 上述代码的运行日志可以从 `此处 </zh-cn/latest/_static/logs/examples/TransE/accelerate_transe_FB15K.txt>`_ 下载。

######################################################################
# --------------
#