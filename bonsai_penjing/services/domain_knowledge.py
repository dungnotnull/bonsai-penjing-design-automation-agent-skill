"""
Bonsai & Penjing domain knowledge base — species profiles, form matching logic,
pruning physiology rules, wiring guidelines, and rock composition templates.
This is the authoritative, hardcoded domain knowledge that drives core-analysis.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# --- Species profiles ---
SPECIES_PROFILES: Dict[str, Dict[str, Any]] = {
    "juniper": {
        "scientific": "Juniperus chinensis / Juniperus procumbens",
        "common_names": ["juniper", "juniperus", "shimpaku", "tùng", "bách xù"],
        "water": "Allow soil surface to dry slightly between watering. Mist foliage daily. Reduce watering in winter.",
        "soil": {"akadama": 40, "pumice": 30, "lava_rock": 30},
        "repot_years": 2,
        "fertilisation": "Balanced 7-7-7 every 2 weeks during growth. Low nitrogen in autumn.",
        "pests": ["spider mites", "juniper scale", "cedar-apple rust", "phomopsis blight"],
        "seasonal": {
            "spring": "Major pruning and repotting window. Begin fertilisation after new growth hardens.",
            "summer": "Pinch new growth to maintain shape. Watch for spider mites in hot dry weather.",
            "autumn": "Structural pruning possible. Reduce nitrogen. Prepare for winter protection.",
            "winter": "Protect from hard freeze. Reduce watering. No fertilisation.",
        },
        "pruning_timing": "Major structural pruning: late winter to early spring. Pinching: throughout growing season.",
        "wiring_notes": "Wire in autumn/winter. Juniper bark marks easily — use raffia on thick bends. Remove wire after 6-9 months.",
        "apical_dominance": "moderate",
    },
    "pine": {
        "scientific": "Pinus thunbergii / Pinus sylvestris / Pinus parviflora",
        "common_names": ["pine", "thông", "black pine", "white pine", "japanese black pine"],
        "water": "Allow soil to become nearly dry before thorough watering. Good drainage essential. Reduce in winter.",
        "soil": {"akadama": 50, "pumice": 25, "lava_rock": 25},
        "repot_years": 2,
        "fertilisation": "High nitrogen spring, balanced summer, low nitrogen autumn. Use organic cakes.",
        "pests": ["pine wilt nematode", "pine bark beetle", "needle cast", "aphids"],
        "seasonal": {
            "spring": "Candle selection and pinching. Major repotting window before candles extend.",
            "summer": "Decandling JBP in early summer for ramification. Needle plucking for balance.",
            "autumn": "Remove old needles. Structural wiring. Apply 0-10-10 for winter hardiness.",
            "winter": "Dormant period. Minimal watering. Wire while branches flexible. Protect from desiccating wind.",
        },
        "pruning_timing": "Decandling: early summer (JBP). Structural: late winter. Needle plucking: autumn.",
        "wiring_notes": "Best wired in late autumn through winter. Pine branches set slowly — may need 12-18 months. Use copper for conifers.",
        "apical_dominance": "strong",
    },
    "maple": {
        "scientific": "Acer palmatum / Acer buergerianum",
        "common_names": ["maple", "phong", "japanese maple", "trident maple", "acer"],
        "water": "Keep soil consistently moist, never waterlogged. Japanese maples sensitive to drought. Mist in hot weather.",
        "soil": {"akadama": 60, "pumice": 20, "lava_rock": 20},
        "repot_years": 1,
        "fertilisation": "Organic slow-release in spring. Low nitrogen from midsummer. Stop fertilising 6 weeks before leaf drop.",
        "pests": ["aphids", "scale", "verticillium wilt", "powdery mildew", "caterpillars"],
        "seasonal": {
            "spring": "Prune before bud break for structural work. Repot as buds swell. Begin fertilisation after leaves harden.",
            "summer": "Partial defoliation for leaf reduction. Pinch new shoots to 1-2 pairs. Partial shade in hot climates.",
            "autumn": "Light pruning after leaf drop. Wire deciduous branches while flexible. Admire autumn colour.",
            "winter": "Dormant. Minimal water. Protect from hard freeze (roots sensitive). Plan structural work.",
        },
        "pruning_timing": "Structural pruning: late winter before bud break. Pinching: spring-summer. Defoliation: early summer.",
        "wiring_notes": "Wire in autumn after leaf drop or late winter. Branches thicken fast — check monthly. Use aluminum wire. Protect bark.",
        "apical_dominance": "moderate",
    },
    "ficus": {
        "scientific": "Ficus microcarpa / Ficus retusa / Ficus benjamina",
        "common_names": ["ficus", "fig", "banyan", "đa", "si", "sanh"],
        "water": "Keep soil evenly moist. Tolerates occasional drying. High humidity preferred. Reduce in cooler months.",
        "soil": {"akadama": 40, "pumice": 30, "organic": 30},
        "repot_years": 2,
        "fertilisation": "Weekly liquid feed during growth. Balanced NPK. Reduce in winter if growth slows.",
        "pests": ["scale", "mealybug", "spider mites", "thrips"],
        "seasonal": {
            "spring": "Major pruning. Repotting. Begin heavy feeding. Defoliation for leaf reduction possible.",
            "summer": "Continuous pinching. Aerial root development. Full sun. Heavy watering and feeding.",
            "autumn": "Reduce pruning as growth slows. Prepare for indoor overwintering (temperate climates).",
            "winter": "Reduce watering and feeding. Minimum 15°C. Supplementary lighting if indoors.",
        },
        "pruning_timing": "Heavy pruning: spring. Continuous pinching in growing season. Can defoliate 1-2 times per year in tropical climates.",
        "wiring_notes": "Wire anytime but check frequently — ficus grows fast and wires cut in quickly. Use aluminum. Ficus heals well so wire scars less problematic.",
        "apical_dominance": "weak",
    },
    "azalea": {
        "scientific": "Rhododendron indicum / Rhododendron obtusum",
        "common_names": ["azalea", "satsuki", "đỗ quyên", "rhododendron"],
        "water": "Keep soil consistently moist. Sensitive to lime — use rainwater or acidified water. Never let dry completely.",
        "soil": {"kanuma": 60, "pumice": 20, "akadama": 20},
        "repot_years": 2,
        "fertilisation": "Acid-loving fertiliser. Feed after flowering. Low nitrogen. Stop in late summer for flower bud set.",
        "pests": ["lace bug", "spider mites", "azalea gall", "root rot", "petal blight"],
        "seasonal": {
            "spring": "Prune immediately after flowering. Repot after bloom or before bud swell. Begin acid fertiliser.",
            "summer": "Pinch new shoots for ramification. Partial shade. Maintain even moisture. Watch for lace bug.",
            "autumn": "Remove flower buds to desired number. Stop fertilising. Prepare for winter.",
            "winter": "Dormant or semi-dormant. Reduce water. Protect from hard freeze. Plan next year's design.",
        },
        "pruning_timing": "Major pruning immediately after flowering. Do NOT prune after midsummer — removes next year's flowers.",
        "wiring_notes": "Wire after flowering. Branches brittle — bend carefully. Use raffia protection. Remove after 3-4 months. Azalea bark scars permanently.",
        "apical_dominance": "moderate",
    },
    "elm": {
        "scientific": "Ulmus parvifolia / Zelkova serrata",
        "common_names": ["elm", "du", "chinese elm", "zelkova", "corticosa"],
        "water": "Keep evenly moist. Tolerates occasional drying. Good drainage essential to prevent root rot.",
        "soil": {"akadama": 50, "pumice": 30, "lava_rock": 20},
        "repot_years": 1,
        "fertilisation": "Heavy feeder. Weekly liquid feed during growth. High nitrogen for ramification development.",
        "pests": ["elm leaf beetle", "aphids", "scale", "powdery mildew", "dutch elm disease (zelkova resistant)"],
        "seasonal": {
            "spring": "Heavy structural pruning. Repotting. Begin aggressive feeding after leaves harden.",
            "summer": "Continuous pinching. Defoliation possible for leaf reduction. Full sun. Heavy water and feed.",
            "autumn": "Light pruning after leaf drop. Wire while flexible. Reduce fertiliser.",
            "winter": "Dormant. Minimal water. Protect from extreme cold. Plan next season's design.",
        },
        "pruning_timing": "Structural: late winter. Pinching: throughout growing season. Defoliation: early summer.",
        "wiring_notes": "Wire in autumn or late winter. Branches set in 4-6 weeks during growing season. Use aluminum. Check frequently — elm grows fast.",
        "apical_dominance": "moderate",
    },
    "bougainvillea": {
        "scientific": "Bougainvillea glabra / Bougainvillea spectabilis",
        "common_names": ["bougainvillea", "paper flower", "hoa giấy", "bông giấy"],
        "water": "Allow to dry between watering. Drought-tolerant. Over-watering reduces flowering. Reduce water to induce bloom.",
        "soil": {"akadama": 30, "pumice": 30, "organic": 20, "sand": 20},
        "repot_years": 2,
        "fertilisation": "High phosphorus for flowering. 6-8-10 or bloom booster. Feed bi-weekly. Reduce nitrogen.",
        "pests": ["aphids", "mealybug", "scale", "caterpillars"],
        "seasonal": {
            "spring": "Heavy pruning to shape. Repotting. Begin bloom fertiliser. Increase sun exposure.",
            "summer": "Reduce water slightly to induce bract colour. Continuous pinching. Full sun. Heat-loving.",
            "autumn": "Post-bloom pruning. Reduce water and feed. Bring indoors if below 10°C.",
            "winter": "Semi-dormant. Minimal water. No fertiliser. Protect from cold. 10-15°C minimum.",
        },
        "pruning_timing": "Major pruning after flowering or early spring. Continuous light pinching.",
        "wiring_notes": "Wire young flexible shoots. Older branches are brittle — use guy wires. Bougainvillea has thorns — wear gloves. Remove wire after 3-4 months.",
        "apical_dominance": "weak",
    },
}

DEFAULT_SPECIES = {
    "water": "Keep soil moist but not waterlogged. Allow surface to dry slightly between watering. Adjust frequency by season and climate.",
    "soil": {"akadama": 40, "pumice": 30, "lava_rock": 30},
    "repot_years": 2,
    "fertilisation": "Balanced organic fertiliser during growing season. Reduce or stop in winter dormancy.",
    "pests": ["monitor regularly for common pests: aphids, scale, spider mites, fungal issues"],
    "seasonal": {
        "spring": "Major pruning and repotting window. Begin fertilisation as growth starts.",
        "summer": "Maintenance pruning and pinching. Ensure adequate water. Monitor for pests.",
        "autumn": "Light structural pruning. Reduce fertiliser. Prepare for dormancy.",
        "winter": "Minimal intervention during dormancy. Protect from extreme cold. Reduce watering.",
    },
    "pruning_timing": "Major structural pruning during dormant season. Maintenance pruning during growing season.",
    "wiring_notes": "Wire during dormant period or when branches are most flexible for the species.",
    "apical_dominance": "moderate",
}

# --- Form matching logic ---
FORM_MATCHING: Dict[str, Dict[str, Any]] = {
    "chokkan": {
        "school": "japan",
        "description": "Formal upright. Straight trunk, even taper, branches alternate left-right-back with decreasing spacing toward apex.",
        "suitable_species": ["pine", "juniper", "maple", "elm", "larch", "spruce"],
        "trunk_requirements": "Straight vertical trunk with even taper. Base wider than apex. No reverse taper.",
        "branch_structure": "First branch at 1/3 height, left or right. Second branch opposite side, slightly higher. Third branch back. Alternating upward with decreasing intervals.",
        "nebari": "Radial root spread on all sides — balanced and even.",
        "container": "Rectangular or oval, unglazed, muted colour. Width ~2/3 tree height. Depth matches trunk calliper.",
    },
    "shakan": {
        "school": "japan",
        "description": "Slanting style. Trunk leans at consistent angle (15-45° from vertical). Roots anchor opposite the lean.",
        "suitable_species": ["pine", "juniper", "maple", "elm", "azalea"],
        "trunk_requirements": "Consistent lean angle. Trunk can be straight or gently curved but angle must be uniform.",
        "branch_structure": "First branch opposite the lean direction. Branches arranged to balance visual weight against the lean. Apex returns toward centre line.",
        "nebari": "Strong roots on the side opposite the lean to anchor visually and physically.",
        "container": "Round or oval. Can be deeper on the anchor-root side for stability.",
    },
    "moyogi": {
        "school": "japan",
        "description": "Informal upright. Curved trunk with alternating direction changes. Most common bonsai form.",
        "suitable_species": ["juniper", "maple", "pine", "elm", "azalea", "ficus"],
        "trunk_requirements": "Curves should alternate direction. Each curve tighter and closer together toward apex. No S-curves — natural curves only.",
        "branch_structure": "Branches emerge from outside of curves. No branches on inside of bends. First branch at ~1/3 height.",
        "nebari": "Radial, may be slightly stronger on one side to complement trunk movement.",
        "container": "Oval or round. Unglazed for conifers, glazed for deciduous. Colour complementary to foliage/flowers.",
    },
    "kengai": {
        "school": "japan",
        "description": "Full cascade. Trunk descends below the container base. Simulates tree growing on cliff face.",
        "suitable_species": ["juniper", "pine", "azalea", "cotoneaster"],
        "trunk_requirements": "Trunk rises then cascades downward. Cascade line must be continuous. Apex may rise slightly at the tip.",
        "branch_structure": "Branches arranged horizontally from the cascading trunk. Alternating left-right. Foliage pads stepped like stairs descending.",
        "nebari": "Strong roots anchoring the tree to the cliff face. Visible and prominent.",
        "container": "Tall, deep cascade pot. Unglazed. Height compensates for the descending trunk.",
    },
    "han_kengai": {
        "school": "japan",
        "description": "Semi-cascade. Trunk descends below pot rim but not below pot base.",
        "suitable_species": ["juniper", "pine", "maple", "azalea"],
        "trunk_requirements": "Trunk rises then cascades to or just below pot rim level.",
        "branch_structure": "Similar to cascade but more compact. Crown remains above cascade line.",
        "nebari": "Strong roots visible, anchoring the cascade.",
        "container": "Round or hexagonal, medium depth. Can be glazed or unglazed.",
    },
    "bunjingi": {
        "school": "japan",
        "description": "Literati style. Tall, slender, elegant trunk with minimal branches. Emphasizes line and negative space. Inspired by Chinese scholar paintings.",
        "suitable_species": ["pine", "juniper", "maple"],
        "trunk_requirements": "Tall, thin, with dramatic curves. No taper needed. Natural, graceful movement essential.",
        "branch_structure": "Very few branches — typically 2-4 only. Usually in upper third of tree. Long, slender, reaching out. Abundant negative space.",
        "nebari": "Minimal visible root. Delicate and refined.",
        "container": "Small, shallow, round pot. Unglazed, subdued earth tones. Container should NOT dominate.",
    },
    "sokan": {
        "school": "japan",
        "description": "Twin-trunk style. Two trunks from single root base. Primary trunk taller and thicker.",
        "suitable_species": ["juniper", "maple", "pine", "elm", "ficus"],
        "trunk_requirements": "Two trunks from same root base. Fork at or near soil level. Primary trunk dominant in thickness and height. Secondary trunk follows same movement.",
        "branch_structure": "Branches emerge from outside of the V. No branches between trunks. Both trunks share branch space harmoniously.",
        "nebari": "Unified radial nebari supporting both trunks.",
        "container": "Oval or rectangular. Wider than solo-tree pots to accommodate dual trunks.",
    },
    "neagari": {
        "school": "japan",
        "description": "Exposed root style. Roots visible above soil, creating sculptural effect.",
        "suitable_species": ["ficus", "juniper", "maple", "pine", "elm"],
        "trunk_requirements": "Roots trained to be visible above soil line, merging into trunk.",
        "branch_structure": "Standard form-dependent branch arrangement.",
        "nebari": "THE focal point — roots are exposed and sculptural, merging into the trunk.",
        "container": "Shallow to medium depth, allowing root display. Usually unglazed.",
    },
    "shanshui": {
        "school": "china",
        "description": "Penjing landscape style with mountains, water, and miniature trees creating a complete scene.",
        "suitable_species": ["juniper", "pine", "maple", "elm"],
        "trunk_requirements": "Multiple small trees arranged in landscape composition. Individual trees follow miniature forms.",
        "branch_structure": "Trees arranged to create depth perspective. Larger trees in foreground, smaller in background.",
        "rock_composition": "Essential — limestone or weathered rocks shaped as mountains. Water feature (real or implied with white sand).",
        "container": "Large shallow tray or marble slab. Low rim or rimless.",
    },
    "tho_nui": {
        "school": "vietnam",
        "description": "Vietnamese mountain style (thế thổ núi). Dramatic landscape composition with vertical mountain rock, trees emerging from crevices.",
        "suitable_species": ["ficus", "juniper", "bougainvillea"],
        "trunk_requirements": "Trees growing from rock crevices. Dramatic angles. Naturalistic mountain growth pattern.",
        "branch_structure": "Asymmetrical. Trees appear wind-swept or cliff-adapted. Multiple specimens on single rock formation.",
        "rock_composition": "Vertical mountain rock — limestone or weathered stone. Central dramatic feature. Multiple planting pockets.",
        "container": "Shallow water tray or carved stone base. Water feature common.",
    },
    "chan_tho": {
        "school": "vietnam",
        "description": "Vietnamese multi-tier trunk style (chân thọ). Trunk develops dramatic tiered structure with distinct platforms at each level.",
        "suitable_species": ["ficus", "juniper", "elm"],
        "trunk_requirements": "Trunk divides into distinct horizontal tiers. Each tier develops independent branch structure. Dramatic taper at each division.",
        "branch_structure": "Each tier develops its own branch canopy. Tiers stacked vertically. Negative space between tiers is critical.",
        "nebari": "Broad, powerful, anchoring the multi-tier structure.",
        "container": "Large, deep, rectangular. Substantial and grounded.",
    },
}

# --- Pruning physiology reference ---
PRUNING_PHYSIOLOGY = {
    "apical_dominance": {
        "description": "Auxin (IAA) produced in apical buds and young leaves is transported basipetally, suppressing lateral bud growth. Removing the apex reduces auxin flow, releasing lateral buds from inhibition.",
        "implications": [
            "Pruning terminal shoots redistributes auxin and releases lower buds — essential for ramification",
            "Strong apical species (pine, spruce) need decandling or candle-pinching to balance energy",
            "Weak apical species (ficus, bougainvillea) respond to pinching with profuse back-budding",
            "Partial defoliation of outer canopy reduces auxin, stimulating interior back-budding",
        ],
        "sources": [
            "Cline (1997). Auxin and apical dominance. Plant Physiol. DOI: 10.1104/pp.96.4.1621",
        ],
    },
    "wound_healing": {
        "description": "CODIT (Compartmentalization of Decay in Trees) — trees wall off wounded tissue through chemical and physical barriers. Proper pruning cuts at the branch collar maximise healing.",
        "implications": [
            "Always cut at the branch collar — never flush with trunk (removes protective zone)",
            "Concave cuts heal faster and produce less visible scarring",
            "Large cuts should be sealed with cut paste to prevent desiccation and pathogen entry",
            "Pruning timing affects healing rate — active growth season heals fastest",
        ],
        "sources": [
            "Shigo & Marx (1977). CODIT. USDA Forest Service. DOI: 10.5962/bhl.title.69538",
            "Dujesiefken & Liese (2015). Wound closure after pruning. Arboric. J. DOI: 10.1080/03071375.2015.1087131",
        ],
    },
    "timing": {
        "description": "Pruning timing depends on species physiology and objective. Structural pruning during dormancy minimises sap loss and stress. Maintenance pruning during active growth stimulates ramification.",
        "implications": [
            "Deciduous: major structural pruning in late winter dormancy before bud break",
            "Conifers: structural pruning in late winter to early spring; pinching throughout growing season",
            "Tropical (ficus): can prune year-round in warm climates; avoid heavy pruning in cool periods",
            "Flowering species: prune immediately after flowering to preserve next year's blooms",
            "Never heavy-prune during extreme heat, drought stress, or immediately after repotting",
        ],
    },
    "ramification": {
        "description": "Ramification is the repeated division of branches into finer and finer twigs, creating dense foliage pads and mature appearance.",
        "techniques": [
            "Pinching: remove soft growing tips to force division at the node below",
            "Decandling (pines): remove entire spring candle to force multiple summer buds",
            "Partial defoliation (deciduous): remove outer leaves to promote interior back-budding",
            "Clip-and-grow: allow shoots to extend, then cut back hard to force branching at the cut point",
        ],
    },
}

# --- Wiring reference ---
WIRING_REFERENCE = {
    "materials": {
        "copper": "Best for conifers. Work-hardens after bending for strong hold. Colour ages to brown. More difficult to apply.",
        "aluminum": "Best for deciduous and beginners. Easier to bend. Silver colour less visible on light bark. Must use anodized.",
    },
    "gauge_selection": [
        {"branch_diameter_mm": "1-3", "wire_gauge_mm": 1.0},
        {"branch_diameter_mm": "3-6", "wire_gauge_mm": 1.5},
        {"branch_diameter_mm": "6-10", "wire_gauge_mm": 2.0},
        {"branch_diameter_mm": "10-15", "wire_gauge_mm": 2.5},
        {"branch_diameter_mm": "15-25", "wire_gauge_mm": 3.0},
        {"branch_diameter_mm": "25-40", "wire_gauge_mm": 4.0},
    ],
    "technique": [
        "Wire at 45° angle in consistent, even spirals",
        "Anchor wire in soil or around a lower branch before starting",
        "Wire two branches with one wire where possible (double-wiring)",
        "Bend branch by placing thumbs against the wire — wire supports the bend",
        "Never cross wires — creates pressure points",
        "Remove wire BEFORE it bites into bark (typically 3-9 months for deciduous, 6-18 for conifers)",
    ],
}

# --- Rock/landscape composition for penjing ---
ROCK_COMPOSITION_TEMPLATES = {
    "ishitsuki": {
        "description": "Root-over-rock style. Tree grows on/over a rock with roots gripping the stone and reaching soil below.",
        "rock_selection": "Weathered, textured rock with crevices and character. Limestone, lava, or collected mountain stone.",
        "technique": "Place young tree with long roots over rock. Bind roots to rock with raffia or plastic wrap. Bury rock+roots in soil. Expose gradually over 1-3 years as roots thicken and grip.",
        "key_principles": [
            "Rock and tree must complement in proportion and character",
            "Roots should follow rock contours naturally, not artificially",
            "Exposed roots must thicken and become woody — this takes years",
            "Tree species should be drought-tolerant (roots dry faster on rock)",
        ],
    },
    "saikei": {
        "description": "Miniature landscape planting with multiple trees, rocks, and ground cover creating a natural scene.",
        "rock_selection": "Weathered rocks arranged as mountains, cliffs, or outcrops. Scale-appropriate to trees.",
        "technique": "Arrange rocks to create depth perspective. Place trees at varying distances. Add moss/ground cover. Maintain sense of scale throughout.",
        "key_principles": [
            "Foreground rocks larger, background rocks smaller for perspective",
            "Trees placed according to landscape logic — not random",
            "Open space (water/grass) balances rock and tree mass",
            "Maintain consistent scale — small trees with proportionally small rocks",
        ],
    },
    "shanshui_penjing": {
        "description": "Chinese landscape penjing with water, mountains, and miniature architecture.",
        "rock_selection": "Limestone with natural erosion patterns. Water-worn rocks from river beds. Multiple sizes for depth layering.",
        "technique": "Build mountain scene with primary peak (host), secondary peaks (guest). Add trees in crevices. Water feature with white sand or actual water. Optional: miniature pavilions, bridges, boats.",
        "key_principles": [
            "Host mountain dominates — guest mountains support",
            "Odd numbers of rocks preferred (3, 5, 7)",
            "Water element essential — real water or implied with white sand",
            "Trees subordinate to mountain composition",
        ],
    },
}
