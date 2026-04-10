import os
import pandas as pd
from config import Config


def load_candidates(data_dir: str = None) -> pd.DataFrame:
    path = os.path.join(data_dir or Config.DATA_DIR, "p1_dental_provider_candidates.xlsx")
    return pd.read_excel(path)


def load_alumni_networks(data_dir: str = None) -> pd.DataFrame:
    path = os.path.join(data_dir or Config.DATA_DIR, "p1_dental_alumni_networks.xlsx")
    return pd.read_excel(path)


def load_tax_rates(data_dir: str = None) -> pd.DataFrame:
    path = os.path.join(data_dir or Config.DATA_DIR, "p1_dental_tax_rates.xlsx")
    return pd.read_excel(path)


def load_outreach_hooks(data_dir: str = None) -> str:
    path = os.path.join(data_dir or Config.DATA_DIR, "outreach_hooks.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
