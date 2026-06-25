# models/

每个子目录是一个可并存的 world model（当前解释），包含：

- `manifest.json`：该解释内部采用的模块版本指针（lexicon/constraints/graph/routing/experience）
- `lexicon/` `constraints/` `graph/` `routing/` `experience/`：结构资产版本
- `evidence/`：该解释自身的证据链

注意：
- world model 不是神圣的，只是暂时解释；
- 允许多模型并存、竞争、分叉、推翻；
- Production 不直接读取这里，Production 只读 `../active_manifest.json` 选择哪个 model 生效。

