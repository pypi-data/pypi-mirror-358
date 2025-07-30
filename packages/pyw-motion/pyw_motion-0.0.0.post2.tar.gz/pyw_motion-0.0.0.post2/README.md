# pyw-motion 🏃
[![PyPI](https://img.shields.io/pypi/v/pyw-motion.svg)](https://pypi.org/project/pyw-motion/)
[![CI](https://github.com/pythonWoods/pyw-motion/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-motion/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Motion detection e tracking utilities per il **pythonWoods** ecosystem.  
(algoritmi real-time, OpenCV integration, type-safe APIs).

## Installation (nothing to use yet)

```bash
pip install pyw-motion
```

## Usage

```python
from pyw.motion import MotionDetector, OpticalFlow
detector = MotionDetector()
frames = detector.detect_motion(video_source)
```

Questo installerà automaticamente:
- `pyw-core` (namespace comune)
- `opencv-python` (computer vision base)
- `numpy` (array processing)

### Extras per algoritmi avanzati:

```bash
pip install pyw-motion[advanced]  # + scikit-image, scipy
pip install pyw-motion[gpu]       # + OpenCV GPU acceleration
pip install pyw-motion[full]      # tutto incluso
```

## Philosophy

* **Real-time ready** – algoritmi ottimizzati per streaming video.
* **Multiple backends** – OpenCV, scikit-image, custom implementations.
* **Type-safe APIs** – Pydantic models per bounding boxes, tracks.
* **Lightweight core** – dipendenze pesanti come extras opzionali.

## Roadmap

- 🎯 **Motion detection**: Background subtraction, frame differencing
- 📹 **Object tracking**: Kalman filter, particle filter, deep SORT
- 🌊 **Optical flow**: Lucas-Kanade, Farneback, deep learning methods  
- 📊 **Analytics**: Trajectory analysis, heat maps, statistics
- ⚡ **Performance**: GPU acceleration, multi-threading, async processing

## Contributing

1. Fork il repo: `pyw-motion`.
2. Crea virtual-env via Poetry: `poetry install && poetry shell`.
3. Lancia linter e mypy: `ruff check . && mypy`.
4. Apri la PR: CI esegue lint, type-check, build.

Felice tracking nella foresta di **pythonWoods**! 🌲🏃

## Links utili
Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-motion/latest/

Issue tracker → https://github.com/pythonWoods/pyw-motion/issues

Changelog → https://github.com/pythonWoods/pyw-motion/releases

© pythonWoods — MIT License