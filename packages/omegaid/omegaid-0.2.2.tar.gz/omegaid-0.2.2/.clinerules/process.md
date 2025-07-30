### 旧目标（已证明不可行）

- [ ] 理论突破：找到通用的 `n*m` 分解理论。

### 新目标（可行且清晰的工程路径）

- [x] **理论选定：** 确定**双格理论 (Doublet Lattice)** 作为 `n>2` 或 `m>2` 时的核心近似框架。
- [ ] **新模块 `omegaid/core/doublet_lattice.py`：**
  - [ ] 实现 `generate_doublet_atoms(n, m)`: 根据输入的维度，自动生成所有成对原子的列表。
  - [ ] 实现 `generate_doublet_mi_tasks(n, m)`: 生成所有需要计算的互信息组合。
  - [ ] 实现 `build_doublet_matrix(n, m)`: **核心！** 程序化地构建`n*m`双格分解的系数矩阵`A`。
- [ ] **重构核心计算函数 `calc_phiid_multivariate`：**
  - [ ] 添加逻辑：当 `n=2` 且 `m=2` 时，调用现有精确解；否则，调用新的双格分解。
  - [ ] 内部调用`doublet_lattice.py`中的新函数。
  - [ ] 协调整个计算流程：计算MI -> 构建矩阵 -> 求解 -> 返回结果。
- [ ] **扩展测试：**
  - [ ] 新增 `test_2x2_equivalence.py`，确保重构后的函数在 `2x2` 场景下与原始实现结果完全一致。
  - [ ] 新增 `test_4x2_decomposition.py`，确保 `4x2` 分解的正确性和数值稳定性。
  - [ ] 将性能基准测试扩展到 `4x2` 场景，评估其在GPU上的实际表现。
