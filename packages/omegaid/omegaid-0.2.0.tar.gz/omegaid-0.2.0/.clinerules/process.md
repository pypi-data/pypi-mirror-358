# OmegaID 开发待办事项

## 阶段一：测试驱动开发 (TDD)

- [x] **数值完整性测试**
  - [x] 创建 `omegaid/tests/test_numerical_integrity.py`。
  - [x] 在测试脚本中加载 `phyid` 的原始测试数据 (`.mat` 文件)。
  - [x] 调用原始 `phyid.calc_PhiID` 函数计算预期结果。
  - [x] 调用新的 `omegaid` 实现（NumPy 后端）计算实际结果。
  - [x] 使用 `np.allclose` 断言两个结果在数值上一致，确保重构的正确性。
  - [x] 额外使用随机数据，以进一步确保两套算法的结果一致

- [x] **性能基准测试**
  - [x] 创建 `omegaid/tests/benchmark.py`。
  - [x] 实现一个计时工具（装饰器或上下文管理器）来精确测量函数执行时间。
  - [x] 分别对 `phyid` (原始 Scipy)、`omegaid` (NumPy 后端) 和 `omegaid` (CuPy 后端) 的核心计算函数进行基准测试。
  - [x] 设计测试用例，使用不同规模的随机数据 (例如, 1k, 10k 数据点) 来评估不同负载下的性能。
  - [x] 将性能比较结果（执行时间、与原始实现的加速比）以清晰的表格形式打印到终端。

## 阶段二：代码结构重设计与实现

- [x] **项目结构初始化**
  - [x] 初始化 `pyproject.toml` 并使用 `uv` 配置虚拟环境。

- [x] **后端兼容性层**
  - [x] 创建 `omegaid/utils/backend.py`。
  - [x] 实现一个 `get_backend()` 函数，根据环境变量 `OMEGAID_BACKEND` (值为 `numpy` 或 `cupy`) 动态导入 `numpy` 或 `cupy` 并将其赋值给 `xp`。
  - [x] 实现数据传输函数 `to_device()` 和 `to_cpu()`，用于在 CPU 和 GPU 之间移动 `xp` 数组。

- [x] **核心逻辑重构**
  - [x] 将 `phyid/measures.py` 和 `phyid/calculate.py` 的逻辑迁移到 `omegaid/core/` 下的新模块中。
  - [x] 创建 `omegaid/core/entropy.py` 用于熵相关计算。
  - [x] 创建 `omegaid/core/decomposition.py` 用于信息分解计算。
  - [x] 移除所有既有的注释和文档字符串，确保代码自解释。

- [x] **GPU 性能优化**
  - [x] **向量化重构**: 识别并重写 `_get_entropy_four_vec` 中的循环，使其成为一个单一的向量化操作，一次性计算所有熵值。
  - [x] **重写 `local_entropy_mvn`**: 在 `omegaid/core/entropy.py` 中，使用 `xp.linalg.det`, `xp.linalg.inv` 和矩阵乘法重新实现多元正态分布的 PDF 计算，完全替代 `scipy.stats.multivariate_normal.pdf`。
  - [x] **重写 `_get_atoms_four_vec`**: 在 `omegaid/core/decomposition.py` 中，使用 `xp.linalg.solve` 解决线性方程组，并利用其对批处理的支持，一次性求解所有时间点的原子。
  - [x] **性能分析与调试**: 在关键计算步骤（如协方差矩阵计算、熵计算、线性求解）前后插入时间戳记录，并将各阶段耗时打印出来，以供性能分析和瓶颈定位。

## 阶段三：文档与收尾

- [ ] 更新项目根目录的 `README.md`，提供清晰的安装指南、使用示例，并说明如何通过环境变量选择计算后端。
- [ ] 撰写一份总结报告，展示重构后的性能测试结果（特别是 CuPy 后端的加速效果），并总结关键的优化经验。
