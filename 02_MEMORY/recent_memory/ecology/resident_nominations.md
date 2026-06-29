# resident_nominations

- window_days: 30
- generated_at: 2026-06-25T15:54:41.770462

## 候选清单

### 未知工作流：01_AGENTS (`unknown_01_agents`)
- status: `NOT_YET`
- occurrences_30d: `68`
- ecological_need: `false`
- replaceable_by_existing_roles: `false`
- stable_input: repo activity
- evidence:
  - 01_AGENTS (changes=68)

### 未知工作流：02_MEMORY (`unknown_02_memory`)
- status: `NOT_YET`
- occurrences_30d: `53`
- ecological_need: `false`
- replaceable_by_existing_roles: `false`
- stable_input: repo activity
- evidence:
  - 02_MEMORY (changes=53)

### 约束工程 (`constraint_engineering`)
- status: `NOT_YET`
- occurrences_30d: `17`
- ecological_need: `true`
- replaceable_by_existing_roles: `true`
- covered_by_existing_roles: 档案官, 馆长, 守夜人
- stable_input: constraint proposals + incidents
- stable_output_paths: 03_DATA/CONSTRAINTS
- memory_deposit_paths: 03_DATA/research/constraint_proposal
- evidence:
  - 03_DATA/CONSTRAINTS (changes=4)
  - 05_TOOLS/constraints (changes=4)

### 未知工作流：03_DATA/research (`unknown_03_data_research`)
- status: `NOT_YET`
- occurrences_30d: `16`
- ecological_need: `false`
- replaceable_by_existing_roles: `false`
- stable_input: repo activity
- evidence:
  - 03_DATA/research (changes=16)

### 未知工作流：docs/V6_RFC (`unknown_docs_v6_rfc`)
- status: `NOT_YET`
- occurrences_30d: `8`
- ecological_need: `false`
- replaceable_by_existing_roles: `false`
- stable_input: repo activity
- evidence:
  - docs/V6_RFC (changes=8)
