// Named in-content sections referenced by [here](section:key) links in RichText.
// Each entry has a display title and body text (markdown, rendered by RichText).

export interface SectionEntry {
  title: string;
  body: string;
}

export const SECTIONS: Record<string, SectionEntry> = {
  'bm-intro': {
    title: "You Ate a Good Meal? It's a Miracle Like Manna from Heaven! Say Thank You!",
    body: `**Bentchaphobia:** "I don't want bread—I don't want to bentch!" We go to great lengths to avoid getting to bentch?! The simple answer is that bentching is long and we're in a rush. But I'd like to take it a bit deeper and offer two thoughts on this subject for you to consider. And they apply not only to the full Birkas Ha'mazon, but to Al Ha'michyah and Borei Nefashos as well.\n\n**1.** In our world of plenty, it's so easy to take stuff for granted. We go to the store and find tons of all kinds of food right there for us—in all seasons. A lot of miracles! The sun has to rise, it must rain at the right time and the right amount, seeds must sprout… and that's before we even consider the daily miracles involved in us having the ability to eat the food, taste it, and digest it. These miracles are no less amazing than the miracles in the desert—it's just that we're used to them since they happen all the time. That's why we don't feel the need to spend all that time bentching—it feels like a burden with no real reason. This is also the reason that Pesukei D'Zimrah (which many people find annoying—"Why do I have to praise Hashem so much? Does He need the praises?") struggles with this burden. We don't need our bentching, and He does not need our Pesukei D'Zimrah. We need to say it in order to make us aware of His countless gifts to us.\n\n**2.** We don't like to owe other people favors. We don't like to be beholden to others. "I'm fine, I can do it all myself!" But we can't do anything without Hashem's help. Bentching (and the same for Pesukei D'Zimrah, and in fact all tefillah) reminds us of that. By bentching—and again, the same for Pesukei D'Zimrah—we remind ourselves that Hashem is in charge and that though we must do as much as we can, in the end nothing happens without Hashem's help.`,
  },
};

export function getSection(key: string): SectionEntry | undefined {
  return SECTIONS[key];
}
