import React from 'react';
import { Text, StyleProp, TextStyle } from 'react-native';

// Wrap each maximal run of Hebrew (letters + nikkud + internal spaces) in
// Unicode directional isolates (RLI U+2067 … PDI U+2069). Without this, RN's
// bidi algorithm reorders inline Hebrew against adjacent dashes/punctuation,
// pushing a leading lemma like "מוֹדֶה אֲנִי—Thank You" into the middle of the line.
function isolateHebrew(text: string): string {
  return text.replace(
    /[֐-׿]+(?:[ ֐-׿]*[֐-׿])?/g,
    (run) => '⁧' + run + '⁩'
  );
}

interface Props {
  text: string;
  style?: StyleProp<TextStyle>;
  italicStyle?: StyleProp<TextStyle>;
}

// Renders commentary/insight/etc. text with:
//  - *markdown* italic spans
//  - correct placement of inline Hebrew lemmas (bidi isolation)
export function RichText({ text, style, italicStyle }: Props) {
  // Split on *italic*. With a capture group, odd indices are the italic content.
  const parts = text.split(/\*([^*]+)\*/g);
  return (
    <Text style={style}>
      {parts.map((part, i) =>
        i % 2 === 1 ? (
          <Text key={i} style={italicStyle}>
            {isolateHebrew(part)}
          </Text>
        ) : (
          isolateHebrew(part)
        )
      )}
    </Text>
  );
}
