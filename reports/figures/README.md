# Figures

The five figures in this folder were generated from my deterministic SYNTHETIC sample, `data/sample/synthetic_eurofxref_sample.csv`, with:

```bash
python src/visualize.py --csv data/sample/synthetic_eurofxref_sample.csv
```

They are not ECB data and show nothing about real exchange rates; they demonstrate the chart types offline. Real-data figures regenerate after `python src/download_data.py --refresh` followed by `python src/visualize.py`. Markers that need real data (for example the 2022 parity crossing) only appear when the plotted series supports them.
