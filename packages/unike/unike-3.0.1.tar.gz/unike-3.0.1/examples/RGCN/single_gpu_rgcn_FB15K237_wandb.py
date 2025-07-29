"""
`RGCN-FB15K237-single-gpu <single_gpu_rgcn_FB15K237.html>`_ ||
**RGCN-FB15K237-single-gpu-wandb** ||
`RGCN-FB15K237-single-gpu-hpo <single_gpu_rgcn_FB15K237_hpo.html>`_

RGCN-FB15K237-single-gpu-wandb
=====================================================

.. Note:: created by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 7, 2023

.. Note:: updated by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 21, 2024

.. Note:: last run by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 21, 2024

这一部分介绍如何用一个 GPU 在 FB15K237 知识图谱上训练 ``R-GCN`` :cite:`R-GCN`，使用 ``wandb`` 记录实验结果。

导入数据
-----------------
UniKE 有一个工具用于导入数据: :py:class:`unike.data.GraphDataLoader`。
"""

from unike.utils import WandbLogger
from unike.data import KGEDataLoader, RGCNSampler, RGCNTestSampler
from unike.module.model import RGCN
from unike.module.loss import RGCNLoss
from unike.module.strategy import RGCNSampling
from unike.config import Trainer, Tester

######################################################################
# 首先初始化 :py:class:`unike.utils.WandbLogger` 日志记录器，它是对 wandb 初始化操作的一层简单封装。

wandb_logger = WandbLogger(
	project="pybind11-ke",
	name="rgcn",
	config=dict(
        in_path = '../../benchmarks/FB15K237/',
        batch_size = 60000,
        neg_ent = 10,
        test = True,
        test_batch_size = 100,
        num_workers = 16,
        dim = 500,
        num_layers = 2,
        regularization = 1e-5,
        use_tqdm = False,
        use_gpu = True,
        device = 'cuda:0',
        epochs = 10000,
        lr = 0.0001,
        valid_interval = 500,
        log_interval = 500,
        save_interval = 500,
        save_path = '../../checkpoint/rgcn.pth'
	)
)

config = wandb_logger.config

######################################################################
# UniKE 提供了很多数据集，它们很多都是 KGE 原论文发表时附带的数据集。
# :py:class:`unike.data.KGEDataLoader` 包含 ``in_path`` 用于传递数据集目录。

dataloader = KGEDataLoader(
	in_path = config.in_path,
	batch_size = config.batch_size,
	neg_ent = config.neg_ent,
	test = config.test,
	test_batch_size = config.test_batch_size,
	num_workers = config.num_workers,
    train_sampler = RGCNSampler,
    test_sampler = RGCNTestSampler
)

######################################################################
# --------------
#

################################
# 导入模型
# ------------------
# UniKE 提供了很多 KGE 模型，它们都是目前最常用的基线模型。我们下面将要导入
# :py:class:`unike.module.model.RGCN`，它提出于 2017 年，是第一个图神经网络模型，

# define the model
rgcn = RGCN(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim = config.dim,
	num_layers = config.num_layers
)

######################################################################
# --------------
#


#####################################################################
# 损失函数
# ----------------------------------------
# 我们这里使用了 ``R-GCN`` :cite:`R-GCN` 原论文使用的损失函数：:py:class:`unike.module.loss.RGCNLoss`，
# :py:class:`unike.module.strategy.RGCNSampling` 对
# :py:class:`unike.module.loss.RGCNLoss` 进行了封装。

# define the loss function
model = RGCNSampling(
	model = rgcn,
	loss = RGCNLoss(model = rgcn, regularization = config.regularization)
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

# test the model
tester = Tester(
    model = rgcn, data_loader = dataloader, use_tqdm = config.use_tqdm,
    use_gpu = config.use_gpu, device = config.device
)

# train the model
trainer = Trainer(model = model, data_loader = dataloader.train_dataloader(),
	epochs = config.epochs, lr = config.lr, use_gpu = config.use_gpu, device = config.device,
	tester = tester, test = config.test, valid_interval = config.valid_interval,
    log_interval = config.log_interval, save_interval = config.save_interval,
    save_path = config.save_path, use_wandb = True
)
trainer.run()

######################################################################
# .. Note:: 上述代码的运行日志可以从 `此处 </zh-cn/latest/_static/logs/examples/RGCN/single_gpu_rgcn_FB15K237_wandb.txt>`_ 下载。
# .. Note:: 上述代码的运行报告可以从 `此处 </zh-cn/latest/_static/pdfs/examples/RGCN/RGCN单卡训练示例（一）.pdf>`_ 下载。

######################################################################
# --------------
#