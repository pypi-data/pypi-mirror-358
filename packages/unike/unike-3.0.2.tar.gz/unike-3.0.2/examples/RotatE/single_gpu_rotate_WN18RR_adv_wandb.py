"""
`RotatE-WN18RR-single-gpu-adv <single_gpu_rotate_WN18RR_adv.html>`_ ||
**RotatE-WN18RR-single-gpu-adv-wandb** ||
`RotatE-WN18RR-single-gpu-adv-hpo <single_gpu_rotate_WN18RR_adv_hpo.html>`_

RotatE-WN18RR-single-gpu-adv-wandb
====================================================================

.. Note:: created by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 7, 2023

.. Note:: updated by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 15, 2024

.. Note:: last run by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on May 15, 2024

这一部分介绍如何用一个 GPU 在 ``WN18RR`` 知识图谱上训练 ``RotatE`` :cite:`RotatE`，使用 ``wandb`` 记录实验结果。

导入数据
-----------------
UniKE 有 1 个工具用于导入数据: :py:class:`unike.data.KGEDataLoader`。
"""

from unike.utils import WandbLogger
from unike.data import KGEDataLoader, UniSampler, TradTestSampler
from unike.module.model import RotatE
from unike.module.loss import SigmoidLoss
from unike.module.strategy import NegativeSampling
from unike.config import Trainer, Tester

######################################################################
# 首先初始化 :py:class:`unike.utils.WandbLogger` 日志记录器，它是对 wandb 初始化操作的一层简单封装。

wandb_logger = WandbLogger(
	project="pybind11-ke",
	name="RotatE-WN18RR",
	config=dict(
		in_path = '../../benchmarks/WN18RR/',
		batch_size = 2000,
		neg_ent = 64,
		test = True,
		test_batch_size = 10,
		num_workers = 16,
		dim = 1024,
		margin = 6.0,
		epsilon = 2.0,
		adv_temperature = 2,
		regul_rate = 0.0,
        use_tqdm = False,
		use_gpu = True,
		device = 'cuda:1',
		epochs = 6000,
		lr = 2e-5,
		opt_method = 'adam',
		valid_interval = 100,
		log_interval = 100,
		save_interval = 100,
		save_path = '../../checkpoint/rotate.pth'
	)
)

config = wandb_logger.config

######################################################################
# UniKE 提供了很多数据集，它们很多都是 KGE 原论文发表时附带的数据集。
# :py:class:`unike.data.KGEDataLoader` 包含 ``in_path`` 用于传递数据集目录。

# dataloader for training
dataloader = KGEDataLoader(
	in_path = config.in_path, 
	batch_size = config.batch_size,
	neg_ent = config.neg_ent,
	test = config.test,
	test_batch_size = config.test_batch_size,
	num_workers = config.num_workers,
	train_sampler = UniSampler,
	test_sampler = TradTestSampler
)

######################################################################
# --------------
#

################################
# 导入模型
# ------------------
# UniKE 提供了很多 KGE 模型，它们都是目前最常用的基线模型。我们下面将要导入
# :py:class:`unike.module.model.RotatE`，它将实体表示成复数向量，关系建模为复数向量空间的旋转。

# define the model
rotate = RotatE(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim = config.dim,
	margin = config.margin,
	epsilon = config.epsilon,
)

######################################################################
# --------------
#


#####################################################################
# 损失函数
# ----------------------------------------
# 我们这里使用了逻辑损失函数：:py:class:`unike.module.loss.SigmoidLoss`，
# :py:class:`unike.module.strategy.NegativeSampling` 对
# :py:class:`unike.module.loss.SigmoidLoss` 进行了封装，加入权重衰减等额外项。

# define the loss function
model = NegativeSampling(
	model = rotate, 
	loss = SigmoidLoss(adv_temperature = config.adv_temperature),
	regul_rate = config.regul_rate
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
# 使得训练器能够在训练过程中评估模型；:py:class:`unike.config.Tester` 使用
# :py:class:`unike.data.TestDataLoader` 作为数据采样器。

# test the model
tester = Tester(model = rotate, data_loader = dataloader, use_tqdm = config.use_tqdm,
                use_gpu = config.use_gpu, device = config.device)

# train the model
trainer = Trainer(model = model, data_loader = dataloader.train_dataloader(), epochs = config.epochs,
	lr = config.lr, opt_method = config.opt_method, use_gpu = config.use_gpu, device = config.device,
	tester = tester, test = config.test, valid_interval = config.valid_interval,
	log_interval = config.log_interval, save_interval = config.save_interval,
	save_path = config.save_path, use_wandb = True)
trainer.run()

# close your wandb run
wandb_logger.finish()

######################################################################
# .. Note:: 上述代码的运行日志可以从 `此处 </zh-cn/latest/_static/logs/examples/RotatE/single_gpu_rotate_WN18RR_adv_wandb.txt>`_ 下载。
# .. Note:: 上述代码的运行报告可以从 `此处 </zh-cn/latest/_static/pdfs/examples/RotatE/RotatE单卡训练示例（一）.pdf>`_ 下载。

######################################################################
# --------------
#