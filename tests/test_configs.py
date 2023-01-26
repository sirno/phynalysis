"""Test configs module."""

from phynalysis.configs import BeastConfig, VirolutionConfig


def test_beast_config_encode_query():
    """Test encoding of query."""
    config = BeastConfig(
        template="template",
        sample="sample",
        n_samples=100,
        query="x > 0 and y == 1 and z < 2 and w in [1, 2, 3]",
    )
    assert config.encoded_query == "x_gt_0_and_y_eq_1_and_z_lt_2_and_w_in_1,2,3"


def test_beast_config_encode_seed():
    """Test encoding of seed."""
    config = BeastConfig(
        template="template",
        sample="sample",
        n_samples=100,
        phyn_seed=10,
        beast_seed=123,
    )
    assert config.encoded_seed == "phyn_seed_10_beast_seed_123"


def test_beast_config_config_path():
    """Test config path."""
    config = BeastConfig(
        template="template",
        sample="sample",
        n_samples=100,
        phyn_seed=10,
        beast_seed=123,
    )
    assert config.config_path() == "template/sample/all/100/phyn_seed_10_beast_seed_123"


def test_beast_config_expand_template_path():
    config = BeastConfig(template="template[1,2]", sample="sample", n_samples=100)
    configs = config.expand_paths()
    for idx, config in enumerate(configs):
        assert config.template == f"template{idx + 1}"


def test_beast_config_expand_sample_path():
    config = BeastConfig(template="template", sample="sample[1,2]", n_samples=100)
    configs = config.expand_paths()
    for idx, config in enumerate(configs):
        assert config.sample == f"sample{idx + 1}"


def test_beast_config_expand_paths():
    config = BeastConfig(template="template[1,2]", sample="sample[1,2]", n_samples=100)
    configs = config.expand_paths()
    for idx, config in enumerate(configs):
        assert config.template == f"template{idx // 2 + 1}"
        assert config.sample == f"sample{idx % 2 + 1}"
