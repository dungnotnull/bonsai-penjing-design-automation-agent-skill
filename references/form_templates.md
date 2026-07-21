# Classical Form Templates Reference

This directory contains detailed templates for classical bonsai/penjing forms used by the core analysis service.

## Form Classification

### Japanese School (Bonsai)

#### Major Forms (5 Basic Styles)

1. **Chokkan (Formal Upright)**
   - Straight trunk
   - Tapering from base to apex
   - Branches evenly distributed
   - Apex centered above base
   - Symbolism: Strength, dignity, solitude

2. **Moyogi (Informal Upright)**
   - Curving trunk with movement
   - Tapering maintained
   - Branches following trunk curves
   - Dynamic but balanced
   - Symbolism: Naturalness, flexibility

3. **Shakan (Slanting)**
   - Trunk slanted at ~45°
   - Roots counterbalancing
   - Apex off-center
   - Wind-swept appearance
   - Symbolism: Resilience, struggle

4. **Kengai (Cascade)**
   - Trunk cascades below pot rim
   - Grown in tall pot
   - Apex below pot base
   - Cliff-hanging metaphor
   - Symbolism: Age, endurance

5. **Han-Kengai (Semi-Cascade)**
   - Trunk extends below pot rim
   - Apex above pot base
   - Moderate cascade
   - Symbolism: Graceful aging

#### Advanced Forms

6. **Fukinagashi (Windswept)**
   - All branches flowing one direction
   - Trunk often twisted
   - Wind simulation
   - Symbolism: Harsh conditions, survival

7. **Bunjingi (Literati)**
   - Slender trunk
   - Minimal foliage
   - Branches at upper portion only
   - Elegant simplicity
   - Symbolism: Scholarly refinement

8. **Sokan (Twin Trunk)**
   - Two trunks from single root base
   - One dominant, one subordinate
   - Shared canopy
   - Symbolism: Parent-child, duality

9. **Kabudachi (Clump)**
   - Multiple trunks from single base
   - Canopy unified
   - Forest simulation
   - Symbolism: Community, harmony

10. **Yose-ue (Forest)**
    - Multiple trees in single pot
    - Odd-numbered planting
    - Depth and perspective
    - Symbolism: Landscape, perspective

### Chinese School (Penjing)

#### Landscape Forms

1. **Shan-Shui (Mountain-Water)**
   - Rock-dominated composition
   - Trees as accent elements
   - Water simulation
   - Philosophical: Taoist landscape

2. **Shui-Han (Water and Land)**
   - Balanced rock/tree composition
   - Water feature present
   - Landscape miniature
   - Philosophical: Harmony

3. **Pen-Jing (Pot Landscape)**
   - Comprehensive scene
   - Rock, tree, water, figurines
   - Narrative element
   - Philosophical: Storytelling

#### Tree Forms

4. **Guai-Zi (Dragon Style)**
   - Dramatic trunk movement
   - Power and age expression
   - Chinese aesthetic
   - Symbolism: Mythical power

5. **Tiao-Wen (Striped Pattern)**
   - Exposed root style
   - Surface roots prominent
   - Age simulation
   - Symbolism: Endurance

### Vietnamese School (Bon Sai)

#### Regional Forms

1. **Phong Thuy (Feng Shui)**
   - Auspicious placement
   - Lucky number of elements
   - Cultural symbolism
   - Symbolism: Prosperity, harmony

2. **Tuong Dai (Grandeur Style)**
   - Large, impressive specimens
   - Monumental scale
   - Exhibition focus
   - Symbolism: Status, achievement

3. **Nhon Nho (Human Figure)**
   - Figurative shaping
   - Human forms/animals
   - Narrative scenes
   - Symbolism: Storytelling, culture

## Form Matching Algorithm

The core analysis service uses this decision tree:

```
IF species has strong conical growth
   → Chokkan (Formal Upright) suitable
ELIF species has flexible branches
   → Kengai (Cascade) or Han-Kengai (Semi-Cascade)
ELIF species has natural movement
   → Moyogi (Informal Upright) or Shakan (Slanting)
ELIF species tolerates heavy pruning
   → Yose-ue (Forest) or Kabudachi (Clump)
ELIF species has interesting bark
   → Bunjingi (Literati)
ELSE
   → Moyogi (Informal Upright) as default
```

## Form-Specific Considerations

### Wiring by Form

| Form | Primary Wire Locations | Timing Considerations |
|------|------------------------|----------------------|
| Chokkan | Trunk straightening, branch positioning | Early spring, before bud break |
| Moyogi | Trunk movement, branch direction | Late winter, dormancy |
| Kengai | Heavy trunk bending, branch cascading | Spring, active growth |
| Bunjingi | Upper branch refinement | Any time, careful monitoring |
| Yose-ue | Individual tree positioning | Repotting time |

### Pruning by Form

| Form | Pruning Priority | Ramification Focus |
|------|-----------------|-------------------|
| Chokkan | Branch selection, apical control | Lower branches first |
| Moyogi | Movement maintenance | Along trunk curve |
| Kengai | Balance maintenance | Cascade region |
| Bunjingi | Foliage pads | Upper canopy only |
| Yose-ue | Individual tree shaping | Outer canopy |

## Form Evaluation Criteria

When evaluating a specimen for form potential:

1. **Trunk Quality**
   - Taper (base to apex)
   - Movement (dynamic vs static)
   - Bark characteristics
   - Age indicators

2. **Branch Structure**
   - Placement (alternating vs opposite)
   - Direction (radial vs one-sided)
   - Thickness ratio (branch to trunk)
   - Ramification potential

3. **Root Structure**
   - Nebari (surface root spread)
   - Rootage (visible roots)
   - Stability (anchoring)
   - Aesthetic contribution

4. **Overall Balance**
   - Visual weight distribution
   - Negative space utilization
   - Pot selection
   - Display angle

## References

- Naka, J. (1984). "Bonsai Techniques I & II"
- Kobayashi, K. (2002). "Forest, Rock Planting & Ezo Spruce Bonsai"
- Zhao, X. (2019). "Chinese penjing composition principles"
- Nguyen, T. (2021). "Vietnamese bonsai traditions and contemporary adaptations"
