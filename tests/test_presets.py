import pytest

from helpers.context import PlaybackContext
from presets import DEFAULT_LAYOUT, DEFAULT_PLAYER, LAYOUTS, PLAYERS, make_context


def test_defaults_exist():
    assert DEFAULT_PLAYER in PLAYERS
    assert DEFAULT_LAYOUT in LAYOUTS


@pytest.mark.parametrize("player", list(PLAYERS))
def test_every_player_is_a_valid_context(player):
    assert isinstance(PLAYERS[player], PlaybackContext)


def test_dise_players_name_their_version_and_hardware():
    for name, context in PLAYERS.items():
        if name.startswith("Dise One"):
            assert (context.platform, context.dise_version) == ("dise", "one")
        elif name.startswith("Dise Premium / Lite"):
            assert (context.platform, context.dise_version) == ("dise", "legacy")


@pytest.mark.parametrize("layout", [name for name in LAYOUTS if name != "Custom size…"])
def test_fixed_layouts_set_the_canvas(layout):
    context = make_context(DEFAULT_PLAYER, layout)
    assert (context.canvas_width, context.canvas_height) == LAYOUTS[layout]
    assert context.dise_player == PLAYERS[DEFAULT_PLAYER].dise_player


def test_custom_layout_requires_a_size():
    with pytest.raises(ValueError, match="Enter a custom width and height"):
        make_context(DEFAULT_PLAYER, "Custom size…")
    context = make_context(DEFAULT_PLAYER, "Custom size…", (5760, 1080))
    assert (context.canvas_width, context.canvas_height) == (5760, 1080)


def test_custom_size_is_validated():
    with pytest.raises(ValueError):
        make_context(DEFAULT_PLAYER, "Custom size…", (0, 1080))


def test_custom_size_is_ignored_for_fixed_layouts():
    context = make_context(DEFAULT_PLAYER, "HD portrait", (5760, 1080))
    assert (context.canvas_width, context.canvas_height) == (1080, 1920)
