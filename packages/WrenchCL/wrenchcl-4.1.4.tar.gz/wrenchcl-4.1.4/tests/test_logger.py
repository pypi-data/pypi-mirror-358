import logging
import os
import re
import sys
import time
from io import StringIO

import pytest
from pydantic import BaseModel

from WrenchCL.Tools.ccLogBase import logger


class DummyPretty:
    def pretty_repr(self):
        return "PRETTY_PRINTED"


class DummyJSON:
    def json(self):
        return {
                "meta_data": {"integration_test": True},
                "targets": {"likes": 3091},
                "post_url": "https://picsum.photos/455",
                "file_type": "video",
                "spirra_media_id": "4e05cc02-d0e1-4db7-86bc-4267642b2c3c",
                "spirra_influencer_id": "7076e470-9809-45a6-8e04-74db55b8ab83",
                "social_media_platform": "facebook"
                }


class SuggestionTarget:
    def __init__(self):
        self.valid_key = 1


class DummyPydantic(BaseModel):
    name: str
    value: int


@pytest.fixture
def logger_stream():
    stream = StringIO()
    os.environ["PROJECT_NAME"] = "ai-axis"
    os.environ["PROJECT_VERSION"] = "1.2.3"
    os.environ["ENV"] = "dev"

    logger.reinitialize()
    logger.add_new_handler(logging.StreamHandler, stream=stream, force_replace=True)
    logger.add_new_handler(logging.StreamHandler, stream=sys.stdout)

    yield logger, stream

    for key in ["PROJECT_NAME", "PROJECT_VERSION", "ENV"]:
        os.environ.pop(key, None)


def flush_handlers(logger):
    for h in logger.logger_instance.handlers:
        h.flush()


def test_info_log(logger_stream):
    logger, stream = logger_stream
    logger.info("test info")
    flush_handlers(logger)
    assert "test info" in stream.getvalue()


def test_info_log_w_header(logger_stream):
    logger, stream = logger_stream
    logger.info("test info", header="Little Info Header")
    flush_handlers(logger)
    assert "test info" in stream.getvalue()
    assert "LITTLE INFO HEADER" in stream.getvalue()


def test_internal_log(logger_stream):
    logger, stream = logger_stream
    logger._internal_log("test internal")
    flush_handlers(logger)
    assert "test internal" in stream.getvalue()


def test_warning_log(logger_stream):
    logger, stream = logger_stream
    logger.warning("test warning")
    flush_handlers(logger)
    assert "test warning" in stream.getvalue()


def test_critical_log(logger_stream):
    logger, stream = logger_stream
    logger.critical("test critical")
    flush_handlers(logger)
    assert "test critical" in stream.getvalue()


def test_data_log(logger_stream):
    logger, stream = logger_stream
    logger.data({"test": "data"})
    flush_handlers(logger)
    out = stream.getvalue()
    assert "test" in out
    assert "data" in out
    assert "{" in out
    assert "}" in out


def test_error_log_and_suggestion(logger_stream):
    logger, stream = logger_stream
    try:
        obj = SuggestionTarget()
        _ = obj.valud_key  # typo on purpose
    except Exception as e:
        logger.error("lookup failed", e)
        flush_handlers(logger)
    out = stream.getvalue()
    assert "lookup failed" in out
    assert "Did you mean" in out


def test_critical_log_and_suggestion(logger_stream):
    logger, stream = logger_stream
    try:
        obj = SuggestionTarget()
        _ = obj.valud_key  # typo on purpose
    except Exception as e:
        logger.critical("lookup failed", e)
        flush_handlers(logger)
    out = stream.getvalue()
    assert "lookup failed" in out
    assert "Did you mean" in out


def test_warning_log_and_suggestion(logger_stream):
    logger, stream = logger_stream
    try:
        obj = SuggestionTarget()
        _ = obj.valud_key  # typo on purpose
    except Exception as e:
        logger.warning("lookup failed", e)
        flush_handlers(logger)
    out = stream.getvalue()
    assert "lookup failed" in out
    assert "Did you mean" in out


def test_pretty_log_with_pretty_print(logger_stream):
    logger, stream = logger_stream
    logger.data(DummyPretty())
    flush_handlers(logger)
    assert "DATA" in stream.getvalue()


def test_pretty_log_with_json(logger_stream):
    logger, stream = logger_stream
    logger.data(DummyJSON())
    flush_handlers(logger)
    assert "social_media_platform" in stream.getvalue()
    assert "3091" in stream.getvalue()


def test_pretty_log_with_fallback(logger_stream):
    logger, stream = logger_stream
    logger.cdata(1234)
    flush_handlers(logger)
    assert "1234" in stream.getvalue()


def test_header_output(logger_stream):
    logger, stream = logger_stream
    logger.header("HEADER")
    flush_handlers(logger)
    assert "Header" in stream.getvalue() or "HEADER" in stream.getvalue()


def test_log_time():
    stream = StringIO()

    logger.start_time()
    logger.add_new_handler(logging.StreamHandler, stream=stream, force_replace=True)
    time.sleep(2)
    logger.log_time("Compact Test")
    flush_handlers(logger)
    output = stream.getvalue()
    assert "Compact Test" in output
    assert "\n" not in output.strip()
    assert "->" in output


def test_compact_mode():
    stream = StringIO()

    logger.compact_mode = True
    logger.add_new_handler(logging.StreamHandler, stream=stream, force_replace=True)

    logger.info("Compact Test")
    flush_handlers(logger)
    output = stream.getvalue()
    assert "Compact Test" in output
    assert "\n" not in output.strip()
    assert "->" in output


def test_pretty_log_with_pydantic_model(logger_stream):
    logger, stream = logger_stream
    model = DummyPydantic(name="test", value=42)
    logger.data(model)
    flush_handlers(logger)
    assert "test" in stream.getvalue()
    assert "42" in stream.getvalue()


def test_pretty_log_with_pydantic_model_non_compact(logger_stream):
    logger, stream = logger_stream
    logger.compact_mode = False
    model = DummyPydantic(name="test", value=42)
    logger.data(model)
    flush_handlers(logger)
    assert "test" in stream.getvalue()
    assert "42" in stream.getvalue()


def test_run_id_format(logger_stream):
    logger, _ = logger_stream
    assert re.match(r"R-[A-F0-9]{7}", logger.run_id)


def test_initiate_new_run(logger_stream):
    logger, stream = logger_stream
    original = logger.run_id
    logger.initiate_new_run()
    logger.info("New run")
    flush_handlers(logger)
    assert original != logger.run_id
    assert "New run" in stream.getvalue()


def test_silence_logger(logger_stream):
    logger, _ = logger_stream

    # Prepare a logger WrenchCL will silence
    test_logger = logging.getLogger("test_silence")
    test_logger.setLevel(logging.DEBUG)
    test_logger.propagate = False  # Required to prevent root fallback

    test_stream = StringIO()
    stream_handler = logging.StreamHandler(test_stream)
    stream_handler.setLevel(logging.DEBUG)

    test_logger.handlers = [stream_handler]

    # Emit log before silence
    test_logger.info("Before silence")
    stream_handler.flush()
    assert "Before silence" in test_stream.getvalue()

    # Silence and assert no output
    logger.silence_logger("test_silence")

    test_stream.truncate(0)
    test_stream.seek(0)
    test_logger.info("After silence")

    assert test_stream.getvalue() == ""


def test_silence_other_loggers():
    test_loggers = []
    test_streams = []
    for i in range(3):
        s = StringIO()
        l = logging.getLogger(f"other_logger_{i}")
        l.setLevel(logging.INFO)
        l.addHandler(logging.StreamHandler(s))
        test_loggers.append(l)
        test_streams.append(s)
        l.info(f"msg {i}")
        assert f"msg {i}" in s.getvalue()
    logger.silence_other_loggers()
    for s in test_streams:
        s.truncate(0);
        s.seek(0)
    for i, l in enumerate(test_loggers):
        l.info(f"after silence {i}")
        assert f"after silence {i}" not in test_streams[i].getvalue()


def test_verbose_mode(logger_stream):
    logger, stream = logger_stream
    logger.verbose_mode = False
    logger.info("Non-verbose test")
    flush_handlers(logger)
    stream.truncate(0);
    stream.seek(0)
    logger.verbose_mode = True
    logger.info("Verbose test")
    flush_handlers(logger)
    assert "Verbose test" in stream.getvalue()


def test_set_level(logger_stream):
    logger, stream = logger_stream
    logger.setLevel("WARNING")
    logger.info("Not shown")
    logger.warning("Shown")
    flush_handlers(logger)
    out = stream.getvalue()
    assert "Shown" in out
    assert "Not shown" not in out


def test_pretty_log_highlighting_all_literals(logger_stream):
    logger, stream = logger_stream
    logger.setLevel("INFO")
    logger.verbose_mode = False

    sample = {
            "true_val": True, "false_val": False, "none_val": None, "int_val": 42,
            "string_val": "hi", "dict": {"a": 1, "b": [1, 2, {"nested": None}]}
            }

    logger.data(sample)
    flush_handlers(logger)
    out = stream.getvalue()
    forbidden = ['"true_val": true', '"false_val": false', '"none_val": null']
    assert not any(x in out for x in forbidden)


def test_simple_info_log_highlighting(logger_stream):
    logger, stream = logger_stream
    logger.warning("Simple literal test: true false none 1234 %s {name}")
    flush_handlers(logger)
    out = stream.getvalue()
    for token in ["true", "false", "none", "1234", '%s', '{', '}']:
        assert token in out
    for token in ['{name}']:
        assert token not in out


def test_log_no_syntax_highlights(logger_stream):
    logger, stream = logger_stream
    logger.configure(highlight_syntax=False)
    logger.data("Simple literal test: true false none 1234")
    flush_handlers(logger)
    assert "Simple literal test: true false none 1234" in stream.getvalue()


# def test_show_demo_string(logger_stream):
#     logger, stream = logger_stream
#     logger.configure(color_enabled=True, highlight_syntax=True, mode="terminal")
#     logger.display_logger_state()
#     flush_handlers(logger)
#     out = stream.getvalue()
#     required = ["Log Level Color Preview", "Literal/Syntax Highlight Preview"]
#     print(out)
#     assert all(x in out for x in required)


def test_color_presets():
    assert hasattr(logger, "color_presets")


def test_color_mode(logger_stream):
    logger, stream = logger_stream
    logger.color_mode = True
    logger.info("Test message A")
    logger.color_mode = False
    logger.info("Test message B")
    os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "lambda"
    logger.color_mode = True
    logger.info("Test message C")
    os.environ.pop("AWS_LAMBDA_FUNCTION_NAME")
    logger.color_mode = True
    logger.info("Test message D")
    logger.compact_mode = True
    logger.info("Test message E")
    flush_handlers(logger)
    assert "Test message" in stream.getvalue()


def test_number_highlighting_with_units_and_exclusions(logger_stream):
    logger, stream = logger_stream
    logger.configure(highlight_syntax=True, color_enabled=True)

    test_msg = (
            "Duration: 3s, 1.5sec, 2min, 4.7minutes, 95%, 2x "
            "— Invalids: Data3, abc123, uuid-1234-5678, key42"
    )
    logger.info(test_msg)
    flush_handlers(logger)
    out = stream.getvalue()

    # ✅ Highlighted tokens
    should_be_colored = ["3s", "1.5sec", "2min", "4.7minutes", "95", "2x"]
    # ❌ Should remain uncolored
    should_not_be_colored = ["Data3", "abc123", "1234", "5678", "key42"]

    ansi_pattern = re.compile(
            r'\x1b\[[\d;]+m(\d+(?:\.\d+)?(?:[a-zA-Z%]+)?)\x1b\[39m'
            )
    highlighted = [m.group(1) for m in ansi_pattern.finditer(out)]

    for val in should_be_colored:
        assert val in highlighted, f"{val} should be highlighted"

    for val in should_not_be_colored:
        assert not any(val in h for h in highlighted), f"{val} should not be highlighted"


def test_uuid_highlighting(logger_stream):
    logger, stream = logger_stream
    logger.configure(highlight_syntax=True, color_enabled=True)

    test_msg = (
            "Tracking IDs: 550e8400-e29b-41d4-a716-446655440000, "
            "not-a-uuid, 1234-5678, uuid:00000000-0000-0000-0000-000000000000"
    )
    logger.info(test_msg)
    flush_handlers(logger)

    out = stream.getvalue()
    print(repr(out))
    # Match ANSI-highlighted UUIDs
    uuid_ansi_pattern = re.compile(
            r'\x1b\[[\d;]+m([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\x1b\[(?:39|0)m',
            re.IGNORECASE
            )

    highlighted = [m.group(1) for m in uuid_ansi_pattern.finditer(out)]

    assert "550e8400-e29b-41d4-a716-446655440000" in highlighted

    assert all(x not in highlighted for x in ["not-a-uuid", "1234-5678", '00000000-0000-0000-0000-000000000000'])
