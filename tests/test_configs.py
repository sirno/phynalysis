"""Test configs module."""

from phynalysis.configs import BeastJobConfig, VirolutionJobConfig, SimulationParameters
import yaml
import sys


def test_beast_config_encode_query():
    """Test encoding of query."""
    config = BeastJobConfig(
        template="template",
        sample="sample",
        n_samples=100,
        query="x > 0 and y == 1 and z < 2 and w in [1, 2, 3]",
    )
    assert config.encoded_query == "x_gt_0_and_y_eq_1_and_z_lt_2_and_w_in_1,2,3"


def test_beast_config_encode_seed():
    """Test encoding of seed."""
    config = BeastJobConfig(
        template="template",
        sample="sample",
        n_samples=100,
        phyn_seed=10,
        beast_seed=123,
    )
    assert config.encoded_seed == "phyn_seed_10_beast_seed_123"


def test_beast_config_config_path():
    """Test config path."""
    config = BeastJobConfig(
        template="template",
        sample="sample",
        n_samples=100,
        phyn_seed=10,
        beast_seed=123,
    )
    assert config.config_path() == "template/sample/all/100/phyn_seed_10_beast_seed_123"


def test_beast_config_expand_template_path():
    config = BeastJobConfig(template="template[1,2]", sample="sample", n_samples=100)
    configs = config.expand_paths()
    for idx, config in enumerate(configs):
        assert config.template == f"template{idx + 1}"


def test_beast_config_expand_sample_path():
    config = BeastJobConfig(template="template", sample="sample[1,2]", n_samples=100)
    configs = config.expand_paths()
    for idx, config in enumerate(configs):
        assert config.sample == f"sample{idx + 1}"


def test_beast_config_expand_paths():
    config = BeastJobConfig(template="template[1,2]", sample="sample[1,2]", n_samples=100)
    configs = config.expand_paths()
    for idx, config in enumerate(configs):
        assert config.template == f"template{idx // 2 + 1}"
        assert config.sample == f"sample{idx % 2 + 1}"


def test_virolution_config_expand_path():
    config = VirolutionJobConfig(path="path[1,2]", generations=100, compartments=1)
    configs = config.expand_path()
    for idx, config in enumerate(configs):
        assert config.path == f"path{idx + 1}"


def test_virolution_settings():
    config = """\
mutation_rate: 1e-6
recombination_rate: 0
host_population_size: 100000000
infection_fraction: 0.7
basic_reproductive_number: 100.0
max_population: 100000000
dilution: 0.02
substitution_matrix:
- - 0.0
  - 1.0
  - 1.0
  - 1.0
- - 1.0
  - 0.0
  - 1.0
  - 1.0
- - 1.0
  - 1.0
  - 0.0
  - 1.0
- - 1.0
  - 1.0
  - 1.0
  - 0.0
fitness_model:
  distribution: !Exponential
    weights:
      beneficial: 0.29
      deleterious: 0.51
      lethal: 0.2
      neutral: 0.0
    lambda_beneficial: 0.03
    lambda_deleterious: 0.21
  utility: !Algebraic
    upper: 1.5
"""
    settings = SimulationParameters.from_yaml(config)
    config2 = settings.to_yaml()
    assert config == config2
