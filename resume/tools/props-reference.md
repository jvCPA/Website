# Background props: references and build notes

Three small stylised props float behind the figure in the hero, one per pillar. They are built in
code (`buildCalculator`, `buildRobot`, `buildBarChart` in `apps-script/Scene.html`) following the
img2threejs staged approach (blockout → structure → form → material → lighting → optimisation).
They are rendered into a quarter-resolution target, blurred, and used as the stage background, so
they always sit behind the figure and read as out of focus. They are skipped on phones and on
low-power devices.

The image collections could not be reached from the build machine, so each reference is a written
description of a clean product shot rather than a photo.

| Pillar | Reference (described) | Identity-defining features kept | Materials |
|---|---|---|---|
| Accounting & Tax | A desktop calculator photographed at three-quarter view on a plain background: chunky rounded slab, recessed display at the top, 4 × 5 keypad, one coloured equals key | Slab silhouette with soft corners, inset dark display with a lit readout, regular keypad grid, accent equals key bottom-right | Body: navy satin plastic. Keys: dark navy and pale periwinkle. Equals key: accent blue, faintly emissive. Readout: periwinkle glow |
| AI Automation | A small toy robot head: rounded cube head, dark glass visor band, two pill-shaped glowing eyes, round ear pods, a thin antenna with a ball tip | Rounded-cube head, visor band, capsule eyes, ear pods, antenna and tip, short neck | Head: pale periwinkle matte. Visor: dark navy gloss. Eyes and antenna tip: periwinkle glow. Ears: accent blue |
| Data Analytics | A 3D bar chart desk ornament: a low base tile with four rounded bars rising left to right, the last bar highlighted | Base tile, four bars with a dip at the third, tallest bar in the accent colour | Base: navy satin. Bars: pale periwinkle. Tallest bar: accent blue |

Stylisation notes: geometry is deliberately simple (rounded boxes, capsules, cylinders) because the
props are small, blurred and fogged; colour comes only from the page palette (navy, periwinkle and
the single accent `#5266eb`). A single view cannot show hidden sides; the backs mirror the fronts.
