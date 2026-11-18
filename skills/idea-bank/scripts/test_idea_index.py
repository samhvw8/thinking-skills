"""Tests for idea_index.py. Run: uv run --with pytest --with pyyaml pytest <this dir>"""
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("idea_index", HERE / "idea_index.py")
ix_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ix_mod)
BANK = HERE / "fixtures" / "bank"


@pytest.fixture(scope="module")
def ix():
    return ix_mod.build(ix_mod.load(BANK))


def test_counts(ix):
    assert ix["counts"] == {"Brick": 2, "Idea Card": 6, "Move": 3, "Reading": 1, "State": 1}


def test_broken_link_found(ix):
    assert {"from": "card:sae-features", "to": "brick:relu-encoder"} in ix["broken_links"]
    assert len(ix["broken_links"]) == 1


def test_one_way_link(ix):
    # sae-features lists the brick, the brick does not list the card
    assert {"from": "card:sae-features", "to": "brick:sparse-overcomplete-code"} in ix["one_way_links"]


def test_links_are_bidirectional_union(ix):
    assert ix["links"]["sparse-overcomplete-code"] == ["ksvd-2006", "olshausen-field-1996", "sae-features"]


def test_migrations_widen_fields(ix):
    top = ix["bricks_by_field_count"][0]
    assert top["brick"] == "sparse-overcomplete-code"
    assert top["fields"] == ["interpretability", "machine-learning", "mechanistic-interpretability", "neuroscience"]


def test_convergence_on_unrelated_fields(ix):
    roles = {c["role"]: c for c in ix["convergence"]}
    assert "sparse-represent-signal" in roles
    assert roles["sparse-represent-signal"]["unrelated_pairs"] == [["fixed-basis-transform", "sparse-overcomplete-code"]]


def test_hot_slot(ix):
    assert ix["hot_slots"] == [{"role": "sparse-represent-signal", "moves": ["fixed-to-learned-basis", "learned-basis-ksvd"]}]


def test_migration_gap_candidates(ix):
    gaps = {(g["brick"], g["field"]) for g in ix["migration_gap_candidates"]}
    assert gaps == {("fixed-basis-transform", "genomics"), ("sparse-overcomplete-code", "genomics")}


def test_no_gap_inside_reached_field(ix):
    assert all(g["field"] not in g["brick_fields"] for g in ix["migration_gap_candidates"])


def test_known_bricks(ix):
    k = ix["known_bricks"]
    assert k["owned"] == ["fixed-basis-transform"]
    assert k["unknown_slugs"] == ["ghost-brick"]
    assert k["owned_share"] == 0.5


def test_bad_frontmatter_crashes(tmp_path):
    (tmp_path / "bad.md").write_text("no frontmatter here\n")
    with pytest.raises(SystemExit):
        ix_mod.load(tmp_path)


def test_cli_json(tmp_path, capsys):
    out = tmp_path / "ix.json"
    assert ix_mod.main([str(BANK), "--json", str(out)]) == 0
    assert json.loads(out.read_text())["hot_slots"]
    assert "Migration-gap candidates" in capsys.readouterr().out


def test_migrate_brick_moves_widen_fields_but_not_hot_slots(ix):
    assert ix["migrate_brick_moves"] == [{"move": "sparse-code-to-sae", "brick": "sparse-overcomplete-code",
                                         "from_field": "neuroscience", "to_field": "mechanistic-interpretability"}]
    assert [h["role"] for h in ix["hot_slots"]] == ["sparse-represent-signal"]
    assert len(ix["hot_slots"][0]["moves"]) == 2


def test_low_confidence_listed(ix):
    assert ix["low_confidence_matches"] == [{"brick": "sparse-overcomplete-code", "field": "machine-learning",
                                             "source": "ksvd-2006", "role": "denoise-signal"}]


def test_constraints_index(ix):
    assert ix["constraints"] == {"compute-per-pixel-cost": ["jpeg"], "trial-length": ["sleep-gate"]}
    assert ix["evidence_limits"] == {"no-control-group": ["sleep-gate"]}


def test_level3_hints_counted(ix):
    assert ix["reading_hints"] == [{"reading": "261102-sae", "mode": "deep", "level3_hints": 1, "notes": 3}]


def test_suggest_merges_finds_near_duplicates():
    rows = ix_mod.suggest_merges(ix_mod.load(BANK))
    pairs = {(r["a"], r["b"]) for r in rows}
    assert ("sparse-represent-signal", "sparse-represent-signals") in pairs   # tension vs role, plural
    assert ("consolidate-after-signal", "gate-consolidation-by-sleep") not in pairs  # different words
    for r in rows:
        assert r["a"] < r["b"]


def test_suggest_merges_ignores_unrelated_roles():
    rows = ix_mod.suggest_merges(ix_mod.load(BANK))
    # explain-receptive-fields and decompose-activations share no words: never suggested
    assert all({r["a"], r["b"]} != {"decompose-activations", "explain-receptive-fields"} for r in rows)


def test_cli_suggest_merges(capsys):
    assert ix_mod.main([str(BANK), "--suggest-merges"]) == 0
    assert "Merge suggestions" in capsys.readouterr().out


# --- generated views (--write / --check) ---

import shutil


@pytest.fixture
def bank_copy(tmp_path):
    dst = tmp_path / "bank"
    shutil.copytree(BANK, dst, symlinks=False)
    return dst


def test_check_reports_stale_then_write_fixes_it(bank_copy):
    assert ix_mod.main([str(bank_copy), "--check"]) == 1
    assert ix_mod.main([str(bank_copy), "--write"]) == 0
    assert ix_mod.main([str(bank_copy), "--check"]) == 0


def test_write_is_idempotent(bank_copy):
    ix_mod.main([str(bank_copy), "--write"])
    before = {p: p.read_text() for p in bank_copy.rglob("*.md")}
    assert ix_mod.sync_views(bank_copy, write=True) == []
    assert before == {p: p.read_text() for p in bank_copy.rglob("*.md")}


def test_signature_moves_from_frontmatter_to_body(bank_copy):
    ix_mod.main([str(bank_copy), "--write"])
    text = (bank_copy / "bricks" / "sparse-overcomplete-code.md").read_text()
    fm, body = ix_mod.FM_RE.match(text).groups()
    assert "signature" not in fm
    assert "# Signature\n- **Input:** signal\n- **Output:** sparse coefficients" in body
    # the rest of the frontmatter is untouched text, and still parses
    assert "roles: [sparse-represent-signal]" in fm
    assert ix_mod.build(ix_mod.load(bank_copy))["counts"]["Brick"] == 2


def test_related_links_both_directions(bank_copy):
    ix_mod.main([str(bank_copy), "--write"])
    brick = (bank_copy / "bricks" / "sparse-overcomplete-code.md").read_text()
    # sae-features lists the brick but the brick does not list the card: the view still shows it
    assert "](/cards/sae-features.md) (" in brick  # bank outside a bundle: links are bank-root relative
    assert "Shares role `sparse-represent-signal` with [" in brick and "fixed-basis-transform.md)" in brick
    assert "explain-receptive-fields" in brick  # role taken from the migration row of that card
    card = (bank_copy / "cards" / "sae-features.md").read_text()
    assert "- Brick `relu-encoder` (no file yet)." in card  # broken link is shown, not hidden
    move = (bank_copy / "moves" / "sparse-code-to-sae.md").read_text()
    assert "- Brick moved [" in move


def test_hand_text_outside_block_survives(bank_copy):
    p = bank_copy / "cards" / "jpeg.md"
    ix_mod.main([str(bank_copy), "--write"])
    p.write_text(p.read_text() + "\nA note the owner added after the block.\n")
    ix_mod.main([str(bank_copy), "--write"])
    text = p.read_text()
    assert "A note the owner added after the block." in text
    assert text.count(ix_mod.REL_BEGIN) == 1 and text.rstrip().endswith(ix_mod.REL_END)


def test_bricks_index_lists_shared_roles(bank_copy):
    ix_mod.main([str(bank_copy), "--write"])
    idx = (bank_copy / "bricks" / "index.md").read_text()
    assert "## Shared roles" in idx
    shared = idx.split("## All bricks")[0]
    assert "`sparse-represent-signal` - [Fixed-basis transform" in shared
    assert "`denoise-signal`" not in shared  # one brick only
    assert idx.count("](sparse-overcomplete-code.md)") == 2  # once under the shared role, once in the full list


def test_link_prefix_inside_and_outside_bundle(tmp_path):
    (tmp_path / "index.md").write_text("---\nokf_version: '0.2'\n---\n# B\n")
    (tmp_path / "ideas").mkdir()
    assert ix_mod.link_prefix(tmp_path / "ideas") == "/ideas"
    assert ix_mod.link_prefix(tmp_path) == ""


# --- parts (split / bind) and links (connect without merging) ---

def _brick(root, slug, extra=""):
    (root / "bricks" / f"{slug}.md").write_text(
        f"---\ntype: Brick\ntitle: {slug}\ndescription: d\nroles: [r-{slug}]\nfields: []\n{extra}---\n\n# Signature\n- **Input:** x\n")


@pytest.fixture
def layered(bank_copy):
    # string-c -> quark-b -> sparse-overcomplete-code; quark-a -> sparse-overcomplete-code
    _brick(bank_copy, "string-c")
    _brick(bank_copy, "quark-b", "parts: [string-c]\n")
    _brick(bank_copy, "quark-a")
    p = bank_copy / "bricks" / "sparse-overcomplete-code.md"
    p.write_text(p.read_text().replace("type: Brick\n", "type: Brick\nparts: [quark-a, quark-b]\n"
                                       "links:\n- {to: fixed-basis-transform, via: quark-a, note: same split}\n", 1))
    return bank_copy


def test_parts_depth_is_relative(layered):
    ix = ix_mod.build(ix_mod.load(layered))
    assert ix["parts"]["brick:sparse-overcomplete-code"] == ["brick:quark-a", "brick:quark-b"]
    assert ix["part_of"]["brick:string-c"] == ["brick:quark-b"]
    # a part can have parts of its own: depth is computed, never stored
    assert ix["depth"] == {"brick:string-c": 0, "brick:quark-a": 0, "brick:quark-b": 1, "brick:sparse-overcomplete-code": 2}
    assert ix["part_cycles"] == []


def test_part_refs_resolve_across_types(layered):
    _brick(layered, "pattern-x", "parts: ['card:jpeg', quark-a]\n")
    ix = ix_mod.build(ix_mod.load(layered))
    assert ix["parts"]["brick:pattern-x"] == ["card:jpeg", "brick:quark-a"]


def test_broken_part_and_via_are_reported(layered):
    _brick(layered, "pattern-y", "parts: [ghost]\nlinks: [{to: quark-a, via: nowhere}]\n")
    ix = ix_mod.build(ix_mod.load(layered))
    assert {"from": "brick:pattern-y", "to": "part:ghost"} in ix["broken_links"]
    assert {"from": "brick:pattern-y", "to": "via:nowhere"} in ix["broken_links"]


def test_part_cycle_reported_not_crashing(layered):
    p = layered / "bricks" / "string-c.md"
    p.write_text(p.read_text().replace("fields: []\n", "fields: []\nparts: [quark-b]\n"))
    ix = ix_mod.build(ix_mod.load(layered))
    assert ix["part_cycles"] and set(ix["part_cycles"][0]) == {"brick:quark-b", "brick:string-c"}


def test_unit_links_both_directions(layered):
    ix = ix_mod.build(ix_mod.load(layered))
    assert ix["unit_links"] == [{"a": "brick:sparse-overcomplete-code", "b": "brick:fixed-basis-transform",
                                 "via": "brick:quark-a", "note": "same split"}]


def test_views_show_parts_part_of_and_links(layered):
    ix_mod.main([str(layered), "--write"])
    whole = (layered / "bricks" / "sparse-overcomplete-code.md").read_text()
    assert "- Parts (no cut recorded): [quark-a](/bricks/quark-a.md), [quark-b](/bricks/quark-b.md)." in whole
    assert "- Linked to [Fixed-basis transform" in whole and "via [quark-a](/bricks/quark-a.md): same split." in whole
    other = (layered / "bricks" / "fixed-basis-transform.md").read_text()
    assert "- Linked to [Sparse" in other
    mid = (layered / "bricks" / "quark-b.md").read_text()
    assert "- Part of [" in mid and "- Parts (no cut recorded): [string-c](/bricks/string-c.md)." in mid
    assert "- Part of [Sparse" in mid and "(cut" not in mid  # an unlabelled part names no cut


def test_part_entries_carry_how_in_frontmatter(layered):
    _brick(layered, "pattern-z", "parts:\n- quark-a\n- {to: quark-b, how: judge, note: sits inside}\n")
    ix = ix_mod.build(ix_mod.load(layered))
    assert ix["parts"]["brick:pattern-z"] == ["brick:quark-a", "brick:quark-b"]
    assert ix["cut_how"]["brick:pattern-z"] == {"unlabelled": {"brick:quark-b": "judge"}}
    ix_mod.main([str(layered), "--write"])
    text = (layered / "bricks" / "pattern-z.md").read_text()
    assert "- Parts (no cut recorded): [quark-a](/bricks/quark-a.md), [quark-b](/bricks/quark-b.md) (judge: sits inside)." in text


# --- cuts: one unit split by several kinds of cut (scissors), and bound (tape) ---

CUTS = HERE / "fixtures" / "cuts-bank"
WHOLE = "brick:self-improve-from-own-samples"


@pytest.fixture
def cuts_copy(tmp_path):
    dst = tmp_path / "cuts"
    shutil.copytree(CUTS, dst)
    return dst


def test_parts_grouped_by_cut():
    ix = ix_mod.build(ix_mod.load(CUTS))
    assert ix["part_cuts"][WHOLE] == {
        "cost": ["brick:generate-candidates", "brick:filter-bad-samples"],
        "data-flow": ["brick:generate-candidates", "brick:score-samples", "brick:filter-bad-samples"],
    }
    # the distinct parts over all cuts, each once
    assert ix["parts"][WHOLE] == ["brick:generate-candidates", "brick:filter-bad-samples", "brick:score-samples"]
    # a part in two cuts of one whole is part of it once, and the cuts are named
    assert ix["part_of_cuts"]["brick:generate-candidates"][WHOLE] == ["cost", "data-flow"]


def test_how_is_kept_per_cut_in_json():
    ix = ix_mod.build(ix_mod.load(CUTS))
    # found by splitting under one cut and by a judge under another: both kept
    assert ix["cut_how"][WHOLE]["cost"]["brick:generate-candidates"] == "split"
    assert ix["cut_how"][WHOLE]["data-flow"]["brick:generate-candidates"] == "judge"
    assert "brick:filter-bad-samples" not in ix["cut_how"][WHOLE]["data-flow"]  # no how written
    assert "part_how" not in ix


def test_missing_cut_is_unlabelled(layered):
    ix = ix_mod.build(ix_mod.load(layered))
    assert ix["part_cuts"]["brick:sparse-overcomplete-code"] == {"unlabelled": ["brick:quark-a", "brick:quark-b"]}
    assert ix["cuts"]["unlabelled_wholes"] == ["brick:quark-b", "brick:sparse-overcomplete-code"]
    assert ix["cuts"]["labels"] == {}  # unlabelled is not a label


def test_depth_takes_deepest_part_over_all_cuts():
    ix = ix_mod.build(ix_mod.load(CUTS))
    # score-samples (depth 1) is only in the data-flow cut; the cost cut alone would give depth 1
    assert ix["depth"]["brick:score-samples"] == 1
    assert ix["depth"][WHOLE] == 2


def test_view_has_one_line_per_cut_with_cut_named(cuts_copy):
    assert ix_mod.main([str(cuts_copy), "--write"]) == 0
    assert ix_mod.main([str(cuts_copy), "--check"]) == 0
    text = (cuts_copy / "bricks" / "self-improve-from-own-samples.md").read_text()
    lines = [l for l in text.splitlines() if l.startswith("- Parts by cut ")]
    assert lines == [
        "- Parts by cut `cost`: [generate-candidates](/bricks/generate-candidates.md) (split: most of the compute), "
        "[filter-bad-samples](/bricks/filter-bad-samples.md) (split).",
        "- Parts by cut `data-flow`: [generate-candidates](/bricks/generate-candidates.md) (judge), "
        "[score-samples](/bricks/score-samples.md) (split), [filter-bad-samples](/bricks/filter-bad-samples.md).",
    ]
    part = (cuts_copy / "bricks" / "generate-candidates.md").read_text()
    # "Part of" names the cuts the part belongs under
    assert "- Part of [Self-improve from own samples](/bricks/self-improve-from-own-samples.md) (cuts `cost`, `data-flow`)." in part
    assert "- Part of [Generate, then keep the good ones](/bricks/generate-then-filter.md) (cut `functional`)." in part


# --- the cut registry and the Cuts report ---

def test_registry_holds_decompositions_and_idea_cuts():
    reg = ix_mod.load_registry()
    for i in ("functional", "temporal", "data-flow", "risk", "failure-mode", "constraint", "value-chain",
              "cost", "causal-chain", "evidence-role"):
        assert i in reg
    assert ix_mod.CUTS_FILE.parent.name == "references"  # read from this skill's own built copy


def test_registry_id_clash_crashes(tmp_path):
    f = tmp_path / "cuts.json"
    f.write_text(json.dumps({"decompositions": [{"id": "cost", "name": "A", "how": "x"}],
                             "cuts": [{"id": "cost", "name": "B", "how": "y"}]}))
    with pytest.raises(SystemExit):
        ix_mod.load_registry(f)
    with pytest.raises(SystemExit):
        ix_mod.load_registry(tmp_path / "missing.json")


def test_cuts_report_counts_registry_labels():
    cu = ix_mod.build(ix_mod.load(CUTS))["cuts"]
    assert cu["labels"] == {"cost": {"wholes": 1, "parts": 2, "registry": True},
                            "data-flow": {"wholes": 1, "parts": 3, "registry": True},
                            "functional": {"wholes": 1, "parts": 2, "registry": True}}
    assert cu["unregistered"] == [] and cu["near_duplicates"] == []


# Labels the review found drifting in real runs: one view, several spellings.
DRIFT = ["data-path", "goal-path", "measurement-path", "compute-cost", "cost-terms", "cost-flow", "causal",
         "lens:cost-flow", "score-samples"]


def test_cuts_report_flags_drift_and_unregistered_labels(cuts_copy):
    parts = "".join(f"  - {{ to: generate-candidates, how: split, cut: '{c}' }}\n" for c in DRIFT)
    _brick(cuts_copy, "drifty", "parts:\n" + parts)
    cu = ix_mod.build(ix_mod.load(cuts_copy))["cuts"]
    pairs = {(n["a"], n["b"]) for n in cu["near_duplicates"]}
    for pair in [("data-flow", "data-path"), ("data-path", "goal-path"), ("data-path", "measurement-path"),
                 ("goal-path", "measurement-path"), ("compute-cost", "cost"), ("cost", "cost-terms"),
                 ("cost", "cost-flow"), ("causal", "causal-chain")]:
        assert pair in pairs, pair
    # two registry kinds are never flagged against each other
    assert ("cost", "value-chain") not in pairs
    # a prefixed label and a label that names a brick are not cut kinds
    assert {"lens:cost-flow", "score-samples", "data-path"} <= set(cu["unregistered"])
    assert "cost" not in cu["unregistered"]


def test_cli_cuts_lists_registry_with_questions(capsys):
    assert ix_mod.main([str(CUTS), "--cuts"]) == 0
    out = capsys.readouterr().out
    assert "- cost: Decompose by where the cost goes" in out
    assert "- data-flow (NOT" not in out and "- data-flow: 1 whole(s)" in out


def test_cli_prints_cuts_report(capsys):
    assert ix_mod.main([str(CUTS)]) == 0
    out = capsys.readouterr().out
    assert "## Cuts" in out and "- registry: " in out and "causal-chain" in out
    assert "- in use: data-flow (registry): 1 whole(s), 3 part(s)" in out
    assert "- bound (how: bind): brick:generate-then-filter under functional" in out


# --- tape: a bigger brick bound from existing bricks ---

def test_bind_records_a_whole_made_from_existing_bricks(cuts_copy):
    ix = ix_mod.build(ix_mod.load(cuts_copy))
    w = "brick:generate-then-filter"
    assert ix["parts"][w] == ["brick:generate-candidates", "brick:filter-bad-samples"]
    assert ix["cuts"]["binds"] == {w: ["functional"]}
    assert ix["cut_how"][w]["functional"]["brick:filter-bad-samples"] == "bind"
    assert w in ix["part_of"]["brick:generate-candidates"]
    ix_mod.main([str(cuts_copy), "--write"])
    text = (cuts_copy / "bricks" / "generate-then-filter.md").read_text()
    assert ("- Parts by cut `functional`: [generate-candidates](/bricks/generate-candidates.md) (bind: recurs in two sources), "
            "[filter-bad-samples](/bricks/filter-bad-samples.md) (bind).") in text


# --- the card points to its method brick; its Recipe renders one cut ---

def test_card_method_and_recipe_in_step(cuts_copy):
    ix = ix_mod.build(ix_mod.load(cuts_copy))
    assert ix["cards_without_method"] == []
    assert ix["recipe_drift"] == []
    assert "self-training-card" in ix["links"]["self-improve-from-own-samples"]  # method counts as a card brick
    assert ix["one_way_links"] == [] and ix["broken_links"] == []
    ix_mod.main([str(cuts_copy), "--write"])
    card = (cuts_copy / "cards" / "self-training-card.md").read_text()
    assert "- Method brick [Self-improve from own samples](/bricks/self-improve-from-own-samples.md)." in card
    assert card.count("self-improve-from-own-samples.md") == 1  # not listed again as a plain brick
    whole = (cuts_copy / "bricks" / "self-improve-from-own-samples.md").read_text()
    assert "- Method of [Self-training card](/cards/self-training-card.md)." in whole


def test_recipe_out_of_step_is_reported(cuts_copy):
    p = cuts_copy / "cards" / "self-training-card.md"
    p.write_text(p.read_text().replace("Cut: `data-flow`", "Cut: cost"))
    d = ix_mod.build(ix_mod.load(cuts_copy))["recipe_drift"]
    assert d == [{"card": "self-training-card", "method": "self-improve-from-own-samples", "cut": "cost",
                  "only_in_recipe": ["score-samples"], "only_in_parts": []}]
    p.write_text(p.read_text().replace("Cut: cost\n", ""))
    assert ix_mod.build(ix_mod.load(cuts_copy))["recipe_drift"][0]["cut"] is None


def test_missing_method_brick_is_a_broken_link(cuts_copy):
    p = cuts_copy / "cards" / "self-training-card.md"
    p.write_text(p.read_text().replace("method: self-improve-from-own-samples", "method: no-such-method"))
    ix = ix_mod.build(ix_mod.load(cuts_copy))
    assert {"from": "card:self-training-card", "to": "brick:no-such-method"} in ix["broken_links"]


def test_older_cards_without_method_still_index(ix):
    # the fixture bank keeps the older shape: no method, Recipe table with no Cut line
    assert ix["cards_without_method"] == ["gene-programs", "jpeg", "ksvd-2006", "olshausen-field-1996",
                                          "sae-features", "sleep-gate"]
    assert ix["recipe_drift"] == []


# --- edge cases the review listed ---

def test_cycle_that_closes_only_across_two_cuts(cuts_copy):
    # generate-candidates contains the whole under one cut; the whole contains it under another
    p = cuts_copy / "bricks" / "generate-candidates.md"
    p.write_text(p.read_text().replace("cards: [self-training-card]\n",
                                       "cards: [self-training-card]\nparts:\n  - { to: self-improve-from-own-samples, cut: temporal }\n"))
    cyc = ix_mod.build(ix_mod.load(cuts_copy))["part_cycles"]
    assert any(set(c) == {WHOLE, "brick:generate-candidates"} for c in cyc)


def test_same_part_twice_in_one_cut_counts_once(cuts_copy):
    _brick(cuts_copy, "twice", "parts:\n  - { to: score-samples, how: split, cut: cost }\n"
                               "  - { to: score-samples, how: judge, cut: cost }\n")
    ix = ix_mod.build(ix_mod.load(cuts_copy))
    assert ix["part_cuts"]["brick:twice"] == {"cost": ["brick:score-samples"]}
    assert ix["cut_how"]["brick:twice"]["cost"] == {"brick:score-samples": "split"}  # the first entry wins
    assert ix["cuts"]["labels"]["cost"]["parts"] == 3


# --- re-cuts: a later cut must draw a new boundary; the card compares the cuts in one table ---

def _add_parts(root, slug, lines, extra=""):
    """Append entries to the end of a brick's block-style `parts` (its last frontmatter key), as a re-cut does."""
    p = root / "bricks" / f"{slug}.md"
    head, sep, body = p.read_text()[4:].partition("\n---\n")
    assert head.splitlines()[-1].startswith("  - ")  # parts is the last key
    p.write_text("---\n" + extra + head + "".join(f"\n  - {l}" for l in lines) + sep + body)


def test_recut_report_shows_overlap_and_new_parts():
    r = ix_mod.build(ix_mod.load(CUTS))["recuts"]
    assert [w["whole"] for w in r] == [WHOLE]
    cost, flow = r[0]["cuts"]
    assert cost["cut"] == "cost" and cost["overlap"] == {"data-flow": {"shared": 2, "of": 2, "pct": 100}}
    assert cost["retag_of"] == [] and not cost["no_new_boundary"]  # the first cut is the base
    assert flow["new_parts"] == ["brick:score-samples"] and flow["overlap"]["cost"]["pct"] == 67
    assert flow["retag_of"] == [] and not flow["no_new_boundary"]


def test_recut_that_only_retags_is_flagged(cuts_copy, capsys):
    _add_parts(cuts_copy, "self-improve-from-own-samples", [
        "{ to: generate-candidates, how: split, cut: question, group: 'what can we try?' }",
        "{ to: filter-bad-samples, how: split, cut: question, group: 'what do we keep?' }"])
    q = ix_mod.build(ix_mod.load(cuts_copy))["recuts"][0]["cuts"][-1]
    assert q["cut"] == "question" and q["retag_of"] == ["cost", "data-flow"] and q["no_new_boundary"]
    assert q["overlap"]["data-flow"] == {"shared": 2, "of": 2, "pct": 100}
    assert ix_mod.main([str(cuts_copy), "--recuts"]) == 0
    out = capsys.readouterr().out
    assert "`question` (2 parts): shares 2/2 (100%) with `cost`" in out
    assert "RE-TAG of `cost`, `data-flow`: all its parts are parts of that cut" in out


def test_recut_that_cuts_a_part_again_is_a_new_boundary(cuts_copy):
    _add_parts(cuts_copy, "self-improve-from-own-samples", ["{ to: score-samples, how: split, cut: question }",
                                                            "{ to: filter-bad-samples, how: split, cut: question }"])
    _brick(cuts_copy, "pick-a-reference")
    sc = cuts_copy / "bricks" / "score-samples.md"
    sc.write_text(sc.read_text().replace("parts: [compare-to-reference]", "parts:\n  - compare-to-reference\n"
                                         "  - { to: pick-a-reference, how: split, cut: question }"))
    r = {w["whole"]: w["cuts"] for w in ix_mod.build(ix_mod.load(cuts_copy))["recuts"]}
    q = r[WHOLE][-1]
    assert q["parts_cut_again"] == ["brick:score-samples"] and q["retag_of"] == [] and not q["no_new_boundary"]


def test_recut_mixing_parts_of_two_cuts_draws_no_boundary(cuts_copy):
    for s in ("x", "y", "z"):
        _brick(cuts_copy, s)
    _brick(cuts_copy, "mixed", "parts:\n  - { to: x, cut: cost }\n  - { to: y, cut: cost }\n"
                               "  - { to: y, cut: risk }\n  - { to: z, cut: risk }\n"
                               "  - { to: x, cut: temporal }\n  - { to: z, cut: temporal }\n")
    r = {w["whole"]: w for w in ix_mod.build(ix_mod.load(cuts_copy))["recuts"]}["brick:mixed"]["cuts"]
    assert r[1]["new_parts"] == ["brick:z"] and not r[1]["no_new_boundary"]
    assert r[2]["retag_of"] == [] and r[2]["no_new_boundary"]  # x and z both came earlier, from two cuts


def _question_cut(root):
    _brick(root, "samples-match-target")
    _add_parts(root, "self-improve-from-own-samples", [
        "{ to: compare-to-reference, how: split, cut: question, group: 'is it good?' }",
        "{ to: generate-then-filter, how: bind, cut: question, group: 'what do we keep?' }",
        "{ to: samples-match-target, how: split, cut: question, group: 'what must hold? | assumed' }"],
        "cuts:\n  - { cut: question, angle: what question each part answers, shows: only the check needs a reference }\n")


def test_card_gets_one_table_comparing_the_cuts(cuts_copy):
    _question_cut(cuts_copy)
    assert ix_mod.main([str(cuts_copy), "--write"]) == 0
    assert ix_mod.main([str(cuts_copy), "--check"]) == 0
    card = (cuts_copy / "cards" / "self-training-card.md").read_text()
    rows = [l for l in card.splitlines() if l.startswith("| ") and "Signature" not in l and "(inferred)" not in l]
    gtf = "Generate, then keep the good ones"
    assert rows == [
        "| Piece | `data-flow` (Recipe) | `cost` | `question` |",
        f"| [generate-candidates](/bricks/generate-candidates.md) | make samples | part | inside {gtf} |",
        "| [score-samples](/bricks/score-samples.md) | score them | - | spans compare-to-reference |",
        f"| [filter-bad-samples](/bricks/filter-bad-samples.md) | keep the good ones | part | inside {gtf} |",
        "| [compare-to-reference](/bricks/compare-to-reference.md) | inside score-samples | - | is it good? |",
        f"| [{gtf}](/bricks/generate-then-filter.md) | spans generate-candidates, filter-bad-samples "
        "| spans generate-candidates, filter-bad-samples | what do we keep? |",
        "| [samples-match-target](/bricks/samples-match-target.md) | - | - | what must hold? \\| assumed |",
    ]
    assert "- `question` (asked: what question each part answers): only the check needs a reference" in card
    assert "- `cost`: not written yet" in card
    # the table sits right after the Recipe section, before the next section and the Related block
    assert card.index("Operator: sequence") < card.index("# Cuts compared") < card.index("# Related")
    assert card.count("self-improve-from-own-samples.md") == 1  # the table does not link the method again


def test_cut_table_is_idempotent_and_leaves_hand_text(cuts_copy):
    p = cuts_copy / "cards" / "self-training-card.md"
    p.write_text(p.read_text() + "\n# Raw\nRe-read for cut question: Methods 2.1\n")
    _question_cut(cuts_copy)
    ix_mod.main([str(cuts_copy), "--write"])
    once = p.read_text()
    ix_mod.main([str(cuts_copy), "--write"])
    assert p.read_text() == once
    assert once.index("# Cuts compared") < once.index("# Raw") < once.index("# Related")
    assert "Re-read for cut question: Methods 2.1" in once


def test_cut_table_needs_two_cuts(cuts_copy):
    ix_mod.main([str(cuts_copy), "--write"])
    p = cuts_copy / "cards" / "self-training-card.md"
    assert "# Cuts compared" in p.read_text()  # the fixture's method has a cost and a data-flow cut
    b = cuts_copy / "bricks" / "self-improve-from-own-samples.md"
    b.write_text("".join(l for l in b.read_text().splitlines(True) if "cut: cost" not in l))
    ix_mod.main([str(cuts_copy), "--write"])
    text = p.read_text()
    assert "# Cuts compared" not in text and "cuts:begin" not in text and "Operator: sequence\n\n<!-- related" in text
