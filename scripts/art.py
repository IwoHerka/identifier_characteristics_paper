import random
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy.stats import rankdata, chi2
from itertools import combinations
from scipy.stats import rankdata
from multiprocessing import Process
from db.models import Function, ARTRun
from db.utils import init_local_session

METRICS = [
  "median_id_length", 
  "median_id_semantic_similarity", 
  "median_id_soft_word_count",
  "id_duplicate_percentage",
  "num_single_letter_ids",
  "id_percent_abbreviations",
  "id_percent_dictionary_words",
  "num_conciseness_violations",
  "num_consistency_violations",
  "term_entropy",
  "median_id_lv_dist",
  "context_coverage",
  "median_id_semantic_similarity",
  # TODO: grammar
]
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

NUM_PROCESSES = 4


class AlignedRankTransform:
  @staticmethod
  def show_diagram(metric):
      plt.figure(figsize=(12,5))

      plt.subplot(1,2,1)
      plt.hist(metric, bins=30, color='lightblue', edgecolor='black')
      plt.title(f"Histogram of {metric_name}")

      plt.subplot(1,2,2)
      stats.probplot(metric, dist="norm", plot=plt)
      plt.title("Q-Q Plot")

      plt.tight_layout()
      plt.show()

  @staticmethod
  def check_if_parametric():
    session = init_local_session()

    for metric_name in METRICS:
      metric = Function.get_metrics(session, limit=100000, metric=metric_name)
      random.shuffle(metric)
      metric = [value[0] for value in metric[:1000]]

      # --- 1) Shapiro–Wilk Test ---
      shapiro_stat, shapiro_p = stats.shapiro(metric[:500])  # Shapiro is sensitive to large n, so we take subset
      print(f"Shapiro–Wilk test statistic = {shapiro_stat:.4f}, p-value = {shapiro_p:.4f}")

      if shapiro_p >= 0.05:
        print(f"{metric_name} is normally distributed")
        break

      # --- 2) Kolmogorov–Smirnov Test ---
      # Compare data to a normal distribution with the same mean and std
      mu, sigma = np.mean(metric), np.std(metric)
      ks_stat, ks_p = stats.kstest(metric, 'norm', args=(mu, sigma))
      print(f"K–S test statistic = {ks_stat:.4f}, p-value = {ks_p:.4f}")

      if ks_p >= 0.05:
        print(f"{metric_name} is normally distributed")
        break

      # --- 3) Anderson–Darling Test ---
      ad_results = stats.anderson(metric, dist='norm')
      print("Anderson–Darling statistic = {:.4f}".format(ad_results.statistic))
      for i, crit in enumerate(ad_results.critical_values):
          sl = ad_results.significance_level[i]
          print(f"At {sl}% significance level, critical value is {crit:.4f}.")

          if ad_results.statistic < crit:
            print(f"{metric_name} is normally distributed")
            break

  @staticmethod
  def execute():
    # For all langs
    # For all combinations of domains, at least 3

    # ------------------------
    # 1) Fetch metric data
    # ------------------------
    langs = ["c", "clojure", "elixir", "erlang", "haskell", "java", "javascript", "ocaml", "python"]
    # edu, seman, test, struct

    # domains = ["ml", "db", "lang", "game", "infr", "test", "build", "code", "ui", "comp", "log"]
    domains = ["ui", "db", "ml", "lang", "game"] #, "infr", "code", "comp", "backend", "frontend"]
    # domains = ["frontend", "backend", "infr", "db", "cli", "lang", "ml", "game", "comp", "build", "code"]
    metrics = METRICS

    per_lang_limit = 3000
    session = init_local_session()

    for metric in metrics:
      AlignedRankTransform._perform_art(langs, [domains], metric, per_lang_limit)

    # # Random domain combinations
    # def generate_domain_subsets(domains, min_size):
    #     subsets = []
    #     # for size in range(min_size, len(domains) + 1):
    #     subsets.extend(combinations(domains, min_size))
    #     return subsets

    # processes = []
    # domain_subsets = generate_domain_subsets(domains, 3)
    # metric = "term_entropy"

    # for i in range(NUM_PROCESSES):
    #     chunk = domain_subsets[i::NUM_PROCESSES]
    #     p = Process(target=AlignedRankTransform._perform_art, args=(langs, chunk, metric, per_lang_limit))
    #     p.start()
    #     processes.append(p)

    # for p in processes:
    #     p.join()

  @staticmethod
  def _perform_art(langs, domains_subset, metric, per_lang_limit):
    session = init_local_session()

    for domains in domains_subset:
      metric_values = Function.get_metrics_with_labels(session, langs=langs, limit=per_lang_limit, metric=metric, domains=domains)
      # result = AlignedRankTransform._execute(metric_values)
      result_srh = AlignedRankTransform._execute(metric_values)

      # print(result)

      # run = ARTRun(
      #   metric=metric,
      #   langs=" ".join(langs),
      #   domains=" ".join(domains),
      #   lang_fval=result["lang_fval"],
      #   domain_fval=result["domain_fval"],
      #   interact_fval=result["interact_fval"],
      #   paradigm_fval=result.get("paradigm_fval", None),
      # )
      # session.add(run)
      # session.commit()

  @staticmethod
  def _execute(metric_values):
    random.shuffle(metric_values)

    values = [value[0] for value in metric_values]
    languages = [value[1] for value in metric_values]
    domains = [value[2] for value in metric_values]
    paradigms = [LANG_TO_PARADIGM[value[1]] for value in metric_values]

    N = len(values)
    df = pd.DataFrame({'Language': languages, 'Domain': domains, 'Metric': values})

    # Inspect the first few rows
    # print(df.head())

    # ------------------------
    # 2) Model-fitting helper function
    # ------------------------
    def fit_and_anova(data, formula):
        """
        Fits an OLS model using the given formula and prints an ANOVA table.
        Returns the F value of the model.
        """
        model = smf.ols(formula, data=data).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        print(anova_table)
        f_val = anova_table['F'][0]
        return f_val

    # ------------------------
    # 3) Aligned Rank Transform Steps
    #    For each effect, we:
    #      - Fit a model *excluding* that effect (but including others).
    #      - Subtract the fitted values of that model from the original metric
    #        => "aligned" metric for the effect of interest
    #      - Rank the aligned metric
    #      - Then run an OLS (ANOVA) on the ranks with *only* the factor(s) of interest
    # ------------------------

    # --- 3a) Main effect of Language ---
    # Model that includes Domain and the interaction, but NO main effect of Language
    model_no_lang = smf.ols("Metric ~ C(Domain) + C(Language):C(Domain)", data=df).fit()
    df['Aligned_Lang'] = df['Metric'] - model_no_lang.fittedvalues

    # Now rank-transform these aligned values
    df['Ranked_Lang'] = rankdata(df['Aligned_Lang'])

    # Finally, do an ANOVA on the ranks with Language as the predictor
    print("=== ART for main effect of Language ===")
    lang_fval = fit_and_anova(df, "Ranked_Lang ~ C(Language)")

    # --- 3b) Main effect of Domain ---
    # Model that includes Language and the interaction, but NO main effect of Domain
    model_no_domain = smf.ols("Metric ~ C(Language) + C(Language):C(Domain)", data=df).fit()
    df['Aligned_Domain'] = df['Metric'] - model_no_domain.fittedvalues

    df['Ranked_Domain'] = rankdata(df['Aligned_Domain'])

    print("=== ART for main effect of Domain ===")
    domain_fval = fit_and_anova(df, "Ranked_Domain ~ C(Domain)")

    # --- 3c) Interaction Language × Domain ---
    # Model that includes ONLY the main effects, but NO interaction
    model_no_inter = smf.ols("Metric ~ C(Language) + C(Domain)", data=df).fit()
    df['Aligned_Interaction'] = df['Metric'] - model_no_inter.fittedvalues

    df['Ranked_Interaction'] = rankdata(df['Aligned_Interaction'])

    print("=== ART for interaction (Language × Domain) ===")
    interact_fval = fit_and_anova(df, "Ranked_Interaction ~ C(Language):C(Domain)")

    return {
      "lang_fval": lang_fval,
      "domain_fval": domain_fval,
      "interact_fval": interact_fval,
    }

  @staticmethod
  def _execute2(metric_values):
    """
    Perform Aligned Rank Transform for a nested design:
    - Paradigm (main)
    - Domain (main)
    - Nested factor: Language within Paradigm
    - Interaction: Paradigm x Domain

    Expects metric_values to be a list of tuples:
        (metric_value, language, domain, paradigm)
    where 'language' is effectively nested in 'paradigm'.
    """

    # Shuffle the data (optional, but can help with random tie-breaking in rankdata)
    random.shuffle(metric_values)

    # Unpack columns
    values = [mv[0] for mv in metric_values]
    languages = [mv[1] for mv in metric_values]
    domains = [mv[2] for mv in metric_values]
    paradigms = [LANG_TO_PARADIGM[mv[1]] for mv in metric_values]

    # Create a DataFrame
    df = pd.DataFrame({
        'Metric': values,
        'Language': languages,
        'Domain': domains,
        'Paradigm': paradigms
    })

    # For convenience, define a function to fit OLS & get the F-value from ANOVA
    def fit_and_anova(data, formula):
        model = smf.ols(formula, data=data).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        # Return or print desired stats. Here, we'll just print the table for illustration:
        print(anova_table)
        return anova_table

    # ---------------------------------------------------------------------
    # 1) Define the "full model" formula
    #    We treat language as nested in paradigm (Paradigm:Language) and
    #    also include Paradigm, Domain, and their interaction (Paradigm:Domain).
    # ---------------------------------------------------------------------
    full_model_formula = (
        "Metric ~ C(Paradigm) "
        "+ C(Domain) "
        "+ C(Paradigm):C(Domain) "
        "+ C(Paradigm):C(Language)"
    )

    # ---------------------------------------------------------------------
    # 2) For each effect of interest, build a "partial model" that EXCLUDES that effect,
    #    then align & rank, then do a simple ANOVA on only that effect.
    # ---------------------------------------------------------------------

    results = {}

    # -------------------------------------------
    # 2a) Main Effect of Paradigm
    # -------------------------------------------
    # Partial model EXCLUDING Paradigm, but INCLUDING Domain,
    # Paradigm:Domain, Paradigm:Language
    model_no_paradigm_formula = (
        "Metric ~ C(Domain) + C(Paradigm):C(Domain) + C(Paradigm):C(Language)"
    )
    model_no_paradigm = smf.ols(model_no_paradigm_formula, data=df).fit()
    df['Aligned_Paradigm'] = df['Metric'] - model_no_paradigm.fittedvalues
    df['Ranked_Paradigm'] = rankdata(df['Aligned_Paradigm'])

    print("=== ART for main effect of Paradigm (nested design) ===")
    results['paradigm_fval'] = fit_and_anova(df, "Ranked_Paradigm ~ C(Paradigm)")['F'][0]

    # -------------------------------------------
    # 2b) Main Effect of Domain
    # -------------------------------------------
    # Partial model EXCLUDING Domain, but INCLUDING Paradigm,
    # Paradigm:Domain, Paradigm:Language
    model_no_domain_formula = (
        "Metric ~ C(Paradigm) + C(Paradigm):C(Domain) + C(Paradigm):C(Language)"
    )
    model_no_domain = smf.ols(model_no_domain_formula, data=df).fit()
    df['Aligned_Domain'] = df['Metric'] - model_no_domain.fittedvalues
    df['Ranked_Domain'] = rankdata(df['Aligned_Domain'])

    print("=== ART for main effect of Domain (nested design) ===")
    results['domain_fval'] = fit_and_anova(df, "Ranked_Domain ~ C(Domain)")['F'][0]

    # -------------------------------------------
    # 2c) Interaction: Paradigm x Domain
    # -------------------------------------------
    # Partial model EXCLUDING Paradigm:Domain, but INCLUDING
    # Paradigm, Domain, Paradigm:Language
    model_no_interaction_formula = (
        "Metric ~ C(Paradigm) + C(Domain) + C(Paradigm):C(Language)"
    )
    model_no_interaction = smf.ols(model_no_interaction_formula, data=df).fit()
    df['Aligned_ParadigmDomain'] = df['Metric'] - model_no_interaction.fittedvalues
    df['Ranked_ParadigmDomain'] = rankdata(df['Aligned_ParadigmDomain'])

    print("=== ART for interaction (Paradigm x Domain) ===")
    results['interact_fval'] = fit_and_anova(
        df, "Ranked_ParadigmDomain ~ C(Paradigm):C(Domain)"
    )['F'][0]

    # -------------------------------------------
    # 2d) Nested Factor: Paradigm:Language
    # -------------------------------------------
    # This is effectively the "Language-within-Paradigm" effect.
    # Partial model EXCLUDING Paradigm:Language, but INCLUDING
    # Paradigm, Domain, Paradigm:Domain
    model_no_nested_formula = (
        "Metric ~ C(Paradigm) + C(Domain) + C(Paradigm):C(Domain)"
    )
    model_no_nested = smf.ols(model_no_nested_formula, data=df).fit()
    df['Aligned_Nested'] = df['Metric'] - model_no_nested.fittedvalues
    df['Ranked_Nested'] = rankdata(df['Aligned_Nested'])

    print("=== ART for nested factor (Paradigm:Language) ===")
    # Now we run an OLS on the ranks with the nested factor alone.
    # Because we are treating "Language" as nested in "Paradigm," we
    # specify "C(Paradigm):C(Language)" in the formula:
    results['lang_fval'] = fit_and_anova(
        df, "Ranked_Nested ~ C(Paradigm):C(Language)"
    )['F'][0]

    return results

  @staticmethod
  def _execute3(metric_values):
      """
      metric_values is expected to be a list of tuples/lists:
      [
        (value, language, domain),
        (value, language, domain),
        ...
      ]
      """
      # Shuffle data just as in your original code (optional).
      random.shuffle(metric_values)

      # Extract columns into separate lists
      values = [value[0] for value in metric_values]
      languages = [value[1] for value in metric_values]
      domains = [value[2] for value in metric_values]
      paradigms = [LANG_TO_PARADIGM[lang] for lang in languages]

      # Create a DataFrame
      df = pd.DataFrame({
          'Language': languages,
          'Domain': domains,
          'Metric': values
      })

      # ---------------------------------------------------------
      # Helper Functions for Partial Eta Squared / Partial Omega
      # ---------------------------------------------------------
      def partial_eta_squared(anova_tbl, factor_label):
          """Compute Partial Eta Squared for a given factor from the ANOVA table."""
          ss_effect = anova_tbl.loc[factor_label, 'sum_sq']
          ss_residual = anova_tbl.loc['Residual', 'sum_sq']
          return ss_effect / (ss_effect + ss_residual)

      def partial_omega_squared(anova_tbl, factor_label):
          """
          Compute Partial Omega Squared for a given factor from an ANOVA table
          generated by sm.stats.anova_lm(model, typ=2).
          """
          ss_effect = anova_tbl.loc[factor_label, 'sum_sq']
          df_effect = anova_tbl.loc[factor_label, 'df']
          ss_residual = anova_tbl.loc['Residual', 'sum_sq']
          
          # Manually compute mean square error (MSE) for the residual row:
          ms_error = ss_residual / anova_tbl.loc['Residual', 'df']
          
          # Partial omega squared formula
          #   ω_p^2 = (SS_effect - df_effect * MS_error) / (SS_effect + SS_residual + MS_error)
          return (ss_effect - df_effect * ms_error) / (ss_effect + ss_residual + ms_error)

      def fit_and_anova(data, formula, factor_label):
          """
          Fits an OLS model using the given formula and prints an ANOVA table.
          Returns F-value, partial eta squared, and partial omega squared for factor_label.
          """
          model = smf.ols(formula, data=data).fit()
          anova_table = sm.stats.anova_lm(model, typ=2)
          # print(anova_table)  # For debugging

          # Extract the row corresponding to the factor of interest
          f_val = anova_table.loc[factor_label, 'F']
          p_val = anova_table.loc[factor_label, 'PR(>F)']
          pes = partial_eta_squared(anova_table, factor_label)
          # pos = partial_omega_squared(anova_table, factor_label)
          pos = 0.0

          print(f"ANOVA for {factor_label}:")
          print(f"  F-value = {f_val:.3f}, p-value = {p_val:.4g}")
          print(f"  Partial eta squared = {pes:.3f}")
          # print(f"  Partial omega squared = {pos:.3f}\n")

          return f_val, pes, pos

      # ---------------------------------------------------------
      # 3) Aligned Rank Transform (ART) Steps
      # ---------------------------------------------------------
      #
      # We'll compute the aligned/rank-transformed data for each effect
      # (Language, Domain, and their Interaction). Then we'll run an OLS
      # on the ranked values, capturing F, partial eta^2, partial omega^2.

      # 3a) Main effect of Language
      # Model that includes Domain + interaction, but NO main effect of Language
      model_no_lang = smf.ols("Metric ~ C(Domain) + C(Language):C(Domain)", data=df).fit()
      df['Aligned_Lang'] = df['Metric'] - model_no_lang.fittedvalues
      df['Ranked_Lang'] = rankdata(df['Aligned_Lang'])

      print("=== ART for main effect of Language ===")
      lang_fval, lang_eta, lang_omega = fit_and_anova(
          df, "Ranked_Lang ~ C(Language)", factor_label="C(Language)"
      )

      # 3b) Main effect of Domain
      # Model that includes Language + interaction, but NO main effect of Domain
      model_no_domain = smf.ols("Metric ~ C(Language) + C(Language):C(Domain)", data=df).fit()
      df['Aligned_Domain'] = df['Metric'] - model_no_domain.fittedvalues
      df['Ranked_Domain'] = rankdata(df['Aligned_Domain'])

      print("=== ART for main effect of Domain ===")
      domain_fval, domain_eta, domain_omega = fit_and_anova(
          df, "Ranked_Domain ~ C(Domain)", factor_label="C(Domain)"
      )

      # 3c) Interaction: Language × Domain
      # Model that includes ONLY the main effects, but NO interaction
      model_no_inter = smf.ols("Metric ~ C(Language) + C(Domain)", data=df).fit()
      df['Aligned_Interaction'] = df['Metric'] - model_no_inter.fittedvalues
      df['Ranked_Interaction'] = rankdata(df['Aligned_Interaction'])

      print("=== ART for interaction (Language × Domain) ===")
      interact_fval, interact_eta, interact_omega = fit_and_anova(
          df, "Ranked_Interaction ~ C(Language):C(Domain)", 
          factor_label="C(Language):C(Domain)"
      )

      return {
          "lang_fval": lang_fval,
          "lang_eta": lang_eta,
          "lang_omega": lang_omega,
          "domain_fval": domain_fval,
          "domain_eta": domain_eta,
          "domain_omega": domain_omega,
          "interact_fval": interact_fval,
          "interact_eta": interact_eta,
          "interact_omega": interact_omega
      }

  @staticmethod
  def _execute_srh(metric_values):
      """
      metric_values: list of tuples (metric, language, domain)
      
      Returns a Scheirer-Ray-Hare results table (DataFrame).
      """
      # Shuffle data if you wish (optional)
      random.shuffle(metric_values)

      # Extract columns
      values = [row[0] for row in metric_values]
      languages = [row[1] for row in metric_values]
      domains = [row[2] for row in metric_values]
      paradigms = [LANG_TO_PARADIGM[lang] for lang in languages]

      # Create DataFrame
      df = pd.DataFrame({
          'Metric': values,
          'Language': languages,
          'Domain': domains
      })

      # Run Scheirer-Ray-Hare test
      results = AlignedRankTransform._scheirer_ray_hare_test(df, dv='Metric', factorA='Language', factorB='Domain')

      # Print or return the table
      print("=== Scheirer-Ray-Hare Test (Language, Domain) ===")
      print(results)
      return results

  @staticmethod
  def _scheirer_ray_hare_test(df, dv, factorA, factorB):
    """
    Perform the Scheirer-Ray-Hare test for two factors (factorA, factorB) on
    dependent variable (dv) in the given DataFrame `df`.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns [dv, factorA, factorB].
    dv : str
        The name of the dependent variable column (numeric).
    factorA : str
        The name of the first factor (categorical).
    factorB : str
        The name of the second factor (categorical).

    Returns
    -------
    results : pd.DataFrame
        A DataFrame summarizing the H-statistics and p-values for:
        [ factorA, factorB, interaction, error ]
        Similar to an ANOVA table, but using SRH-based H values and chi-square p-values.
    """
    # 1) Extract data
    data = df[[dv, factorA, factorB]].copy()
    data.dropna(inplace=True)

    # 2) Rank the entire DV column (like Kruskal-Wallis)
    data['Rank'] = rankdata(data[dv], method='average')

    # Basic checks
    levelsA = data[factorA].unique()
    levelsB = data[factorB].unique()
    a = len(levelsA)
    b = len(levelsB)
    N = len(data)

    # 3) Group by each cell [factorA x factorB]: sum of ranks, n per cell
    #    R_ij = sum of ranks in cell (i,j)
    grouped = data.groupby([factorA, factorB])['Rank']
    sum_ranks = grouped.sum()
    count_per_cell = grouped.count()

    # 4) Row/Column sums of ranks
    #    R_{i.} = sum of ranks for row i (factorA level)
    #    R_{.j} = sum of ranks for column j (factorB level)
    sum_ranks_A = sum_ranks.groupby(level=0).sum()  # Summation across factorB
    sum_ranks_B = sum_ranks.groupby(level=1).sum()  # Summation across factorA

    # 5) Cell sizes per row/column
    #    n_{i.}, n_{.j}, etc.
    n_by_A = count_per_cell.groupby(level=0).sum()
    n_by_B = count_per_cell.groupby(level=1).sum()

    # 6) Compute the Sums of Squares-like terms using SRH formulas
    #    H(A)   = 12 / [N*(N+1)] * Σ [ (R_{i.}^2 / n_{i.}) ] - 3*(N+1)
    #    H(B)   = analogous for factorB
    #    H(AB)  = 12 / [N*(N+1)] * Σ [ (R_{ij}^2 / n_{ij}) ] - H(A) - H(B) - 3*(N+1)
    #    H(total) = N*(N+1)/12
    #    H(error) = H(total) - [H(A) + H(B) + H(AB)]
    #    The degrees of freedom are:
    #      df(A) = a - 1
    #      df(B) = b - 1
    #      df(AB)= (a-1)*(b-1)
    #      df(error) = N - a*b

    # Helper to do the "sum of (row-sums^2 / n)" part
    def sum_of_squares_by_group(rank_sums, counts):
        return np.sum( (rank_sums**2) / counts )

    # a) H(A)
    termA = sum_of_squares_by_group(sum_ranks_A.values, n_by_A.values)
    H_A = (12.0 / (N * (N+1))) * termA - 3*(N+1)

    # b) H(B)
    termB = sum_of_squares_by_group(sum_ranks_B.values, n_by_B.values)
    H_B = (12.0 / (N * (N+1))) * termB - 3*(N+1)

    # c) H(AB)
    termAB = sum_of_squares_by_group(sum_ranks.values, count_per_cell.values)
    H_AB = (12.0 / (N * (N+1))) * termAB - H_A - H_B - 3*(N+1)

    # d) H(total) and H(error)
    H_total = N * (N+1) / 12.0
    H_error = H_total - (H_A + H_B + H_AB)

    # 7) Degrees of freedom
    dfA = a - 1
    dfB = b - 1
    dfAB = (a-1)*(b-1)
    dfE = N - a*b

    # 8) Convert H-values to p-values using chi-square approximation
    #    (Some texts suggest corrections for large ties or unbalanced data.)
    p_A = 1 - chi2.cdf(H_A, dfA) if dfA > 0 else np.nan
    p_B = 1 - chi2.cdf(H_B, dfB) if dfB > 0 else np.nan
    p_AB = 1 - chi2.cdf(H_AB, dfAB) if dfAB > 0 else np.nan

    # 9) Create a summary table akin to ANOVA
    results = pd.DataFrame({
        'Source': [factorA, factorB, f'{factorA}:{factorB}', 'Error'],
        'H': [H_A, H_B, H_AB, H_error],
        'df': [dfA, dfB, dfAB, dfE],
        'p-value': [p_A, p_B, p_AB, np.nan]  # error doesn't have a p-value
    })

    return results