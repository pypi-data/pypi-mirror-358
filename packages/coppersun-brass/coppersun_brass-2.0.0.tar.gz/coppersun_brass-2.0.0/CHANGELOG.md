# Changelog

All notable changes to Copper Alloy Brass will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-18

### Changed
- 🚀 **Major Rebrand**: DevMind is now Copper Alloy Brass
- Package renamed from `devmind` to `coppersun_brass`
- CLI command changed from `devmind` to `brass`
- Context directory renamed from `.devmind/` to `.brass/`
- License format updated from `DEVMIND-XXXX` to `BRASS-XXXX`
- Environment variables renamed from `DEVMIND_*` to `BRASS_*`

### Added
- Comprehensive migration tool (`brass-migrate`)
- Backward compatibility for old licenses
- Detailed developer environment guide
- Professional documentation structure
- Docker and Kubernetes deployment support
- Enhanced error messages and logging

### Improved
- Reorganized code into standard Python package structure
- Cleaned up development artifacts
- Enhanced documentation with clear user/developer separation
- Better test organization and coverage
- Streamlined installation process

### Compatibility
- ✅ Old license keys automatically converted
- ✅ Environment variables support fallback
- ✅ Configuration files auto-migrate
- ⚠️ Python imports must be updated

### Migration
See [Migration Guide](docs/migration-from-devmind.md) for upgrade instructions.

---

## [1.0.0] - 2025-06-16 (Final DevMind Release)

### Added
- Four specialized agents (Watch, Scout, Strategist, Planner)
- Development Context Protocol (DCP)
- ML-powered code analysis
- Real-time project monitoring
- Strategic planning capabilities
- Claude API integration

### Notes
This was the final release under the DevMind brand.