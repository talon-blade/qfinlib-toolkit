# qfinlib Toolkit

A pip-installable set of qfinlib-backed Dash dashboards for market monitoring, pricing, and strategy experimentation.

## Install

```bash
pip install qfinlib-toolkit
```

## Launch dashboards from CLI

After install, each dashboard can be started directly as a command:

```bash
qfinlib-toolkit.portal
qfinlib-toolkit.market-monitor
qfinlib-toolkit.market-monitor.swap-rate-monitor
qfinlib-toolkit.trade-pricing
qfinlib-toolkit.strategy-lab
```

### Swap Rate Monitor (new)

`qfinlib-toolkit.market-monitor.swap-rate-monitor` launches a dedicated swap-curve dashboard (default port `8061`).

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip build
pip install -e .
python -m build
```

## CI/CD release publishing

GitHub Actions is configured so that every pushed tag matching `v*` builds the package and publishes it to PyPI (using `PYPI_API_TOKEN` repository secret).

Example:

```bash
git tag v0.1.0
git push origin v0.1.0
```
