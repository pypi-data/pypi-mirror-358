# Nyan Pytest 🐱‍🚀

A delightful nyan-cat inspired pytest plugin that displays test results with a colorful nyan cat animation and rainbow trail.

```
========================================================================≈≈≈≈≈≈╭━━━━━━━━━━━━╮
======================================================================≈≈≈≈≈╭┫ ♥ * ♥ * ♥ *┃ ╮ ╮
====================================================================≈≈≈≈≈┃┃* ♥ * ♥ * ♥ ┃(^ᴥ^)
====================================================================≈≈≈≈≈-┫ ♥ * ♥ * ♥ *┣╯
======================================================================≈≈≈≈≈≈╰━━━━━━━━━━━━╯
========================================================================≈≈≈≈≈≈  ╰┛ ╰┛ ╰┛ ╰┛

Tests: 42/50 ✅ 38 ❌ 3 ⏭️ 1
```

*Nyan cat flying through your test results with a beautiful rainbow trail!*

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🌈 **Animated rainbow trail** that grows with test progress
- 🐱 **Adorable nyan cat** with paw animations
- 📊 **Real-time test statistics** (passed, failed, skipped)
- 🎨 **Full color support** with ANSI escape codes
- 🖥️ **Terminal compatibility** for both interactive and non-interactive environments
- ⚡ **Performance optimized** for smooth animations

## 🚀 Installation

```bash
pip install nyan-pytest
```

For development:

```bash
git clone https://github.com/your-repo/nyan-pytest
cd nyan-pytest
make setup
```

## 🎮 Usage

### Basic Usage

Run pytest with nyan cat alongside standard output:

```bash
pytest --nyan
```

Use only nyan cat (cleaner output):

```bash
pytest --nyan-only
```

### Demo Mode

Want to see nyan cat in action? Try the simulation mode:

```bash
# Quick demo with 20 simulated tests
pytest --nyan-sim 20

# Epic demo with 100 tests
pytest --nyan-sim 100

# Fast animation demo
pytest --nyan-sim 30 --nyan-speed 2

# Moderate speed
pytest --nyan-sim 30 --nyan-speed 15

# Slow, relaxing animation
pytest --nyan-sim 30 --nyan-speed 50
```

### Makefile Commands

This project includes a comprehensive Makefile for development:

```bash
# Show all available commands
make help

# Run tests with nyan cat
make test-nyan

# Quick demo
make demo

# Epic party mode! 🎉
make party

# Performance benchmarking
make benchmark

# Development setup
make setup
```

## 🎯 Command Line Options

| Option            | Description                                              |
| ----------------- | -------------------------------------------------------- |
| `--nyan`          | Enable nyan cat reporter alongside default pytest output |
| `--nyan-only`     | Use only nyan cat reporter (no standard pytest output)   |
| `--nyan-sim N`    | Simulate N tests to demo the animation                   |
| `--nyan-speed N`  | Animation speed (1=fastest, 6=default, 100=slowest)     |

### 🎛️ Speed Guide

| Speed Range | Best For | Description |
|-------------|----------|-------------|
| 1-3 | Fast unit tests | Quick visual feedback, minimal distraction |
| 4-8 | Regular development | Good balance of visibility and speed (default: 6) |
| 10-25 | Watching tests run | Comfortable viewing during test execution |
| 30-60 | Relaxed development | Slow, enjoyable animation for longer test suites |
| 70-100 | Demos & presentations | Very slow, perfect for showing off to colleagues! |

## 🎨 What You'll See

When running tests, you'll see:

```
≈≈≈≈≈≈╭━━━━━━━━━━━━╮
≈≈≈≈≈╭┫ ♥ * ♥ * ♥ *┃ ╮ ╮
≈≈≈≈≈┃┃* ♥ * ♥ * ♥ ┃(^ᴥ^)
≈≈≈≈≈-┫ ♥ * ♥ * ♥ *┣╯
≈≈≈≈≈≈╰━━━━━━━━━━━━╯
≈≈≈≈≈≈  ╰┛ ╰┛ ╰┛ ╰┛

Tests: 15/20 ✅ 12 ❌ 2 ⏭️ 1
```

- 🌈 **Rainbow trail** (`≈` characters) grows as tests complete
- 🎭 **Animated cat body** with hearts (♥) and stars (\*)
- 🐾 **Moving paws** that animate during test execution
- 📈 **Live statistics** showing progress and results

## 🛠️ Development

### Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd nyan-pytest
make setup

# Run tests
make test-nyan

# Check code quality
make lint

# Try the demo
make demo
```

### Available Make Commands

| Command            | Description                  |
| ------------------ | ---------------------------- |
| `make setup`       | Install dev dependencies     |
| `make test-nyan`   | Run tests with nyan output   |
| `make demo`        | Demo with 20 simulated tests |
| `make performance` | Run performance benchmarks   |
| `make lint`        | Check code quality           |
| `make format`      | Format code                  |
| `make build`       | Build package                |
| `make clean`       | Clean build artifacts        |

## 🎪 Examples

### Running Your Test Suite

```bash
# Standard pytest with nyan enhancement
pytest tests/ --nyan -v

# Clean nyan-only output
pytest tests/ --nyan-only

# Verbose mode with test details
pytest tests/ --nyan -v -s
```

### Performance Testing

```bash
# Benchmark nyan vs standard reporter
make benchmark

# Time the plugin performance
make performance
```

### Demo Modes

```bash
# Quick 10-test demo
make demo-fast

# Standard 20-test demo
make demo

# Longer 50-test demo
make demo-slow

# Epic 100-test party! 🎉
make party
```

## ⚡ Performance Impact

**TL;DR: The delight factor far outweighs the modest performance cost!**

Nyan cat adds visual joy to your testing workflow with minimal impact on development productivity. Benchmarks show the animation overhead is essentially **constant (~2.3 seconds)** regardless of test count:

### Benchmark Results

| Test Count | Standard | Nyan Cat | Overhead | % Slower |
|------------|----------|----------|----------|----------|
| 10 tests   | 0.18s    | 2.41s    | +2.23s   | +1225%   |
| 100 tests  | 1.26s    | 3.52s    | +2.27s   | +181%    |
| 1000 tests | 11.97s   | 14.31s   | +2.33s   | +20%     |

### Key Insights

🎯 **Animation overhead is constant** - The ~2.3 second cost doesn't scale with test count  
📈 **Scales beautifully** - Larger test suites see proportionally less impact  
⚡ **Negligible in practice** - 2-3 seconds is nothing compared to typical development workflows

### When to Use Nyan Cat

✅ **Perfect for:**
- **Development workflows** - Makes test-watching enjoyable
- **Medium to large test suites** - 20-180% overhead on 100-1000 tests
- **CI/CD pipelines** - Minimal time vs overall build/deploy phases  
- **Demo environments** - Delights stakeholders and team members
- **Any project where developer happiness matters**

✅ **Why the overhead is worth it:**
- **Developer motivation** - Transforms boring test runs into engaging experiences
- **Visual progress feedback** - Clear, delightful indication of test execution
- **Team morale boost** - Brings smiles to code reviews, standups, and demos
- **Context matters** - 2.3s is negligible compared to compile times, network calls, or CI overhead

### Benchmark It Yourself

```bash
# Run the performance comparison tool
make performance TESTS=100

# Test different scales
make performance TESTS=10    # Small suite
make performance TESTS=1000  # Large suite

# Compare with your actual test suite
time pytest your_tests/ --nyan-only
time pytest your_tests/ -q  # Standard output
```

**Bottom line:** Unless you're running thousands of ultra-fast unit tests in tight development loops, nyan cat's constant ~2.3s overhead becomes increasingly negligible as your test suite grows. The joy, motivation, and visual feedback it provides make it a net positive for virtually any development workflow. **Adoption is strongly encouraged!** 🎉

## 🔧 Requirements

- Python 3.8+
- pytest 6.0.0+
- Terminal with ANSI color support (most modern terminals)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the full test suite: `make full-check`
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🎉 Credits

Inspired by the original Nyan Cat. This one's for the ktties.
