# BasketballScraper 2024

## Usage

From there, you can set up the Conda environment:
```shell
conda env create -f environment.yml
conda activate BasketballScraper2024
```
Create output folder
```shell
mkdir csvs
```

## Retrieve PBP 2024

Before running the Jupyter Notebook, it's important to retrieve the auth bearer token from the legabasket.com website.

The notebook contains two ways to retrieve the pbp for the season 2023/2024:
* one complete PBP without two faulty games
* one PBP with all the games without substitution information

