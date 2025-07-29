import duckdb
import os
import ast
import pandas as pd
from importlib.resources import files

class nct:
    DB_PATH = str(files("PCPy.data").joinpath("pcpy.duckdb"))

    def __init__(self, nctid):
        self.nctid = nctid.strip().upper()
        self.conn = duckdb.connect(self.DB_PATH)
        self.nct_df = self.conn.execute("SELECT * FROM nct").fetchdf()
        self.pc_df = self.conn.execute("SELECT * FROM pmc").fetchdf()

        self.nct_row = self.nct_df[self.nct_df["nctid"].str.upper() == self.nctid]
        if self.nct_row.empty:
            raise ValueError(f"No entry found for {self.nctid}")

        self.related_preclinical = self.pc_df[
            self.pc_df["matched_clinical_studies"].apply(self._contains_nctid)
        ]
        self._preclinical_df = self._build_preclinical_df()

    def _contains_nctid(self, val):
        try:
            studies = ast.literal_eval(str(val))
            return self.nctid in studies
        except:
            return False

    def _build_preclinical_df(self):
        rows = []
        seen = set()

        for _, row in self.related_preclinical.iterrows():
            pmcid = row.get("pmcid")
            mesh_term = row.get("mesh_term", "N/A")
            mesh_id = row.get("mesh_id", "N/A")
            pmc_title = row.get("pmc_title", "N/A")
            pmc_link = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/"
            drug = row.get("drug_name", "N/A")
            key = (pmcid, mesh_term, mesh_id)

            if key in seen:
                continue
            seen.add(key)

            try:
                all_nctids = ast.literal_eval(str(row.get("matched_clinical_studies", "[]")))
                if not isinstance(all_nctids, list):
                    all_nctids = []
            except:
                all_nctids = []

            other_nctids = [n for n in all_nctids if n != self.nctid]
            other_nctids_str = ";".join(sorted(other_nctids)) if other_nctids else "N/A"

            rows.append({
                "pmcid": pmcid,
                "pmc_title": pmc_title,
                "pmc_link": pmc_link,
                "drug_name": drug,
                "mesh_term": mesh_term,
                "mesh_id": mesh_id,
                "matched_clinical_studies": other_nctids_str
            })

        return pd.DataFrame(rows, columns=[
            "pmcid", "pmc_title", "pmc_link", "drug_name",
            "mesh_term", "mesh_id", "matched_clinical_studies"
        ])

    def summary(self, key=None):
        title = self.nct_row["nct_title"].iloc[0] if "nct_title" in self.nct_row else "N/A"
        link = self.nct_row["nct_link"].iloc[0] if "nct_link" in self.nct_row else f"https://clinicaltrials.gov/study/{self.nctid}"
        info = {
            "nctid": self.nctid,
            "title": title,
            "link": link
        }
        return info if key is None else info.get(key, None)

    def export(self, fields):
        output = []

        if "nct.title" in fields:
            output.append(self.title)
        if "nct.link" in fields:
            output.append(self.link)
        if "nct.preclinical" in fields:
            self._export_preclinical()

        return "\n".join(output)

    def _export_preclinical(self):
        if not self._preclinical_df.empty:
            os.makedirs("extract/nctid", exist_ok=True)
            path = f"extract/nctid/{self.nctid}_preclinical.tsv"
            self._preclinical_df.to_csv(path, sep="\t", index=False)

    @property
    def title(self):
        return self.summary("title")

    @property
    def link(self):
        return self.summary("link")

    @property
    def preclinical(self):
        return self._preclinical_df

    @property
    def preclinical_count(self):
        return len(self._preclinical_df)