import random
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import itertools

from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy.stats import rankdata, chi2
from itertools import combinations
from scipy.stats import rankdata
from multiprocessing import Process
from db.models import Function, ARTRun, ANOVARun
from db.utils import init_local_session
from rich.console import Console
from patsy.contrasts import Sum


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

console = Console()


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
      # grammar
    ]

    langs = ["c", "clojure", "elixir", "erlang", "haskell", "java", "javascript", "ocaml", "python"]

    domains = [
      ["ml", "infr", "db", "struct", "edu", "lang", "frontend", "backend", "build", "code", "cli", "comp", "game"],
      ["db", "lang", "game", "comp", "backend", "frontend", "ml"],
    ]
    metrics = METRICS
    session = init_local_session()

    for _ in range(10):
      for per_lang_limit in reversed([6300, 8400, 10600]):
        for metric in METRICS:
          AlignedRankTransform._perform_art(langs, domains, metric, per_lang_limit)

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
    console.print(f"Performing ART for {metric}, domains: {domains_subset}, with {per_lang_limit} examples per language")
    session = init_local_session()

    # ART
    # for domains in domains_subset:
    #   metric_values = Function.get_metrics_with_labels(session, langs=langs, limit=per_lang_limit, metric=metric, domains=domains)
    #   result = AlignedRankTransform._execute_art(metric_values)

    #   run = ARTRun(
    #     metric=metric,
    #     langs=" ".join(langs),
    #     domains=" ".join(domains),
    #     max_samples=per_lang_limit,
    #     lang_fval=result["lang_fval"],
    #     lang_p=result["lang_p"],
    #     lang_df=result["lang_df"],
    #     domain_fval=result["domain_fval"],
    #     domain_p=result["domain_p"],
    #     domain_df=result["domain_df"],
    #     interact_fval=result["interact_fval"],
    #     interact_p=result["interact_p"],
    #     interact_df=result["interact_df"],
    #   )
    #   session.add(run)
    #   session.commit()

    for domains in domains_subset:
      metric_values = Function.get_metrics_with_labels(session, langs=langs, limit=per_lang_limit, metric=metric, domains=domains)

      result = AlignedRankTransform._identify_language_differences(metric_values)
      AlignedRankTransform._interpret_language_differences(result)

    return

    # Classic ANOVA
    for domains in domains_subset:
      type_ = 3
      metric_values = Function.get_metrics_with_labels(session, langs=langs, limit=per_lang_limit, metric=metric, domains=domains)
      result = AlignedRankTransform._execute_anova(metric_values, type_)

      run = ANOVARun(
        metric=metric,
        langs=" ".join(langs),
        domains=" ".join(domains),
        typ=5,
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
  def _execute_anova(metric_values, typ):
    """
    Performs a Type III ANOVA on rank-transformed data with sum (effects) coding.

    metric_values: a list of (value, language, domain) tuples.
    Example: [(3.4, 'Python', 'Web'), (2.1, 'Java', 'ML'), ...]

    Returns:
       A dictionary with an ANOVA table (typ=3) from the
       rank-transformed data, plus partial effect sizes.
    """

    # Unpack the metric_values into separate lists
    values = [mv[0] for mv in metric_values]
    languages = [mv[1] for mv in metric_values]
    domains = [mv[2] for mv in metric_values]

    # Create DataFrame
    df = pd.DataFrame({
        'Language': pd.Categorical(languages),
        'Domain': pd.Categorical(domains),
        'Metric': values,
    })

    # ------------------------------------------------
    # 1) Apply sum coding (effects coding) to categorical variables
    # ------------------------------------------------
    # By default, statsmodels uses treatment coding, so we must manually set sum coding.
    df = df.assign(
        Language=df["Language"].cat.codes,  # Convert categories to numerical representation
        Domain=df["Domain"].cat.codes
    )

    # ------------------------------------------------
    # 2) Rank the Metric *once* across the entire dataset
    # ------------------------------------------------
    df['Ranked'] = rankdata(df['Metric'])

    # ------------------------------------------------
    # 3) Fit a Type III ANOVA on the ranks with sum coding
    # ------------------------------------------------
    model = smf.ols("Ranked ~ C(Language, Sum)*C(Domain, Sum)", data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=3)

    # ------------------------------------------------
    # 4) Calculate a partial effect size for each factor
    # ------------------------------------------------
    ss_res = anova_table.loc["Residual", "sum_sq"]

    effect_sizes = {}
    for factor in anova_table.index:  # Dynamically extract correct names
        if factor != "Residual":  # Ignore residual row
            ss_factor = anova_table.loc[factor, "sum_sq"]
            effect_sizes[factor] = ss_factor / (ss_factor + ss_res)

    results = {
        "anova_table": anova_table,

        "lang_p": anova_table.loc['C(Language, Sum)', 'PR(>F)'],
        "domain_p": anova_table.loc['C(Domain, Sum)', 'PR(>F)'],
        "interact_p": anova_table.loc['C(Language, Sum):C(Domain, Sum)', 'PR(>F)'],

        "lang_df": anova_table.loc['C(Language, Sum)', 'df'],
        "domain_df": anova_table.loc['C(Domain, Sum)', 'df'],
        "interact_df": anova_table.loc['C(Language, Sum):C(Domain, Sum)', 'df'],

        "lang_fval": anova_table.loc['C(Language, Sum)', 'F'],
        "domain_fval": anova_table.loc['C(Domain, Sum)', 'F'],
        "interact_fval": anova_table.loc['C(Language, Sum):C(Domain, Sum)', 'F'],

        "lang_es": effect_sizes['C(Language, Sum)'],
        "domain_es": effect_sizes['C(Domain, Sum)'],
        "interact_es": effect_sizes['C(Language, Sum):C(Domain, Sum)'],
    }

    print("\nANOVA Table (Type III, Sum Coding):\n", anova_table)
    print("\nPartial Eta-Squared Effect Sizes:\n", effect_sizes)

    return results    

  @staticmethod
  def _identify_language_differences(metric_values, alpha=0.05):
    """
    Identifies language pairs with largest metric differences using:
    - Mann-Whitney U tests (non-parametric)
    - Cliff's delta effect sizes
    - Holm-Bonferroni correction
    - Rank-transformed data (for consistency with ANOVA)
    
    Returns sorted list of pairs by effect size magnitude.
    """
    # Create DataFrame with ranked data
    df = pd.DataFrame({
        'Language': [mv[1] for mv in metric_values],
        'Metric': [mv[0] for mv in metric_values]
    })
    
    # Rank across entire dataset (aligns with ANOVA procedure)
    df['Ranked'] = rankdata(df['Metric'])
    
    # Get unique languages and their ranked metrics
    languages = df['Language'].unique()
    language_pairs = list(itertools.combinations(languages, 2))
    
    results = []
    for lang1, lang2 in language_pairs:
        # Get ranks for both languages (all domains combined)
        ranks1 = df[df['Language'] == lang1]['Ranked']
        ranks2 = df[df['Language'] == lang2]['Ranked']
        
        # Mann-Whitney U test
        u_stat, p_val = mannwhitneyu(ranks1, ranks2, alternative='two-sided')
        
        # Cliff's delta calculation
        n1, n2 = len(ranks1), len(ranks2)
        cliff_delta = (2 * u_stat / (n1 * n2)) - 1  # Range: [-1, 1]
        
        results.append({
            'comparison': f"{lang1} vs {lang2}",
            'p_value': p_val,
            'cliffs_delta': cliff_delta,
            'n1': n1,
            'n2': n2
        })
    
    # Multiple comparisons adjustment
    p_values = [res['p_value'] for res in results]
    reject, adj_p_values, _, _ = multipletests(p_values, alpha=alpha, method='holm')
    
    # Add adjusted p-values and significance
    for i, res in enumerate(results):
        res['adj_p_value'] = adj_p_values[i]
        res['significant'] = adj_p_values[i] < alpha
    
    # Sort by effect size magnitude (absolute value)
    results.sort(key=lambda x: abs(x['cliffs_delta']), reverse=True)
    
    return results

  @staticmethod
  def _interpret_language_differences(results, alpha=0.05, top_n=10):
    """Prints formatted interpretation of language comparisons"""
    print(f"\n{'Language Pair':<25} {'Cliffs δ':<10} {'p-value':<12} {'Sig.':<6}")
    print("-"*55)
    for res in results[:top_n]:
        sig = "***" if res['adj_p_value'] < 0.001 else \
              "**" if res['adj_p_value'] < 0.01 else \
              "*" if res['significant'] else ""
        print(f"{res['comparison']:<25} {res['cliffs_delta']:+.2f}{sig:<5} {res['adj_p_value']:.4f}")

    # Print key findings
    sig_results = [res for res in results if res['significant']]
    print(f"\nKey Findings (α={alpha}):")
    print(f"- Total comparisons: {len(results)}")
    print(f"- Significant pairs: {len(sig_results)}")
    
    if sig_results:
        print("\nLargest Differences:")
        for res in sig_results[:5]:
            direction = "higher" if res['cliffs_delta'] > 0 else "lower"
            print(f"- {res['comparison']}: {direction} ranks (δ={res['cliffs_delta']:.2f}, p={res['adj_p_value']:.4f})")

  @staticmethod
  def _nonparametric_simple_effects_test(metric_values, alpha=0.05):
    """
    Non-parametric pairwise tests for unbalanced, non-normal data.
    Uses rank-transformed metric and Holm-Bonferroni correction.
    """
    # Prepare DataFrame with original labels and ranks
    df = pd.DataFrame({
        'Language': [mv[1] for mv in metric_values],
        'Domain': [mv[2] for mv in metric_values],
        'Metric': [mv[0] for mv in metric_values]
    })
    df['Ranked'] = rankdata(df['Metric'])  # Use same rank transform as ANOVA
    
    # Generate all (lang, domain) pairs
    pairs = list(df.groupby(['Language', 'Domain']).groups.keys())
    
    results = []
    for pair in itertools.combinations(pairs, 2):
        (lang1, domain1), (lang2, domain2) = pair
        # Extract ranked data for groups
        group1 = df[(df['Language'] == lang1) & (df['Domain'] == domain1)]['Ranked']
        group2 = df[(df['Language'] == lang2) & (df['Domain'] == domain2)]['Ranked']
        
        # Mann-Whitney U test (non-parametric, handles unbalanced groups)
        u_stat, p_val = mannwhitneyu(group1, group2, alternative='two-sided')
        
        # Cliff's delta (non-parametric effect size)
        n1, n2 = len(group1), len(group2)
        cliff_delta = (2 * u_stat / (n1 * n2)) - 1  # Ranges [-1, 1]
        
        results.append({
            'comparison': f"{lang1} ({domain1}) vs {lang2} ({domain2})",
            'p_value': p_val,
            'cliffs_delta': cliff_delta,
            'n1': n1,
            'n2': n2
        })
    
    # Apply Holm-Bonferroni correction (less conservative)
    p_values = [res['p_value'] for res in results]
    reject, adj_p_values, _, _ = multipletests(p_values, alpha=alpha, method='holm')
    
    # Update results
    for i, res in enumerate(results):
        res['adj_p_value'] = adj_p_values[i]
        res['significant'] = adj_p_values[i] < alpha
    
    # Sort by effect size magnitude
    results.sort(key=lambda x: abs(x['cliffs_delta']), reverse=True)
    
    return results

  @staticmethod
  def _interpret_simple_effects(results, alpha=0.05):
    """Prints formatted interpretation of simple effects results"""
    print(f"\n{'Comparison':<40} {'Cliffs δ':<10} {'Adj p-value':<12} {'Significant':<10}")
    print("-"*75)
    for res in results:
        sig = "***" if res['adj_p_value'] < 0.001 else "**" if res['adj_p_value'] < 0.01 else "*" if res['significant'] else ""
        print(f"{res['comparison']:<40} {res['cliffs_delta']:+.2f}{sig:<10} {res['adj_p_value']:.4f}       {str(res['significant'])}")

    # Print key findings
    sig_results = [res for res in results if res['significant']]
    print(f"\nFound {len(sig_results)} significant pairs (α={alpha}):")
    for res in sig_results[:5]:  # Show top 5
        direction = "higher" if res['cliffs_delta'] > 0 else "lower"
        print(f"- {res['comparison']}: {direction} ranks (δ={res['cliffs_delta']:.2f}, p={res['adj_p_value']:.4f})")


  # @staticmethod
  # def _execute_anova(metric_values, typ):
  #   """
  #   metric_values: a list of (value, language, domain) tuples.
  #   Example: [(3.4, 'Python', 'Web'), (2.1, 'Java', 'ML'), ...]

  #   Returns:
  #      A dictionary with an ANOVA table (typ=2) from the
  #      rank-transformed data, plus partial effect sizes.
  #   """

  #   # Unpack the metric_values into separate lists
  #   values = [mv[0] for mv in metric_values]
  #   languages = [mv[1] for mv in metric_values]
  #   domains = [mv[2] for mv in metric_values]

  #   # Create DataFrame
  #   df = pd.DataFrame({
  #       'Subject': range(len(values)),
  #       'Language': languages,
  #       'Domain': domains,
  #       'Metric': values,
  #   })

  #   # ------------------------------------------------
  #   # 1) Rank the Metric *once* across the entire dataset
  #   # ------------------------------------------------
  #   df['Ranked'] = rankdata(df['Metric'])

  #   # ------------------------------------------------
  #   # 2) Fit a standard two-way ANOVA on the ranks
  #   # ------------------------------------------------
  #   # Model formula includes main effects + interaction
  #   # so we can see if there's a significant Language*Domain effect as well.
  #   model = smf.ols("Ranked ~ C(Language, Sum)*C(Domain, Sum)", data=df).fit()
  #   anova_table = sm.stats.anova_lm(model, typ=typ)

  #   # ------------------------------------------------
  #   # 3) Calculate a partial effect size for each factor
  #   #    (e.g., rank-based partial eta^2 or epsilon^2)
  #   # ------------------------------------------------
  #   # We'll do the usual ratio: SS_effect / (SS_effect + SS_residual)
  #   # from the single unified model
  #   ss_res = anova_table.loc["Residual", "sum_sq"]

  #   effect_sizes = {}
  #   for factor in ["C(Language, Sum)", "C(Domain, Sum)", "C(Language, Sum):C(Domain, Sum)"]:
  #       ss_factor = anova_table.loc[factor, "sum_sq"]
  #       effect_sizes[factor] = ss_factor / (ss_factor + ss_res)

  #   results = {
  #       "lang_p": anova_table.loc['C(Language, Sum)', 'PR(>F)'],
  #       "domain_p": anova_table.loc['C(Domain, Sum)', 'PR(>F)'],
  #       "interact_p": anova_table.loc['C(Language, Sum):C(Domain, Sum)', 'PR(>F)'],

  #       "lang_df": anova_table.loc['C(Language, Sum)', 'df'],
  #       "domain_df": anova_table.loc['C(Domain, Sum)', 'df'],
  #       "interact_df": anova_table.loc['C(Language, Sum):C(Domain, Sum)', 'df'],

  #       "lang_fval": anova_table.loc['C(Language, Sum)', 'F'],
  #       "domain_fval": anova_table.loc['C(Domain, Sum)', 'F'],
  #       "interact_fval": anova_table.loc['C(Language, Sum):C(Domain, Sum)', 'F'],

  #       "lang_es": effect_sizes['C(Language, Sum)'],
  #       "domain_es": effect_sizes['C(Domain, Sum)'],
  #       "interact_es": effect_sizes['C(Language, Sum):C(Domain, Sum)'],
  #   }
  #   print(results)
  #   return results

  @staticmethod
  def _execute_art(metric_values):
      """
      metric_values is expected to be a list of tuples/lists:
      [
        (value, language, domain),
        (value, language, domain),
        ...
      ]
      """
      values = [value[0] for value in metric_values]
      languages = [value[1] for value in metric_values]
      domains = [value[2] for value in metric_values]

      df = pd.DataFrame({
          'Language': languages,
          'Domain': domains,
          'Metric': values
      })

      def fit_and_anova(data, formula, factor_label):
          """
          Fits an OLS model using the given formula and prints an ANOVA table.
          Returns F-value, partial eta squared, and partial omega squared for factor_label.
          """
          model = smf.ols(formula, data=data).fit()
          anova_table = sm.stats.anova_lm(model, typ=2)
          # print(anova_table) 

          f_val = anova_table.loc[factor_label, 'F']
          p_val = anova_table.loc[factor_label, 'PR(>F)']
          df_val = anova_table.loc[factor_label, 'df']

          return f_val, p_val, df_val

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

      lang_fval, lang_p, lang_df = fit_and_anova(
          df, "Ranked_Lang ~ C(Language)", factor_label="C(Language)"
      )

      # 3b) Main effect of Domain
      # Model that includes Language + interaction, but NO main effect of Domain
      model_no_domain = smf.ols("Metric ~ C(Language) + C(Language):C(Domain)", data=df).fit()
      df['Aligned_Domain'] = df['Metric'] - model_no_domain.fittedvalues
      df['Ranked_Domain'] = rankdata(df['Aligned_Domain'])

      domain_fval, domain_p, domain_df = fit_and_anova(
          df, "Ranked_Domain ~ C(Domain)", factor_label="C(Domain)"
      )

      # 3c) Interaction: Language × Domain
      # Model that includes ONLY the main effects, but NO interaction
      model_no_inter = smf.ols("Metric ~ C(Language) + C(Domain)", data=df).fit()
      df['Aligned_Interaction'] = df['Metric'] - model_no_inter.fittedvalues
      df['Ranked_Interaction'] = rankdata(df['Aligned_Interaction'])

      interact_fval, interact_p, interact_df = fit_and_anova(
          df, "Ranked_Interaction ~ C(Language):C(Domain)", 
          factor_label="C(Language):C(Domain)"
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