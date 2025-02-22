import random
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
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
    domains = ["ui", "db", "ml", "lang", "game"]
    metrics = METRICS

    per_lang_limit = 10000
    session = init_local_session()

    for metric in metrics:
      AlignedRankTransform._perform_art(langs, [domains], metric, per_lang_limit)

    return

    # Random domain combinations
    def generate_domain_subsets(domains, min_size):
        subsets = []
        # for size in range(min_size, len(domains) + 1):
        subsets.extend(combinations(domains, min_size))
        return subsets

    processes = []
    domain_subsets = generate_domain_subsets(domains, 3)
    metric = "term_entropy"

    for i in range(NUM_PROCESSES):
        chunk = domain_subsets[i::NUM_PROCESSES]
        p = Process(target=AlignedRankTransform._perform_art, args=(langs, chunk, metric, per_lang_limit))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


  @staticmethod
  def _perform_art(langs, domains_subset, metric, per_lang_limit):
    session = init_local_session()

    for domains in domains_subset:
      metric_values = Function.get_metrics_with_labels(session, langs=langs, limit=per_lang_limit, metric=metric, domains=domains)
      result = AlignedRankTransform._execute(metric_values)

      run = ARTRun(
        metric=metric,
        langs=" ".join(langs),
        domains=" ".join(domains),
        lang_fval=result["lang_fval"],
        domain_fval=result["domain_fval"],
        interact_fval=result["interact_fval"],
      )
      session.add(run)
      session.commit()

  @staticmethod
  def _execute(metric_values):
    random.shuffle(metric_values)

    values = [value[0] for value in metric_values]
    languages = [value[1] for value in metric_values]
    domains = [value[2] for value in metric_values]
    # Fake domains
    # domains = [np.random.choice(domains) for _ in range(len(values))]

    N = len(values)
    df = pd.DataFrame({'Language': languages, 'Domain': domains, 'Metric': values })

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
        # print(anova_table)
        f_val = anova_table['F'][0]
        print(f_val)
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