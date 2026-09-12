import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT_CN } from "../theme";

// 小徽章胶囊：delay 后 spring 弹入
export const Badge: React.FC<{
  children: React.ReactNode;
  delay?: number;
  color?: string;
  filled?: boolean;
  style?: React.CSSProperties;
}> = ({ children, delay = 0, color = C.green, filled = false, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({
    frame: frame - delay,
    fps,
    config: { damping: 14, stiffness: 130, mass: 0.7 },
  });
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        padding: "10px 26px",
        borderRadius: 999,
        border: `1.5px solid ${color}`,
        background: filled ? color : "transparent",
        color: filled ? C.bg : color,
        fontFamily: FONT_CN,
        fontWeight: 500,
        fontSize: 26,
        opacity: s,
        scale: `${0.6 + 0.4 * s}`,
        translate: `0 ${(1 - s) * 14}px`,
        whiteSpace: "nowrap",
        ...style,
      }}
    >
      {children}
    </div>
  );
};
