import itertools
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from rich.console import Console
from scipy.stats import rankdata

from db.models import ANOVARun, ARTRun, Function
from db.utils import init_local_session

LANG_TO_PARADIGM = {
    "c": "imperative",
    "clojure": "functional",
    "elixir": "functional",
    "erlang": "functional",
    "fortran": "imperative",
    "haskell": "functional",
    "java": "imperative",
    "javascript": "imperative",
    "ocaml": "functional",
    "python": "imperative",
}

LANGS = [
    "c",
    "clojure",
    "elixir",
    "erlang",
    "haskell",
    "java",
    "javascript",
    "ocaml",
    "python",
]

METRICS = [
    "median_id_length",
    "median_id_soft_word_count",
    "id_duplicate_percentage",
    "num_single_letter_ids",
    "id_percent_abbreviations",
    "id_percent_dictionary_words",
    "num_conciseness_violations",
    "num_consistency_violations",
    "term_entropy",
    "median_id_lv_dist",
    "median_id_semantic_similarity",
    "median_word_concreteness",
    "context_coverage",
    "grammar_hash",
]

DOMAINS = [
    [
        "ml",
        "infr",
        "db",
        "struct",
        "edu",
        "lang",
        "frontend",
        "backend",
        "build",
        "code",
        "cli",
        "comp",
        "game",
    ],
    ["db", "lang", "game", "comp", "backend", "frontend", "ml"],
]

console = Console()


class Statistics:
    @staticmethod
    def check_distribution():
        session = init_local_session()

        for metric_name in METRICS:
            console.print(f"Checking distribution of {metric_name}", style="blue")
            metric = Function.get_metrics(session, limit=100000, metric=metric_name)
            random.shuffle(metric)
            metric = [value[0] for value in metric[:10000]]

            # Shapiro–Wilk Test
            shapiro_stat, shapiro_p = stats.shapiro(
                metric[:500]
            )  # Shapiro is sensitive to large n, so we take subset
            console.print(
                f"Shapiro–Wilk test statistic = {shapiro_stat:.4f}, p-value = {shapiro_p:.4f}"
            )

            if shapiro_p >= 0.05:
                console.print(f"{metric_name} is normally distributed", style="red")

            # Kolmogorov–Smirnov Test
            # Compare data to a normal distribution with the same mean and std
            mu, sigma = np.mean(metric), np.std(metric)
            ks_stat, ks_p = stats.kstest(metric, "norm", args=(mu, sigma))
            console.print(f"K–S test statistic = {ks_stat:.4f}, p-value = {ks_p:.4f}")

            if ks_p >= 0.05:
                console.print(f"{metric_name} is normally distributed", style="red")

            # Anderson–Darling Test
            ad_results = stats.anderson(metric, dist="norm")
            console.print(f"Anderson–Darling statistic = {ad_results.statistic:.4f}")

            for i, crit in enumerate(ad_results.critical_values):
                sl = ad_results.significance_level[i]
                console.print(
                    f"At {sl}% significance level, critical value is {crit:.4f}."
                )

                if ad_results.statistic < crit:
                    console.print(f"{metric_name} is normally distributed", style="red")

    @staticmethod
    def execute_art():
        session = init_local_session()

        for _ in range(10):
            for per_lang_limit in reversed([6300, 8400, 10600]):
                for metric in METRICS:
                    console.print(
                        f"Performing ART for {metric}, domains: {domains_subset}, with {per_lang_limit} examples per language"
                    )

                    for domains in DOMAINS:
                        metric_values = Function.get_metrics_with_labels(
                            session,
                            langs=LANGS,
                            limit=per_lang_limit,
                            metric=metric,
                            domains=domains,
                        )
                        result = AlignedRankTransform._execute_art(metric_values)

                        run = ARTRun(
                            metric=metric,
                            langs=" ".join(LANGS),
                            domains=" ".join(domains),
                            max_samples=per_lang_limit,
                            lang_fval=result["lang_fval"],
                            lang_p=result["lang_p"],
                            lang_df=result["lang_df"],
                            domain_fval=result["domain_fval"],
                            domain_p=result["domain_p"],
                            domain_df=result["domain_df"],
                            interact_fval=result["interact_fval"],
                            interact_p=result["interact_p"],
                            interact_df=result["interact_df"],
                        )
                        session.add(run)
                        session.commit()

    @staticmethod
    def execute_anova():
        session = init_local_session()

        for _ in range(10):
            for per_lang_limit in reversed([6300, 8400, 10600]):
                for metric in METRICS:
                    for domains in DOMAINS:
                        metric_values = Function.get_metrics_with_labels(
                            session,
                            langs=LANGS,
                            limit=per_lang_limit,
                            metric=metric,
                            domains=domains,
                        )
                        result = AlignedRankTransform._execute_anova(metric_values)

                        run = ANOVARun(
                            metric=metric,
                            langs=" ".join(LANGS),
                            domains=" ".join(domains),
                            typ=3,
                            max_samples=per_lang_limit,
                            lang_fval=result["lang_fval"],
                            lang_p=result["lang_p"],
                            lang_df=result["lang_df"],
                            lang_es=result["lang_es"],
                            domain_fval=result["domain_fval"],
                            domain_p=result["domain_p"],
                            domain_df=result["domain_df"],
                            domain_es=result["domain_es"],
                            interact_fval=result["interact_fval"],
                            interact_p=result["interact_p"],
                            interact_df=result["interact_df"],
                            interact_es=result["interact_es"],
                        )
                        session.add(run)
                        session.commit()

    @staticmethod
    def _execute_anova(metric_values):
        """
        Performs a Type III ANOVA on rank-transformed data with sum (effects) coding.

        metric_values: a list of (value, language, domain) tuples.
        Example: [(3.4, 'Python', 'Web'), (2.1, 'Java', 'ML'), ...]

        Returns:
           A dictionary with an ANOVA table (typ=3) from the
           rank-transformed data, plus partial effect sizes.
        """

        values = [mv[0] for mv in metric_values]
        languages = [mv[1] for mv in metric_values]
        domains = [mv[2] for mv in metric_values]

        df = pd.DataFrame(
            {
                "Language": pd.Categorical(languages),
                "Domain": pd.Categorical(domains),
                "Metric": values,
            }
        )

        # Apply sum coding (effects coding) to categorical variables
        # By default, statsmodels uses treatment coding, so we must manually set sum coding.
        df = df.assign(
            Language=df[
                "Language"
            ].cat.codes,  # Convert categories to numerical representation
            Domain=df["Domain"].cat.codes,
        )

        # Rank the Metric *once* across the entire dataset
        df["Ranked"] = rankdata(df["Metric"])

        # Fit a Type III ANOVA on the ranks with sum coding
        model = smf.ols("Ranked ~ C(Language, Sum)*C(Domain, Sum)", data=df).fit()
        anova_table = sm.stats.anova_lm(model, typ=3)

        # Calculate a partial effect size for each factor
        ss_res = anova_table.loc["Residual", "sum_sq"]

        effect_sizes = {}
        for factor in anova_table.index:  # Dynamically extract correct names
            if factor != "Residual":  # Ignore residual row
                ss_factor = anova_table.loc[factor, "sum_sq"]
                effect_sizes[factor] = ss_factor / (ss_factor + ss_res)

        return {
            "anova_table": anova_table,
            "lang_p": anova_table.loc["C(Language, Sum)", "PR(>F)"],
            "domain_p": anova_table.loc["C(Domain, Sum)", "PR(>F)"],
            "interact_p": anova_table.loc["C(Language, Sum):C(Domain, Sum)", "PR(>F)"],
            "lang_df": anova_table.loc["C(Language, Sum)", "df"],
            "domain_df": anova_table.loc["C(Domain, Sum)", "df"],
            "interact_df": anova_table.loc["C(Language, Sum):C(Domain, Sum)", "df"],
            "lang_fval": anova_table.loc["C(Language, Sum)", "F"],
            "domain_fval": anova_table.loc["C(Domain, Sum)", "F"],
            "interact_fval": anova_table.loc["C(Language, Sum):C(Domain, Sum)", "F"],
            "lang_es": effect_sizes["C(Language, Sum)"],
            "domain_es": effect_sizes["C(Domain, Sum)"],
            "interact_es": effect_sizes["C(Language, Sum):C(Domain, Sum)"],
        }

    @staticmethod
    def _execute_art(metric_values):
        values = [value[0] for value in metric_values]
        languages = [value[1] for value in metric_values]
        domains = [value[2] for value in metric_values]

        df = pd.DataFrame({"Language": languages, "Domain": domains, "Metric": values})

        def fit_and_anova(data, formula, factor_label):
            """
            Fits an OLS model using the given formula and prints an ANOVA table.
            Returns F-value, partial eta squared, and partial omega squared for factor_label.
            """
            model = smf.ols(formula, data=data).fit()
            anova_table = sm.stats.anova_lm(model, typ=2)
            # print(anova_table)

            f_val = anova_table.loc[factor_label, "F"]
            p_val = anova_table.loc[factor_label, "PR(>F)"]
            df_val = anova_table.loc[factor_label, "df"]

            return f_val, p_val, df_val

        # We'll compute the aligned/rank-transformed data for each effect
        # (Language, Domain, and their Interaction). Then we'll run an OLS
        # on the ranked values, capturing F, partial eta^2, partial omega^2.

        # 3a) Main effect of Language
        # Model that includes Domain + interaction, but NO main effect of Language
        model_no_lang = smf.ols(
            "Metric ~ C(Domain) + C(Language):C(Domain)", data=df
        ).fit()
        df["Aligned_Lang"] = df["Metric"] - model_no_lang.fittedvalues
        df["Ranked_Lang"] = rankdata(df["Aligned_Lang"])

        lang_fval, lang_p, lang_df = fit_and_anova(
            df, "Ranked_Lang ~ C(Language)", factor_label="C(Language)"
        )

        # 3b) Main effect of Domain
        # Model that includes Language + interaction, but NO main effect of Domain
        model_no_domain = smf.ols(
            "Metric ~ C(Language) + C(Language):C(Domain)", data=df
        ).fit()
        df["Aligned_Domain"] = df["Metric"] - model_no_domain.fittedvalues
        df["Ranked_Domain"] = rankdata(df["Aligned_Domain"])

        domain_fval, domain_p, domain_df = fit_and_anova(
            df, "Ranked_Domain ~ C(Domain)", factor_label="C(Domain)"
        )

        # 3c) Interaction: Language × Domain
        # Model that includes ONLY the main effects, but NO interaction
        model_no_inter = smf.ols("Metric ~ C(Language) + C(Domain)", data=df).fit()
        df["Aligned_Interaction"] = df["Metric"] - model_no_inter.fittedvalues
        df["Ranked_Interaction"] = rankdata(df["Aligned_Interaction"])

        interact_fval, interact_p, interact_df = fit_and_anova(
            df,
            "Ranked_Interaction ~ C(Language):C(Domain)",
            factor_label="C(Language):C(Domain)",
        )

        return {
            "lang_fval": lang_fval,
            "lang_df": lang_df,
            "lang_p": lang_p,
            "domain_fval": domain_fval,
            "domain_df": domain_df,
            "domain_p": domain_p,
            "interact_fval": interact_fval,
            "interact_df": interact_df,
            "interact_p": interact_p,
        }
