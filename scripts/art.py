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
from db.models import Function, ARTRun, ANOVARun, MannWhitneyu
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
      # "median_id_length", 
      # "median_id_soft_word_count",
      # "id_duplicate_percentage",
      # "num_single_letter_ids",
      # "id_percent_abbreviations",
      # "id_percent_dictionary_words",
      # "num_conciseness_violations",
      # "num_consistency_violations",
      # "term_entropy",
      # "median_id_lv_dist",
      # "median_id_semantic_similarity",
      # "median_word_concreteness",
      # "context_coverage",
      "grammar_hash"
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
          # AlignedRankTransform._perform('art', langs, domains, metric, per_lang_limit)
          AlignedRankTransform._perform('anova', langs, domains, metric, per_lang_limit)

    # langs = ["c", "clojure", "elixir", "erlang", "haskell", "fortran", "java", "javascript", "ocaml", "python"]
    # domains = ["ml", "infr", "db", "struct", "edu", "lang", "frontend", "backend", "build", "code", "cli", "comp", "game"]

    # for _ in range(30):
    #   for metric in METRICS:
    #     AlignedRankTransform._perform('interaction_deviations', langs, [domains], metric, 10600)


  @staticmethod
  def _perform(test, langs, domains_subset, metric, per_lang_limit):
    console.print(f"Performing ART for {metric}, domains: {domains_subset}, with {per_lang_limit} examples per language")
    session = init_local_session()

    if test == 'art':
      for domains in domains_subset:
        metric_values = Function.get_metrics_with_labels(session, langs=langs, limit=per_lang_limit, metric=metric, domains=domains)
        results = AlignedRankTransform._execute_art(metric_values)

        run = ARTRun(
          metric=metric,
          langs=" ".join(langs),
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
    
    if test == 'interaction_deviations':
      for domains in domains_subset:
        metric_values = Function.get_metrics_with_labels(session, langs=langs, limit=per_lang_limit, metric=metric, domains=domains)
        results = AlignedRankTransform._identify_deviant_languages(metric_values)

        for result in results:
          run = MannWhitneyu(
              metric=metric,
              max_samples=per_lang_limit,
              language=result['language'],
              p_value=result['p_value'],
              adj_p_value=result['adj_p_value'],
              cliffs_delta=result['cliffs_delta'],
              median_diff=result['median_diff'],
              n_obs=result['n_obs'],
              overall_median=result['overall_median']
          )
          session.add(run)

        session.commit()

    if test == 'anova':
      for domains in domains_subset:
        metric_values = Function.get_metrics_with_labels(session, langs=langs, limit=per_lang_limit, metric=metric, domains=domains)
        result = AlignedRankTransform._execute_anova(metric_values, 3)

        run = ANOVARun(
          metric=metric,
          langs=" ".join(langs),
          domains=" ".join(domains),
          typ=4,
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
  def _interpret_deviant_languages(results, alpha=0.05, top_n=10):
    """Prints formatted interpretation of language deviations"""
    print(f"\n{'Language':<15} {'δ vs Others':<12} {'Med Diff':<12} {'p-value':<12} {'Sig.':<6}")
    print("-"*60)
    for res in results[:top_n]:
        sig = "***" if res['adj_p_value'] < 0.001 else \
              "**" if res['adj_p_value'] < 0.001 else \
              "*" if res['significant'] else ""
        print(f"{res['language']:<15} {res['cliffs_delta']:+.2f}{sig:<5} "
              f"{res['median_diff']:+.2f}{'*' if res['significant'] else '':<5} "
              f"{res['adj_p_value']:.4f}")

    # Print key findings
    sig_results = [res for res in results if res['significant']]
    print(f"\nKey Findings (α={alpha}):")
    print(f"- Total languages: {len(results)}")
    print(f"- Significant deviations: {len(sig_results)}")
    
    if sig_results:
        print("\nMost Distinctive Languages:")
        for res in sig_results[:5]:
            direction = "above" if res['median_diff'] > 0 else "below"
            print(f"- {res['language']}: {direction} average by {abs(res['median_diff']):.2f} "
                  f"(δ={res['cliffs_delta']:.2f}, p={res['adj_p_value']:.4f})")

  @staticmethod
  def _test_interaction_deviations(metric_values, alpha=0.05, min_sample=10):
    """
    Identifies exceptional (language, domain) combinations using:
    - Rank transformation for non-parametric analysis
    - Comparison against all other combinations
    - Cliff's delta effect sizes
    - Holm-Bonferroni correction
    - Practical median differences
    
    Returns sorted list of (lang, domain) pairs by interaction strength.
    """
    # Create DataFrame with ranked data
    df = pd.DataFrame({
        'Language': [mv[1] for mv in metric_values],
        'Domain': [mv[2] for mv in metric_values],
        'Metric': [mv[0] for mv in metric_values]
    })
    
    # Rank across entire dataset (aligns with ANOVA)
    df['Ranked'] = rankdata(df['Metric'])
    
    # Get unique (lang, domain) combinations
    groups = df.groupby(['Language', 'Domain'])
    combinations = list(groups.groups.keys())
    
    results = []
    for (lang, domain) in combinations:
        # Get target group and all others
        target_mask = (df['Language'] == lang) & (df['Domain'] == domain)
        target_group = df[target_mask]
        other_groups = df[~target_mask]
        
        # Skip small samples
        if len(target_group) < min_sample:
            continue
            
        # Non-parametric comparison
        u_stat, p_val = mannwhitneyu(target_group['Ranked'], 
                                   other_groups['Ranked'],
                                   alternative='two-sided')
        
        # Effect size calculations
        n1, n2 = len(target_group), len(other_groups)
        cliff_delta = (2 * u_stat / (n1 * n2)) - 1  # [-1, 1]
        
        # Practical difference metrics
        target_median = np.median(target_group['Metric'])
        overall_median = np.median(df['Metric'])
        median_diff = target_median - overall_median
        
        results.append({
            'combination': f"{lang} × {domain}",
            'language': lang,
            'domain': domain,
            'p_value': p_val,
            'cliffs_delta': cliff_delta,
            'median_diff': median_diff,
            'n_obs': len(target_group),
            'overall_median': overall_median
        })
    
    # Multiple comparisons adjustment
    p_values = [res['p_value'] for res in results]
    reject, adj_p_values, _, _ = multipletests(p_values, alpha=alpha, method='holm')
    
    # Add adjusted p-values and significance
    for i, res in enumerate(results):
        res['adj_p_value'] = adj_p_values[i]
        res['significant'] = adj_p_values[i] < alpha
    
    # Sort by absolute effect size and significance
    results.sort(key=lambda x: (abs(x['cliffs_delta']), -x['adj_p_value']), reverse=True)
    
    return results

  @staticmethod
  def interpret_interaction_deviations(results, alpha=0.05, top_n=10):
    """Prints formatted interpretation of interaction effects"""
    print(f"\n{'Combination':<25} {'δ vs Others':<12} {'Med Diff':<12} {'p-value':<12} {'Sig.':<6}")
    print("-"*65)
    for res in results[:top_n]:
      sig = "***" if res['adj_p_value'] < 0.001 else \
            "**" if res['adj_p_value'] < 0.01 else \
            "*" if res['significant'] else ""
      print(f"{res['combination']:<25} {res['cliffs_delta']:+.2f}{sig:<5} "
            f"{res['median_diff']:+.2f}{'*' if res['significant'] else '':<5} "
            f"{res['adj_p_value']:.4f}")

    # Print key findings
    sig_results = [res for res in results if res['significant']]
    print(f"\nKey Interaction Findings (α={alpha}):")
    print(f"- Total combinations tested: {len(results)}")
    print(f"- Significant deviations: {len(sig_results)}")
    
    if sig_results:
        print("\nMost Exceptional Interactions:")
        for res in sig_results[:5]:
            direction = "above" if res['median_diff'] > 0 else "below"
            print(f"- {res['combination']}: {direction} average by {abs(res['median_diff']):.2f} "
                  f"(δ={res['cliffs_delta']:.2f}, p={res['adj_p_value']:.4f})")

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

  @staticmethod
  def _identify_deviant_languages(metric_values, alpha=0.05, min_sample=10):
    """
    Identifies languages deviating most from the overall pattern (across all domains) using:
    - Rank transformation
    - Mann-Whitney U tests (language vs all others)
    - Cliff's delta effect sizes
    - Holm-Bonferroni correction
    """
    # Create DataFrame with ranked data
    df = pd.DataFrame({
        'Language': [mv[1] for mv in metric_values],
        'Metric': [mv[0] for mv in metric_values]
    })
    
    # Rank across entire dataset (aligned with previous ANOVA)
    df['Ranked'] = rankdata(df['Metric'])
    
    # Get unique languages
    languages = df['Language'].unique()
    
    results = []
    for lang in languages:
        # Split into target vs all others (regardless of domain)
        target_mask = df['Language'] == lang
        target_group = df[target_mask]
        other_groups = df[~target_mask]
        
        # Skip small samples
        if len(target_group) < min_sample:
            continue
            
        # Mann-Whitney U test
        u_stat, p_val = mannwhitneyu(target_group['Ranked'], 
                                   other_groups['Ranked'],
                                   alternative='two-sided')
        
        # Cliff's delta
        n1, n2 = len(target_group), len(other_groups)
        cliff_delta = (2 * u_stat / (n1 * n2)) - 1
        
        # Practical difference metrics
        target_median = np.median(target_group['Metric'])
        overall_median = np.median(df['Metric'])
        median_diff = target_median - overall_median
        
        results.append({
            'language': lang,
            'p_value': p_val,
            'cliffs_delta': cliff_delta,
            'median_diff': median_diff,
            'n_obs': len(target_group),
            'overall_median': overall_median
        })
    
    # Multiple comparisons adjustment
    p_values = [res['p_value'] for res in results]
    reject, adj_p_values, _, _ = multipletests(p_values, alpha=alpha, method='holm')
    
    # Add adjusted p-values and significance
    for i, res in enumerate(results):
        res['adj_p_value'] = adj_p_values[i]
        res['significant'] = adj_p_values[i] < alpha
    
    # Sort by absolute effect size
    results.sort(key=lambda x: abs(x['cliffs_delta']), reverse=True)
    
    return results