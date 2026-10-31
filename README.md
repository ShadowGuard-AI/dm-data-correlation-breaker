![Banner](banner.png)

# dm-data-correlation-breaker
Identifies and removes subtle correlations between seemingly unrelated data points that could lead to re-identification of masked data. It focuses on finding and breaking these hidden links, for example, by injecting carefully chosen errors or variations. - Focused on Tools designed to generate or mask sensitive data with realistic-looking but meaningless values

## Install
`git clone https://github.com/ShadowGuardAI/dm-data-correlation-breaker`

## Usage
`./dm-data-correlation-breaker [params]`

## Parameters
- `-h`: Show help message and exit
- `--input`: Path to the input CSV file.
- `--columns`: Comma-separated list of column names to process.
- `--error-rate`: Probability (0-1) of introducing an error in a data point. Default: 0.01
- `--output`: Path to the output CSV file. Default: output.csv
- `--seed`: Seed for the random number generator to ensure reproducibility.

## Behavior notes
- The output file may not be the input file. If the resolved output path is the input file, by the same spelling, a `./` alias, or a symlink, the run refuses at exit 1 before anything is written and the input is left untouched.
- Values keep their type. A value in a numeric column gets small numeric noise added and stays a number in the output. A value in a text column is replaced with a fake word.
- The same seed and the same input produce byte-identical output.

## License
Copyright (c) ShadowGuardAI
