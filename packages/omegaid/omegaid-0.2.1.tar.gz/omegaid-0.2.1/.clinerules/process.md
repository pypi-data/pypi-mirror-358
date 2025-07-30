# OmegaID 开发待办事项

## 已完成：初始重构与 GPU 加速

- [x] **测试驱动开发 (TDD)**: 建立了数值完整性测试和性能基准测试，确保了重构代码的正确性和高效性。
- [x] **代码结构重设计与实现**:
  - [x] **项目结构初始化**: 使用 `uv` 和 `pyproject.toml` 搭建了现代化 Python 项目环境。
  - [x] **后端兼容性层**: 实现了动态切换 NumPy/CuPy 的后端，支持 CPU 和 GPU 计算。
  - [x] **核心逻辑重构**: 将 `phyid` 的核心算法迁移至 `omegaid`，并移除了所有代码注释。
  - [x] **GPU 性能优化**: 通过向量化、重写核心数学函数（如 `local_entropy_mvn`）和利用批处理线性求解，显著提升了 GPU 计算性能。

## 阶段二：通用 n*m 多元变量分解

- [ ] **核心算法泛化**
  - [ ] 修改 `calc_PhiID` 函数签名，使其能够接受多维 `srcs` (n_srcs, n_samples) 和 `trgs` (n_trgs, n_samples) 数组。
  - [ ] 将 `_get_entropy_four_vec` 重构为 `_get_entropy_multivariate`。此函数需利用 `itertools.combinations` 动态生成所有变量子集的索引，以计算所有必要的联合熵。
  - [ ] 将 `_get_coinfo_four_vec` 重构为 `_get_coinfo_multivariate`，以处理泛化的联合信息计算。
  - [ ] 将 `_get_redundancy_four_vec` 和 `_get_double_redundancy_four_vec` 合并并重构为 `_get_redundancy_multivariate`，以适应 n*m 系统的冗余计算。
  - [ ] 将 `_get_atoms_four_vec` 重构为 `_get_atoms_multivariate`，实现动态构建 `knowns_to_atoms_mat` 矩阵的逻辑，从而能够求解任意 n*m 系统的分解原子。

- [ ] **测试扩展**
  - [ ] 在 `omegaid/tests/test_numerical_integrity.py` 中增加新的测试用例，用于验证 2x1, 1x2, 2x2 等非 1x1 系统的分解结果的正确性。
  - [ ] 在 `omegaid/tests/benchmark.py` 中扩展基准测试，以评估不同 n 和 m 组合下，CPU 和 GPU 后端的性能表现。

- [ ] **API 调整**
  - [ ] 更新 `omegaid/core/__init__.py` 以导出适配 n*m 分解的新函数或修改后的函数。

## 阶段三：文档与收尾

- [ ] 更新项目根目录的 `README.md`，提供清晰的安装指南、使用示例，并说明如何通过环境变量选择计算后端以及如何执行 n*m 分解。
- [ ] 撰写一份总结报告，展示重构后的性能测试结果（特别是 CuPy 后端的加速效果），并总结关键的优化经验。
