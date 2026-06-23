import React from 'react';
import { Text, StyleProp, TextStyle } from 'react-native';
import { useAppendixStore } from '../store/appendix';
import { useSectionModalStore } from '../store/sectionModal';

// Wrap each maximal run of Hebrew (letters + nikkud + internal spaces) in
// Unicode directional isolates (RLI U+2067 … PDI U+2069) so inline Hebrew sits
// correctly inside LTR text instead of being reordered against punctuation.
function isolateHebrew(text: string): string {
  return text.replace(/[֐-׿]+(?:[ ֐-׿]*[֐-׿])?/g, (run) => '⁧' + run + '⁩');
}

// Matches **bold** (greedy-safe) or *italic* spans.
const SPAN_RE = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;
const APPENDIX_RE = /(Appendix\s+\d+)/g;
// [label](section:key) — inline section links
const SECTION_LINK_RE = /(\[[^\]]+\]\(section:[^)]+\))/g;

interface Props {
  text: string;
  style?: StyleProp<TextStyle>;
  italicStyle?: StyleProp<TextStyle>;
  boldStyle?: StyleProp<TextStyle>;
  linkStyle?: StyleProp<TextStyle>;
}

// Render a leaf string: linkify "Appendix N", [text](section:key), and isolate inline Hebrew.
function renderLeaf(
  text: string,
  keyBase: string,
  spanStyle: StyleProp<TextStyle> | undefined,
  openAppendix: (n: number) => void,
  openSection: (key: string) => void,
  linkStyle: StyleProp<TextStyle> | undefined
): React.ReactNode[] {
  // First split on section links, then on Appendix references
  const parts = text.split(SECTION_LINK_RE);
  return parts.flatMap((part, j) => {
    // [label](section:key)
    const sectionMatch = part.match(/^\[([^\]]+)\]\(section:([^)]+)\)$/);
    if (sectionMatch) {
      const [, label, key] = sectionMatch;
      return [(
        <Text
          key={`${keyBase}-s${j}`}
          style={[spanStyle, linkStyle]}
          onPress={() => openSection(key)}
          accessibilityRole="link"
          accessibilityLabel={`Open ${label}`}
        >
          {label}
        </Text>
      )];
    }

    // Appendix N links
    return part.split(APPENDIX_RE).map((chunk, k) => {
      const m = chunk.match(/^Appendix\s+(\d+)$/);
      if (m) {
        const n = parseInt(m[1], 10);
        return (
          <Text
            key={`${keyBase}-${j}-${k}`}
            style={[spanStyle, linkStyle]}
            onPress={() => openAppendix(n)}
            accessibilityRole="link"
            accessibilityLabel={`Open Appendix ${n}`}
          >
            {chunk}
          </Text>
        );
      }
      const content = isolateHebrew(chunk);
      return spanStyle ? (
        <Text key={`${keyBase}-${j}-${k}`} style={spanStyle}>{content}</Text>
      ) : (
        content
      );
    });
  });
}

// Renders commentary/insight/faq text with **bold**, *italic*, correct inline
// Hebrew placement, tappable "Appendix N" links, and [label](section:key) links.
export function RichText({ text, style, italicStyle, boldStyle, linkStyle }: Props) {
  const openAppendix = useAppendixStore((s) => s.open);
  const openSection = useSectionModalStore((s) => s.open);

  return (
    <Text style={style}>
      {text.split(SPAN_RE).map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
          return renderLeaf(part.slice(2, -2), `b${i}`, boldStyle, openAppendix, openSection, linkStyle);
        }
        if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
          return renderLeaf(part.slice(1, -1), `i${i}`, italicStyle, openAppendix, openSection, linkStyle);
        }
        return renderLeaf(part, `p${i}`, undefined, openAppendix, openSection, linkStyle);
      })}
    </Text>
  );
}
