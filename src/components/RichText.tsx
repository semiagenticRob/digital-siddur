import React from 'react';
import { Text, StyleProp, TextStyle } from 'react-native';
import { useAppendixStore } from '../store/appendix';

// Wrap each maximal run of Hebrew (letters + nikkud + internal spaces) in
// Unicode directional isolates (RLI U+2067 … PDI U+2069) so inline Hebrew sits
// correctly inside LTR text instead of being reordered against punctuation.
function isolateHebrew(text: string): string {
  return text.replace(/[֐-׿]+(?:[ ֐-׿]*[֐-׿])?/g, (run) => '⁧' + run + '⁩');
}

// Matches **bold** (greedy-safe) or *italic* spans.
const SPAN_RE = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;
const APPENDIX_RE = /(Appendix\s+\d+)/g;

interface Props {
  text: string;
  style?: StyleProp<TextStyle>;
  italicStyle?: StyleProp<TextStyle>;
  boldStyle?: StyleProp<TextStyle>;
  linkStyle?: StyleProp<TextStyle>;
}

// Render a leaf string: linkify "Appendix N" and isolate inline Hebrew.
function renderLeaf(
  text: string,
  keyBase: string,
  spanStyle: StyleProp<TextStyle> | undefined,
  open: (n: number) => void,
  linkStyle: StyleProp<TextStyle> | undefined
): React.ReactNode[] {
  return text.split(APPENDIX_RE).map((part, j) => {
    const m = part.match(/^Appendix\s+(\d+)$/);
    if (m) {
      const n = parseInt(m[1], 10);
      return (
        <Text
          key={`${keyBase}-${j}`}
          style={[spanStyle, linkStyle]}
          onPress={() => open(n)}
          accessibilityRole="link"
          accessibilityLabel={`Open Appendix ${n}`}
        >
          {part}
        </Text>
      );
    }
    const content = isolateHebrew(part);
    return spanStyle ? (
      <Text key={`${keyBase}-${j}`} style={spanStyle}>{content}</Text>
    ) : (
      content
    );
  });
}

// Renders commentary/insight/faq text with **bold**, *italic*, correct inline
// Hebrew placement, and tappable "Appendix N" cross-reference links.
export function RichText({ text, style, italicStyle, boldStyle, linkStyle }: Props) {
  const open = useAppendixStore((s) => s.open);

  return (
    <Text style={style}>
      {text.split(SPAN_RE).map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
          return renderLeaf(part.slice(2, -2), `b${i}`, boldStyle, open, linkStyle);
        }
        if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
          return renderLeaf(part.slice(1, -1), `i${i}`, italicStyle, open, linkStyle);
        }
        return renderLeaf(part, `p${i}`, undefined, open, linkStyle);
      })}
    </Text>
  );
}
