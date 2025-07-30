# OmegaID 待办清单

- [x] 项目已从 `phyid` 演化为 `omegaid`，一个经 GPU 加速（CuPy/NumPy 动态后端）重构的高性能 PhiID 计算引擎。核心 `local_entropy_mvn` 已被重写，以确保在奇异矩阵下的数值稳定性。

- [x] 关键架构决策是双轨实现：保留了为 2x2 系统高度优化的 `calc_phiid_ccs`，同时引入了由 `numba` JIT 加速的、可处理任意 n > 2 源的广义多元分解算法 `calc_phiid_multivariate`。

- [x] 所有实现均通过了与原始 `phyid` 的数值一致性验证，并在 CPU 和 GPU 后端上确认了显著的性能提升。

**未来方向**: PyPI 发布。
