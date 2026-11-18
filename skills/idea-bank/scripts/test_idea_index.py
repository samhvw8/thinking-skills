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
    assert "- Parts by lens `default`: [quark-a](/bricks/quark-a.md), [quark-b](/bricks/quark-b.md)." in whole
    assert "- Linked to [Fixed-basis transform" in whole and "via [quark-a](/bricks/quark-a.md): same split." in whole
    other = (layered / "bricks" / "fixed-basis-transform.md").read_text()
    assert "- Linked to [Sparse" in other
    mid = (layered / "bricks" / "quark-b.md").read_text()
    assert "- Part of [" in mid and "- Parts by lens `default`: [string-c](/bricks/string-c.md)." in mid


def test_part_entries_carry_how_in_frontmatter(layered):
    _brick(layered, "pattern-z", "parts:\n- quark-a\n- {to: quark-b, how: judge, note: sits inside}\n")
    ix = ix_mod.build(ix_mod.load(layered))
    assert ix["parts"]["brick:pattern-z"] == ["brick:quark-a", "brick:quark-b"]
    assert ix["part_how"]["brick:pattern-z"] == {"brick:quark-b": "judge"}
    ix_mod.main([str(layered), "--write"])
    text = (layered / "bricks" / "pattern-z.md").read_text()
    assert "- Parts by lens `default`: [quark-a](/bricks/quark-a.md), [quark-b](/bricks/quark-b.md) (judge: sits inside)." in text


# --- cuts: one unit split through several lenses ---

CUTS = HERE / "fixtures" / "cuts-bank"
WHOLE = "brick:self-improve-from-own-samples"


def test_parts_grouped_by_lens_old_cut_files():
    ix = ix_mod.build(ix_mod.load(CUTS))
    assert ix["part_lenses"][WHOLE] == {
        "cost-flow": ["brick:generate-candidates", "brick:filter-bad-samples"],
        "data-path": ["brick:generate-candidates", "brick:score-samples", "brick:filter-bad-samples"],
    }
    # the distinct parts over all cuts, each once
    assert ix["parts"][WHOLE] == ["brick:generate-candidates", "brick:filter-bad-samples", "brick:score-samples"]
    # a part in two cuts of one whole is part of it once
    assert ix["part_of"]["brick:generate-candidates"] == [WHOLE]


def test_missing_lens_is_default(layered):
    ix = ix_mod.build(ix_mod.load(layered))
    assert ix["part_lenses"]["brick:sparse-overcomplete-code"] == {"default": ["brick:quark-a", "brick:quark-b"]}


def test_depth_takes_deepest_part_over_all_cuts():
    ix = ix_mod.build(ix_mod.load(CUTS))
    # score-samples (depth 1) is only in the data-path cut; the cost-flow cut alone would give depth 1
    assert ix["depth"]["brick:score-samples"] == 1
    assert ix["depth"][WHOLE] == 2


def test_view_has_one_line_per_lens_with_lens_named(tmp_path):
    bank = tmp_path / "cuts"
    shutil.copytree(CUTS, bank)
    assert ix_mod.main([str(bank), "--write"]) == 0
    assert ix_mod.main([str(bank), "--check"]) == 0
    text = (bank / "bricks" / "self-improve-from-own-samples.md").read_text()
    lines = [l for l in text.splitlines() if l.startswith("- Parts by lens ")]
    assert lines == [
        # a cut that is a lens file links the lens
        "- Parts by lens [Where does the cost go](/lenses/cost-flow.md): "
        "[generate-candidates](/bricks/generate-candidates.md) (split: most of the compute), "
        "[filter-bad-samples](/bricks/filter-bad-samples.md) (split).",
        # a cut with no lens file is named as written
        "- Parts by lens `data-path`: [generate-candidates](/bricks/generate-candidates.md) (judge), "
        "[score-samples](/bricks/score-samples.md) (split), [filter-bad-samples](/bricks/filter-bad-samples.md).",
    ]
    part = (bank / "bricks" / "generate-candidates.md").read_text()
    assert part.count("- Part of [Self-improve from own samples]") == 1


# --- lens on every operation; perspectives and operations (seeds + bank files); recipes ---

LENSB = HERE / "fixtures" / "lens-bank"
Q = "brick:answer-a-question"


@pytest.fixture(scope="module")
def lx():
    return ix_mod.build(ix_mod.load(LENSB))


def test_old_cut_and_new_lens_form_one_group(lx):
    # step-a says `cut: data-path`, step-b says `lens: data-path`: one group
    assert lx["part_lenses"][Q]["data-path"] == ["brick:step-a", "brick:step-b"]


def test_lens_wins_over_cut(lx):
    # step-c says both `lens: fault-tree` and `cut: data-path`
    assert lx["part_lenses"][Q]["fault-tree"] == ["brick:step-c"]
    assert "brick:step-c" not in lx["part_lenses"][Q]["data-path"]


def test_new_types_load_and_seed_refs_are_not_broken(lx):
    assert lx["counts"]["Perspective"] == 1 and lx["counts"]["Operation"] == 1
    # a recipe step names seed operations (split, fuse, invert) and a perspective's part names a seed perspective
    assert lx["broken_links"] == []
    assert lx["part_of"]["perspective:fault-tree"] == ["perspective:what-goes-unchecked"]
    assert lx["depth"]["operation:check-then-fuse"] == 1


def test_recipe_steps_sorted_by_order_with_repeats(lx):
    steps = lx["recipes"]["operation:check-then-fuse"]
    assert [(s["step"], s["lens"]) for s in steps] == [
        ("operation:split", "fault-tree"), ("operation:split", "what-goes-unchecked"),
        ("operation:fuse", None), ("operation:invert", "fault-tree")]
    # ordered steps are a recipe, not a lens group
    assert "operation:check-then-fuse" not in lx["part_lenses"]


def test_order_must_be_a_number(tmp_path):
    bank = tmp_path / "bad"
    (bank / "operations").mkdir(parents=True)
    (bank / "operations" / "x.md").write_text("---\ntype: Operation\ntitle: X\nparts:\n  - { to: split, order: first }\n---\n")
    with pytest.raises(SystemExit, match="order"):
        ix_mod.build(ix_mod.load(bank))


def by_id(rows):
    return {r["id"]: r for r in rows}


def test_perspective_uses_by_verb(lx):
    p = by_id(lx["perspectives"])
    # parts (split), a recipe step (split, invert) and a Mutations row (substitute-brick)
    assert p["fault-tree"]["uses"] == {
        "split": [Q, "operation:check-then-fuse"],
        "invert": ["operation:check-then-fuse"],
        "substitute-brick": ["card:toy-card"]}
    assert p["fault-tree"]["seed"] and p["fault-tree"]["status"] == "tested"
    assert p["guarantee-chain"]["uses"] == {"fuse": ["brick:fused-check"]}
    assert p["what-goes-unchecked"]["file"] and not p["what-goes-unchecked"]["seed"]
    # seeds come first, in the seed file's order; the owner's fear-first seed leads
    assert lx["perspectives"][0]["id"] == "fault-tree"


def test_join_and_old_bind_are_one_verb(lx):
    o = by_id(lx["operations"])
    assert o["join"]["uses"] == {"cost-share": ["brick:joined-pipeline"]}
    assert "bind" not in o


def test_fuse_records_lens(lx):
    o = by_id(lx["operations"])
    assert o["fuse"]["uses"] == {"guarantee-chain": ["brick:fused-check"], "no lens": ["operation:check-then-fuse"]}


def test_move_and_mutation_rows_carry_lens(lx):
    o = by_id(lx["operations"])
    assert o["invert"]["uses"] == {"fault-tree": ["operation:check-then-fuse"], "what-could-break": ["move:invert-the-check"]}
    # a backticked operator and a `-` lens cell are read as plain values
    assert o["remove"]["uses"] == {"no lens": ["card:toy-card"]}
    # judge and owner say who found a part, not which operation made it
    assert "judge" not in o and not any(f["label"] == "judge" for f in lx["free_operations"])


def test_free_labels_and_recurrence(lx):
    free = {f["label"]: f for f in lx["free_lenses"]}
    assert set(free) == {"cost-share", "data-path", "what-could-break"}
    assert free["what-could-break"]["recurs"] and free["what-could-break"]["files"] == 2
    assert free["what-could-break"]["uses"] == {"part": [Q], "invert": ["move:invert-the-check"]}
    assert not free["cost-share"]["recurs"]
    assert [f["label"] for f in lx["free_operations"]] == ["merge-sideways"]


def test_report_lists_seeds_and_bank_files_together():
    text = ix_mod.render(ix_mod.build(ix_mod.load(LENSB)))
    assert "## Perspectives (seeds and bank files" in text
    assert "- what-goes-unchecked (bank file, invented): for split: operation:check-then-fuse" in text
    assert ("- check-then-fuse (bank file, invented, recipe: split through fault-tree, split through "
            "what-goes-unchecked, fuse, invert through fault-tree): not used yet") in text
    assert "- what-could-break: for invert: move:invert-the-check; for part: brick:answer-a-question -- RECURS in 2 files" in text


def test_views_for_new_types_write_twice_then_check(tmp_path):
    bank = tmp_path / "lens"
    shutil.copytree(LENSB, bank)
    assert ix_mod.main([str(bank), "--write"]) == 0
    first = {p: p.read_text() for p in bank.rglob("*.md")}
    assert ix_mod.main([str(bank), "--write"]) == 0
    assert {p: p.read_text() for p in bank.rglob("*.md")} == first
    assert ix_mod.main([str(bank), "--check"]) == 0
    op = (bank / "operations" / "check-then-fuse.md").read_text()
    assert ("- Steps in order: 1. `split` through `fault-tree`; 2. `split` through "
            "[What goes unchecked](/perspectives/what-goes-unchecked.md); 3. `fuse`; 4. `invert` through `fault-tree`.") in op
    per = (bank / "perspectives" / "what-goes-unchecked.md").read_text()
    assert "- Used for `split` on [Check then fuse](/operations/check-then-fuse.md)." in per
    # a part that is a seed perspective has no file, so it is named, not linked
    assert "- Parts by lens `default`: `fault-tree` (split: a narrower form of it)." in per
    q = (bank / "bricks" / "answer-a-question.md").read_text()
    assert "- Parts by lens `data-path`: [Step a](/bricks/step-a.md) (split), [Step b](/bricks/step-b.md) (split)." in q
