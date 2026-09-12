import React from "react";
import { useCurrentFrame } from "remotion";
import { C } from "../theme";

// 打字机：startFrame 起按 framesPerChar 逐字出现，打完后光标按 12 帧周期闪烁
export const Typewriter: React.FC<{
  text: string;
  startFrame?: number;
  framesPerChar?: number;
  cursorColor?: string;
  style?: React.CSSProperties;
}> = ({
  text,
  startFrame = 0,
  framesPerChar = 3,
  cursorColor = C.green,
  style,
}) => {
  const frame = useCurrentFrame();
  const n = Math.max(0, Math.floor((frame - startFrame) / framesPerChar));
  const shown = text.slice(0, Math.min(n, text.length));
  const typing = n < text.length;
  const cursorOn = typing || frame % 12 < 6;
  return (
    <span style={{ ...style, whiteSpace: "pre" }}>
      {shown}
      <span style={{ opacity: cursorOn ? 1 : 0, color: cursorColor }}>▍</span>
    </span>
  );
};
