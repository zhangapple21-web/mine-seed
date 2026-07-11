# Exploration Report: Capability Graph / Skill Registry

**Date**: 2026-07-11

**Topic ID**: T-007

**Why for ACE**: ACE 的 Capability Graph 是核心抽象，可以借鉴插件系统的设计

## Findings

这5个项目都围绕技能/插件注册与分发实现，提供了搜索、分类、版本控制、审计、RBAC 等功能。VoltAgent 的集合侧重海量公开技能，Clawhub 与 tech-leads-club 提供 TypeScript 实现的可插拔注册框架，iflytek 引入企业级治理，Observal 则关注本地分析与可视化。整体来看，它们展示了从轻量化目录到企业级治理的完整生态，可为 ACE 的 Capability Graph 在插件化、治理、可观测性方面提供参考。

## Question for ACE

> 是否应该在 ACE 的 Capability Graph 中加入安全的技能注册、版本化和 RBAC 审计机制？

## Recommendation

**ABSORB** — 该项目直接面向 AI 代理的安全、可验证技能注册，提供成熟的 TypeScript 实现和治理模型，最贴合 ACE 将 Capability Graph 作为插件系统核心的需求，值得纳入研究。

## Projects Found

| Project | Stars | Language | Updated | Description |
|---|---|---|---|---|
| [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) | 51113 | None | 2026-07-11 | The awesome collection of OpenClaw skills. 5,400+ skills filtered and categorize |
| [openclaw/clawhub](https://github.com/openclaw/clawhub) | 9130 | TypeScript | 2026-07-11 | Skill + Plugin Registry for OpenClaw |
| [tech-leads-club/agent-skills](https://github.com/tech-leads-club/agent-skills) | 4857 | TypeScript | 2026-07-10 | The secure, validated skill registry for professional AI coding agents. Extend A |
| [iflytek/skillhub](https://github.com/iflytek/skillhub) | 3970 | Java | 2026-07-11 | Self-hosted, open-source agent skill registry for enterprises. Publish & version |
| [Observal/Observal](https://github.com/Observal/Observal) | 2190 | Python | 2026-07-11 | Observal is a local registry and analytics platform for your AI components.  Set |
