import duckdb
import os
import ast
import pandas as pd
from importlib.resources import files, as_file

class link:
    def __init__(self, query):
        self.query = query.strip().upper()
        self._db_context = None
        self.conn = self._connect_to_db()
        self.pc_df = self.conn.execute("SELECT * FROM pmc").fetchdf()
        self.nct_df = self.conn.execute("SELECT * FROM nct").fetchdf()
        self.links = self._link_pairs()

    def _connect_to_db(self):
        db_file = files("PreCliPy.data").joinpath("pcpy.duckdb")
        self._db_context = as_file(db_file)
        db_path = self._db_context.__enter__()  # Keep the file handle alive
        return duckdb.connect(str(db_path))

    def close(self):
        """Clean up file context and DB connection"""
        if self._db_context:
            self._db_context.__exit__(None, None, None)
            self._db_context = None
        if hasattr(self, "conn"):
            self.conn.close()

    def _parse_terms(self, x):
        try:
            return [str(t).upper() for t in ast.literal_eval(str(x))]
        except:
            return []

    def _link_pairs(self):
        for col in ["mesh_id", "mesh_term", "drug_name"]:
            self.pc_df[col] = self.pc_df[col].astype(str).str.upper()

        self.pc_df["entry_terms"] = self.pc_df["entry_terms"].astype(str).apply(self._parse_terms)
        self.pc_df["pmcid"] = self.pc_df["pmcid"].astype(str).str.upper()
        self.pc_df["pmc_title"] = self.pc_df.get("pmc_title", "")

        self.nct_df["nctid"] = self.nct_df["nctid"].astype(str).str.upper()
        nct_title_map = dict(zip(self.nct_df["nctid"], self.nct_df["nct_title"]))

        matches = self.pc_df[
            (self.pc_df["mesh_id"] == self.query) |
            (self.pc_df["mesh_term"] == self.query) |
            (self.pc_df["drug_name"] == self.query) |
            (self.pc_df["entry_terms"].apply(lambda terms: self.query in terms))
        ]

        seen = set()
        rows = []

        for _, row in matches.iterrows():
            pmcid = row["pmcid"]
            pmc_title = row.get("pmc_title", "")

            try:
                raw = row.get("matched_clinical_studies", "[]")
                nctids = ast.literal_eval(str(raw))
                if not isinstance(nctids, list):
                    nctids = []
            except:
                nctids = []

            for nctid in nctids:
                pair = (pmcid, nctid)
                if pair in seen:
                    continue
                seen.add(pair)
                rows.append({
                    "pmcid": pmcid,
                    "pmc_title": pmc_title,
                    "pmc_link": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/",
                    "nctid": nctid,
                    "nct_title": nct_title_map.get(nctid, ""),
                    "nct_link": f"https://clinicaltrials.gov/study/{nctid}"
                })

        return rows

    def summary(self):
        return self.links

    def export(self, fields=None):
        if not self.links:
            return ""

        df = pd.DataFrame(self.links)
        os.makedirs("extract/link", exist_ok=True)
        out_path = os.path.join("extract/link", f"{self.query.lower()}_links.tsv")
        df.to_csv(out_path, sep="\t", index=False)

        if fields:
            selected = []
            for row in self.links:
                selected.append([str(row.get(field, "")) for field in fields])
            return "\n".join(["\t".join(line) for line in selected])
        return f"Exported {len(df)} links to {out_path}"

    @property
    def link_count(self):
        return len(self.links)

    @property
    def has_links(self):
        return self.link_count > 0

    @property
    def link(self):
        return pd.DataFrame(self.links) if self.links else pd.DataFrame(columns=[
            "pmcid", "pmc_title", "pmc_link", "nctid", "nct_title", "nct_link"
        ])

    def __del__(self):
        self.close()