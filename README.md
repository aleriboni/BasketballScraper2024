# BasketballScraper 2024

## Usage

You can set up the Conda environment:
```shell
conda create -n BasketballScraper2024 --file requirements.txt
conda activate BasketballScraper2024
```
Create output folder
```shell
mkdir csvs
```

If new depenendecies are added, use this command to update requirements.txt
```shell
conda list -e > requirements.txt
```

## Retrieve PBP 2024

The notebook contains two ways to retrieve the pbp for the season 2023/2024:
* one complete PBP without two faulty games
* one PBP with all the games without substitution information

