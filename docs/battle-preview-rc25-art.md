# BATTLE-RC25 motion preview

This is an independent visual and motion preview, accessible at `battle-preview.html`. HP is expressed as demo percentages. These reductions are placeholders for animation checks and do not adopt the main game's balance or award resources. No game storage is read or written. The existing RC24 game remains reachable from the Home link.

Three allies: 白翼のアルム (c001), 鉄骸兵 (c002), 冥牙クロウル (c003). Enemy: 水晶の守護者 (visual-preview identity).

Generated with the built-in image generation tool. Transparent images preserve the generated alpha when optimized as WebP. The approved angel sprite was recovered from the user's existing sprite file.

## Asset map

| Asset | Use |
|---|---|
| assets/rc25-alum.webp | Approved angel idle sprite |
| assets/rc25-iron.webp | Rusted mechanical soldier idle sprite |
| assets/rc25-wolf.webp | Quadruped spectral wolf idle sprite |
| assets/rc25-guardian.webp | Crystal guardian idle sprite |
| assets/rc25-stage.webp | Background-only sky-palace terrace |
| assets/rc25-icon-c001.webp … c003.webp | Existing game portrait thumbnails |
| assets/rc23-party-title.webp | Reused generated title plaque |
| assets/rc23-party-confirm.webp | Reused generated button plaque |
| assets/rc24-party-card.webp | Reused generated portrait frame |

## Generation prompts

### iron

Use case: identity-preserve, stylized-concept. One full-body transparent 2D battle sprite of 鉄骸兵, the rusted mechanical soldier in reference image 1. Reference image 2 is the APPROVED visual style and compact body proportion guide, not a character to include. Preserve the machine's original identity: rounded battered dark iron helmet, exactly two small blazing orange eye lenses, vertical barred respirator mouth, thick ribbed breathing hoses across the neck, overlapping heavily rusted bronze-black armor plates, chunky shoulder spikes, orange furnace cracks and a small glowing chest seam. Extend the torso faithfully into short massive armored legs and heavy boots, two bulky arms and closed mechanical fists. Compact approximately 3-head-tall silhouette with a large readable helmet and stout body, matching the lightly deformed hand-painted 2D RPG style of the angel reference. Neutral ready standing pose, entire figure facing RIGHT in a three-quarter view, both feet visible on the same ground line, arms slightly separated from torso for a clear silhouette. Warm orange glow is restrained inside eyes and cracks. Crisp painted linework, controlled high-detail shading, NOT photorealism, not 3D or plastic, not an icon or card. The exact one character only with all helmet, shoulders, fists, legs and boots fully in frame, modest transparent margin on all sides. Actual alpha-transparent exterior and limb gaps. No angel, no extra characters, text, UI, badge, pedestal, ground, shadow, smoke cloud, background or weapons. Keep the source machine's proportions stout and visually distinct from the crystal guardian enemy.

### wolf

Use case: identity-preserve, stylized-concept. One reusable full-body transparent 2D battle sprite of 冥牙クロウル, the creature in reference image 1. Reference image 2 is solely the approved soft hand-painted 2D RPG battle style/proportion reference, do not include that angel. Preserve a SINGLE black-furred wolf-like QUADRUPED with a broad low snarling canine head, red glowing eyes, sharp pale fangs, shaggy charcoal-black fur, four powerful clawed paws, small close purple spectral flames among the fur and light gray-purple wisps curling near the shoulders. Faithfully extend the original visible head and front paws to a complete compact four-legged wolf body with hind legs and a short-to-medium natural wolf tail. Low battle-ready idle stance, oriented to the RIGHT in a three-quarter view, head looking toward an enemy at the right; all four paws remain clearly separate and visible. Lightly deformed compact RPG monster anatomy with an enlarged readable head, consistent with the reference angel's SD scale, not a humanoid werewolf, not a realistic horror photo, not 3D. Strong simple silhouette and crisp cel-painterly detail readable when small. Keep supernatural effects close to the body and sufficiently translucent, never a large cloud that hides the feet. Entire wolf including tail tip, paws and ears fully visible with transparent margins. One wolf only, actual transparent alpha outside the body and between legs. No background, ground shadow, pedestal, scenery, text, UI, frame, extra head, extra limbs, angel or weapon.

### guardian

Use case: identity-preserve / background-extraction. Create ONE isolated full-body transparent 2D sprite of the blue-crystal stone guardian on the RIGHT of reference image 1. Reference image 2 is a style/SD anatomy guide only, do not include the angel. Preserve that same enemy: squat broad dark slate-gray stone armor, angular oversized forearms and clenched stone fists, short heavy legs, pointed cyan-blue crystals growing from shoulders and head, bright faceted cyan crystal core in chest, thin engraved gold bands, sparse green ivy and a few tiny white/yellow flowers on the shoulders. Exactly one angular head with two small cyan eyes. Same approximately 3-head-tall compact hand-painted 2D RPG style. Neutral ready stance facing LEFT in a three-quarter view, both feet clearly visible on a level baseline, arms readable and separated from torso. Keep the shape friendly-dangerous and readable, matching the premium painted anime style, not photorealistic and not 3D toy rendering. Entire enemy fully visible with generous alpha margin, no cropped crystals or feet. Real transparent alpha background and gaps. Remove ALL other content from the reference: no angel, terrace, ground shadow, HP bar, UI, frames, text, scenery, floor, clouds, labels or other objects. Only the single crystal guardian sprite.

### stage

Use case: precise-object-edit, stylized-concept. Asset type: separate background-only battlefield plate for a portrait Japanese fantasy 2D RPG. Use the provided sky-palace battle concept as the world/art/color reference. Produce a new clean battle-stage BACKGROUND with NO CHARACTERS, HP bars or UI anywhere. Reframe the camera significantly closer to the open terrace, with the horizon and balustrades in the TOP QUARTER of the image and a broad uninterrupted pale stone battle floor occupying the LOWER 75 percent. This large empty walkable foreground must accommodate three ally units vertically staggered on the left and one enemy on the right. Elegant fine gold and muted sapphire floor inlays, restrained blue-white stone material, slightly warm readable floor so dark and white sprites both contrast well. At the upper distance: floating white-and-gold castle ruins, blue sky, modest waterfalls, a sapphire portal on the far left edge, a few flowers kept at the outer corners. Premium hand-painted 2D anime fantasy environment, consistent with the reference world, slightly softer and less busy than unit artwork. Portrait approximately 4:5 composition, camera from a gently elevated side battle view, no extreme perspective, no huge foreground props, no holes, stairs or rails across the central playing field. No hero, enemy, silhouettes, sprites, shadows of characters, text, symbols that resemble UI, HUD, cards, buttons, panels, health bars, frame, watermark or logo. Full opaque background only.


