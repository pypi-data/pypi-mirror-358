# OmegaID 开发计划

## 1. 核心目标

我们的核心目标是利用 GPU 加速（主要是 CuPy），重构 `phyid` 包，以实现对整合信息分解（ΦID）的高性能计算。

## 2. 项目结构

所有新的开发工作都应在 `omegaid` 目录下进行，并遵循以下结构：

```plain
omegaid/
├── core/         # 核心计算逻辑 (原 measures.py, calculate.py)
├── utils/        # 数据处理、兼容性层等辅助函数
└── tests/        # 测试脚本 (例如，性能基准测试)
```

## 3. 工程准则

- **环境管理**: **必须**使用 `uv` 管理独立的虚拟环境。所有新的依赖项都必须通过 `uv add <package_name>` 添加到根目录的 `pyproject.toml` 中。
- **后端兼容性**: 代码必须设计为可在 CPU (NumPy) 和 GPU (CuPy) 之间切换。在 `omegaid/utils/backend.py` 中实现一个兼容性层，动态导入 NumPy 或 CuPy 作为 `xp`。
- **纯函数原则**: 所有数据处理和计算函数应尽可能设计为纯函数，以提高代码的可测试性和可复现性。
- **无注释策略**: 代码必须自解释。在修改或重构时，请移除所有既有的注释和文档字符串。

## 4. GPU 重构指南

1. **兼容性层 (`omegaid/utils/backend.py`)**:
    - 创建一个函数，根据环境变量或配置动态导入 `numpy` 或 `cupy` 并将其赋值给 `xp`。
    - 所有数值计算代码必须使用 `xp`，严禁直接调用 `np` 或 `cp`。
2. **核心函数重构 (`omegaid/core/`)**:
    - 将 `phyid` 中的 `measures.py` 和 `calculate.py` 的逻辑迁移到 `omegaid/core/` 下的新模块中。
    - 识别并向量化所有可以并行处理的循环。
    - **关键优化点**:
        - `_get_entropy_four_vec` 中的 `np.cov` -> `xp.cov`。
        - `local_entropy_mvn` 中的 `sstats.multivariate_normal.pdf`：必须使用 `xp` 的函数（`xp.linalg.det`, `xp.linalg.inv`, 矩阵乘法）在 GPU 上重新实现。
        - `_get_atoms_four_vec` 中的 `np.linalg.solve` -> `xp.linalg.solve`，利用其批处理能力。
3. **数据流**:
    - 数据应在计算开始时一次性转移到 GPU，并在所有计算完成后才传回 CPU，以最小化传输开销。

## 5. 工作流

- **核心循环**: `读取文件 -> 分析需求 -> 编辑/生成代码 -> 定期进行 mypy 检查`。
- **状态追踪**: 每完成一个重要功能模块（例如，`backend.py` 的实现），就在 `.clinerules/process.md` 中更新待办事项清单和关键经验总结。
