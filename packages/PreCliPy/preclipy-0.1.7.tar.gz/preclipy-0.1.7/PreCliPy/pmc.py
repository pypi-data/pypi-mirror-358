import duckdb
import os
import ast
import pandas as pd
from importlib.resources import files, as_file

class pmc:
    def __init__(self, pmcid):
        self.pmcid = pmcid.strip().upper()
        self._db_context = None
        self.conn = self._connect_to_db()

        self.df = self.conn.execute("SELECT * FROM pmc").fetchdf()
        self.df["pmcid"] = self.df["pmcid"].astype(str).str.upper()

        self.matches = self.df[self.df["pmcid"] == self.pmcid]
        if self.matches.empty:
            raise ValueError(f"No entry found for {self.pmcid}")

        self._diseases_df = self._build_disease_df()
        self._clinical_df = self._build_clinical_df()

    def _connect_to_db(self):
        db_file = files("PreCliPy.data").joinpath("pcpy.duckdb")
        self._db_context = as_file(db_file)
        db_path = self._db_context.__enter__()  # Keep the resource alive
        return duckdb.connect(str(db_path))

    def close(self):
        """Clean up file context and DB connection"""
        if self._db_context:
            self._db_context.__exit__(None, None, None)
            self._db_context = None
        if hasattr(self, "conn"):
            self.conn.close()

    def summary(self, key=None):
        title = self.matches["pmc_title"].iloc[0] if "pmc_title" in self.matches else "N/A"
        link = self.matches["pmc_link"].iloc[0] if "pmc_link" in self.matches else f"https://www.ncbi.nlm.nih.gov/pmc/articles/{self.pmcid}/"
        data = {
            "pmcid": self.pmcid,
            "title": title,
            "link": link
        }
        return data if key is None else data.get(key, None)

    def export(self, fields):
        output = []

        if "pmc.title" in fields:
            output.append(self.title)
        if "pmc.link" in fields:
            output.append(self.link)
        if "pmc.disease" in fields:
            self._export_diseases()
        if "pmc.clinical" in fields:
            self._export_clinical()

        return "\n".join(output)

    def _build_disease_df(self):
        seen = set()
        diseases = []

        for _, row in self.matches.iterrows():
            mesh_term = str(row.get("mesh_term", "N/A"))
            mesh_id = str(row.get("mesh_id", "N/A"))
            if (mesh_term, mesh_id) not in seen:
                diseases.append((mesh_term, mesh_id))
                seen.add((mesh_term, mesh_id))

        return pd.DataFrame(diseases, columns=["mesh_term", "mesh_id"])

    def _export_diseases(self):
        if not self._diseases_df.empty:
            os.makedirs("extract/pmcid", exist_ok=True)
            self._diseases_df.to_csv(f"extract/pmcid/{self.pmcid}_diseases.tsv", sep="\t", index=False)

    def _build_clinical_df(self):
        rows = []

        for drug in self.matches["drug_name"].dropna().unique():
            drug_rows = self.matches[self.matches["drug_name"] == drug]
            clinical_count = drug_rows["clinical_count"].iloc[0] if "clinical_count" in drug_rows else "N/A"

            studies = drug_rows["matched_clinical_studies"].dropna().tolist()
            nct_ids = set()
            for study_list in studies:
                try:
                    parsed = ast.literal_eval(study_list)
                    if isinstance(parsed, list):
                        nct_ids.update(parsed)
                except Exception:
                    continue

            matched_studies = sorted(nct_ids) if nct_ids else ["N/A"]
            rows.append({
                "drug_name": drug,
                "clinical_count": clinical_count,
                "matched_clinical_studies": ";".join(matched_studies)
            })

        return pd.DataFrame(rows, columns=["drug_name", "clinical_count", "matched_clinical_studies"])

    def _export_clinical(self):
        if not self._clinical_df.empty:
            os.makedirs("extract/pmcid", exist_ok=True)
            self._clinical_df.to_csv(f"extract/pmcid/{self.pmcid}_clinical.tsv", sep="\t", index=False)

    @property
    def title(self):
        return self.summary("title")

    @property
    def link(self):
        return self.summary("link")

    @property
    def diseases(self):
        return self._diseases_df

    @property
    def disease_count(self):
        return len(self._diseases_df)

    @property
    def clinical(self):
        return self._clinical_df

    @property
    def clinical_count(self):
        return len(self._clinical_df)

    def __del__(self):
        self.close()