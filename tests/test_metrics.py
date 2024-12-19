from scripts.metrics.basic import *


def test_get_median_length():
  assert get_median_length(['a', 'ab', 'abc']) == 2
  assert get_median_length(['abc', 'abc', 'abc']) == 3
  assert get_median_length(['a', 'ab', 'abc', 'abcd']) == 2.5


def test_get_syllable_count():
  assert get_syllable_count('abc') == 1
  assert get_syllable_count('helloWorld') == 3
  assert get_syllable_count('__helloWorld_') == 3
  assert get_syllable_count('hello_world') == 3
  assert get_syllable_count('hello-world') == 3
  assert get_syllable_count('helloworld') == 3
  assert get_syllable_count('hello+world') == 3
  assert get_syllable_count('HELLO_world') == 3


def test_get_casing_style():
  assert get_casing_style('helloWorld') == 'camelcase'
  assert get_casing_style('hello_world') == 'snakecase'
  assert get_casing_style('hello-world') == 'kebabcase'
  assert get_casing_style('HELLO_world') == 'unknown'
  assert get_casing_style('HELLO_WORLD') == 'macrocase'
  assert get_casing_style('hello') == 'nocase'
  assert get_casing_style('__hello__') == 'unknown'
  assert get_casing_style('a') == 'nocase'


def test_get_soft_words():
  assert get_soft_words('helloWorld') == ['hello', 'world']
  assert get_soft_words('hello_world') == ['hello', 'world']
  assert get_soft_words('hello-world') == ['hello', 'world']
  assert get_soft_words('HELLO_world') == ['hello', 'world']
  assert get_soft_words('HELLO_WORLD') == ['hello', 'world']
  assert get_soft_words('HELLO_WORLD123') == ['hello', 'world123']
  assert get_soft_words('HELLO_WORLD_123') == ['hello', 'world', '123']
  assert get_soft_words('HELLO_WORLD_123&%$') == ['hello', 'world', '123&%$']
  assert get_soft_words('hello') == ['hello']
  assert get_soft_words('hello\'') == ['hello\''] # Clojure
  assert get_soft_words('c0') == ['c0']
  assert get_soft_words('__c0__') == ['c0']
  assert get_soft_words('+c0+') == ['+c0+']


def test_get_num_dictionary_words():
  assert get_num_dictionary_words(['hello', 'world']) == 2
  assert get_num_dictionary_words(['hello', 'world', 'c0']) == 2
  assert get_num_dictionary_words(['hello', 'world', 'c0', 'idx', 'a841', 'hello\'']) == 3
  assert get_num_dictionary_words(['__hello__']) == 0
  assert get_num_dictionary_words(['x', 'y', 'a']) == 0


def test_get_duplicate_percentage():
  assert get_duplicate_percentage(['hello', 'world']) == 0
  assert get_duplicate_percentage(['hello', 'hello']) == 0.5
  assert get_duplicate_percentage(['hello', 'hello', 'world']) == 0.3333333333333333
  assert get_duplicate_percentage(['hello', 'world', 'hello', 'world']) == 0.5


def test_get_median_levenshtein_distance():
  assert get_median_levenshtein_distance([('hello', 'world')]) == 4
  assert get_median_levenshtein_distance([('hello', 'world'), ('hello', 'world')]) == 4


def test_get_basic_metrics():
  abbreviations = load_abbreviations("build/abbreviations.csv")
  lev_dist = get_median_levenshtein_distance([('hello', 'world')])

  assert get_basic_metrics(['hello', 'world'], abbreviations) == {
    'median_length': 5,
    'median_syllable_count': 1.5,
    'median_soft_word_count': 1,
    'duplicate_percentage': 0,
    'num_single_letter_names': 0,
    'most_common_casing_style': 'nocase',
    'percent_abbreviations': 0,
    'median_levenshtein_distance': lev_dist,
    'percent_dictionary_words': 1.0,
    'consistency_violations': 0,
    'conciseness_violations': 0
  }

  result = get_basic_metrics(['hello', 'world', 'hello', 'world'], abbreviations)
  assert result['consistency_violations'] == 0
  assert result['conciseness_violations'] == 0

  result = get_basic_metrics(['hello', 'helloWorld'], abbreviations)
  assert result['consistency_violations'] == 1
  assert result['conciseness_violations'] == 1

  result = get_basic_metrics(['hello', 'world', 'helloWorld'], abbreviations)
  assert result['consistency_violations'] == 2
  assert result['conciseness_violations'] == 2

  result = get_basic_metrics(['hello', 'world', 'helloWorldhello'], abbreviations)
  assert result['consistency_violations'] == 1
  assert result['conciseness_violations'] == 2
