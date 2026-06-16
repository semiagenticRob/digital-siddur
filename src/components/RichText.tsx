import React from 'react';
import { Text, StyleProp, TextStyle } from 'react-native';
import { useAppendixStore } from '../store/appendix';

// Wrap each maximal run of Hebrew (letters + nikkud + internal spaces) in
// Unicode directional isolates (RLI U+2067 … PDI U+2069) so inline Hebrew sits
// correctly inside LTR text instead of being reordered against punctuation.
function isolateHebrew(text: string): string {
  return text.replace(/[֐-׿]+(?:[ ֐-׿]*[֐-׿])?/g, (run) => '⁧' + run + '⁩');
}

const APPENDIX_RE = /(Appendix\s+\d+)/g;

interface Props {
  text: string;
  style?: StyleProp<TextStyle>;
  italicStyle?: StyleProp<TextStyle>;
  linkStyle?: StyleProp<TextStyle>;
}

// Renders commentary/insight/faq text with: *markdown* italics, correct inline
// Hebrew placement, and tappable "Appendix N" cross-reference links.
export function RichText({ text, style, italicStyle, linkStyle }: Props) {
  const open = useAppendixStore((s) => s.open);

  // Split into italic / non-italic spans (odd indices are italic).
  const italicParts = text.split(/\*([^*]+)\*/g);

  return (
    <Text style={style}>
      {italicParts.map((part, i) => {
        const isItalic = i % 2 === 1;
        const baseStyle = isItalic ? italicStyle : undefined;
        // Within each span, split out "Appendix N" references.
        const refParts = part.split(APPENDIX_RE);
        return refParts.map((rp, j) => {
          const m = rp.match(/^Appendix\s+(\d+)$/);
          if (m) {
            const n = parseInt(m[1], 10);
            return (
              <Text
                key={`${i}-${j}`}
                style={[baseStyle, linkStyle]}
                onPress={() => open(n)}
                accessibilityRole="link"
                accessibilityLabel={`Open Appendix ${n}`}
              >
                {rp}
              </Text>
            );
          }
          const content = isolateHebrew(rp);
          return isItalic ? (
            <Text key={`${i}-${j}`} style={baseStyle}>{content}</Text>
          ) : (
            content
          );
        });
      })}
    </Text>
  );
}
