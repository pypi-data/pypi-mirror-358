"""
**TransR-FB15K237-single-gpu** ||
`TransR-FB15K237-single-gpu-wandb <single_gpu_transr_FB15K237_wandb.html>`_ ||
`TransR-FB15K237-single-gpu-hpo <single_gpu_transr_FB15K237_hpo.html>`_ ||
`TransR-FB15K237-accelerate <accelerate_transr_FB15K237.html>`_

TransR-FB15K237-single-gpu
=====================================================

.. Note:: created by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 7, 2023

.. Note:: updated by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 12, 2024

.. Note:: last run by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 12, 2024

这一部分介绍如何用一个 GPU 在 FB15K237 知识图谱上训练 ``TransR`` :cite:`TransR`。

导入数据
-----------------
UniKE 有两个工具用于导入数据: :py:class:`unike.data.KGEDataLoader`。
"""

from unike.data import KGEDataLoader, BernSampler, TradTestSampler
from unike.module.model import TransE, TransR
from unike.module.loss import MarginLoss
from unike.module.strategy import NegativeSampling
from unike.config import Trainer, Tester

######################################################################
# UniKE 提供了很多数据集，它们很多都是 KGE 原论文发表时附带的数据集。 
# :py:class:`unike.data.KGEDataLoader` 包含 ``in_path`` 用于传递数据集目录。

# dataloader for training
dataloader = KGEDataLoader(
	in_path = "../../benchmarks/FB15K237/", 
	batch_size = 2048,
	neg_ent = 25, 
	test = True,
	test_batch_size = 10,
	num_workers = 16,
	train_sampler = BernSampler,
	test_sampler = TradTestSampler
)

######################################################################
# --------------
#

######################################################################
# 导入模型
# ------------------
# UniKE 提供了很多 KGE 模型，它们都是目前最常用的基线模型。我们首先导入
# :py:class:`unike.module.model.TransE`，它是最简单的平移模型，
# 因为为了避免过拟合，:py:class:`unike.module.model.TransR` 实体和关系的嵌入向量初始化为
# :py:class:`unike.module.model.TransE` 的结果。

# define the transe
transe = TransE(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim = 100, 
	p_norm = 1, 
	norm_flag = True)

######################################################################
# 下面导入 :py:class:`unike.module.model.TransR` 模型，
# 是一个为实体和关系嵌入向量分别构建了独立的向量空间，将实体向量投影到特定的关系向量空间进行平移操作的模型。

transr = TransR(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim_e = 100,
	dim_r = 100,
	p_norm = 1, 
	norm_flag = True,
	rand_init = False)

######################################################################
# --------------
#


#####################################################################
# 损失函数
# ----------------------------------------
# 我们这里使用了 ``TransE`` :cite:`TransE` 原论文使用的损失函数：:py:class:`unike.module.loss.MarginLoss`，
# :py:class:`unike.module.strategy.NegativeSampling` 对
# :py:class:`unike.module.loss.MarginLoss` 进行了封装，加入权重衰减等额外项。

model_e = NegativeSampling(
	model = transe, 
	loss = MarginLoss(margin = 5.0)
)

model_r = NegativeSampling(
	model = transr,
	loss = MarginLoss(margin = 4.0)
)

######################################################################
# --------------
#

######################################################################
# 训练模型
# -------------
# UniKE 将训练循环包装成了 :py:class:`unike.config.Trainer`，
# 可以运行它的 :py:meth:`unike.config.Trainer.run` 函数进行模型学习；
# 也可以通过传入 :py:class:`unike.config.Tester`，
# 使得训练器能够在训练过程中评估模型。

# pretrain transe
trainer = Trainer(model = model_e, data_loader = dataloader.train_dataloader(),
	epochs = 1, lr = 0.5, opt_method = "sgd", use_gpu = True, device = 'cuda:0')
trainer.run()
parameters = transe.get_parameters()
transe.save_parameters("../../checkpoint/transr_transe.json")

# test the transr
tester = Tester(model = transr, data_loader = dataloader, use_tqdm = False,
                use_gpu = True, device = 'cuda:0')

# train transr
transr.set_parameters(parameters)
trainer = Trainer(model = model_r, data_loader = dataloader.train_dataloader(),
	epochs = 1000, lr = 1.0, opt_method = "sgd", use_gpu = True, device = 'cuda:0',
	tester = tester, test = True, valid_interval = 100,
	log_interval = 100, save_interval = 100, save_path = '../../checkpoint/transr.pth')
trainer.run()

######################################################################
# .. Note:: 上述代码的运行日志可以从 `此处 </zh-cn/latest/_static/logs/examples/TransR/single_gpu_transr_FB15K237.txt>`_ 下载。
# .. Note:: 上述代码的运行报告可以从 `此处 </zh-cn/latest/_static/pdfs/examples/TransR/TransR单卡训练示例（一）.pdf>`_ 下载。

######################################################################
# --------------
#