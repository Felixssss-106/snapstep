import React from "react";
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../theme";

// 印章式结论条：scale 1.3→1 落下 + 轻微震动
export const Stamp: React.FC<{
  children: React.ReactNode;
  startFrame: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({ children, startFrame, color = C.green, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame - startFrame;
  const drop = spring({
    frame: t,
    fps,
    config: { damping: 200, stiffness: 160 },
  });
  const scale = interpolate(drop, [0, 1], [1.3, 1]);
  const shake =
    t > 6 ? Math.sin((t - 6) * 2.6) * 2 * Math.max(0, 1 - (t - 6) / 8) : 0;
  if (t < 0) return null;
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 16,
        padding: "18px 34px",
        borderRadius: 10,
        border: `2px solid ${color}`,
        background: "rgba(63,185,80,0.10)",
        opacity: interpolate(t, [0, 2], [0, 1], { extrapolateRight: "clamp" }),
        scale: `${scale}`,
        translate: `${shake}px 0`,
        ...style,
      }}
    >
      <CheckIcon color={color} size={30} />
      <span style={{ color: C.text, fontSize: 30, fontWeight: 500 }}>
        {children}
      </span>
    </div>
  );
};

// SVG 对勾（避免依赖系统 emoji 字体）
export const CheckIcon: React.FC<{ color?: string; size?: number }> = ({
  color = C.green,
  size = 24,
}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{ flexShrink: 0 }}>
    <path
      d="M4 12.5 L10 18.5 L20 6"
      fill="none"
      stroke={color}
      strokeWidth={3}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

// SVG 叉号
export const CrossIcon: React.FC<{ color?: string; size?: number }> = ({
  color = C.red,
  size = 24,
}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{ flexShrink: 0 }}>
    <path
      d="M6 6 L18 18 M18 6 L6 18"
      fill="none"
      stroke={color}
      strokeWidth={3}
      strokeLinecap="round"
    />
  </svg>
);

// 琥珀色口径胶囊：easeOutBack 弹出
export const CaliberTag: React.FC<{
  children: React.ReactNode;
  startFrame: number;
  style?: React.CSSProperties;
}> = ({ children, startFrame, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame - startFrame;
  if (t < 0) return <div style={{ visibility: "hidden", padding: "6px 18px" }} />;
  const s = spring({ frame: t, fps, config: { damping: 12, stiffness: 150, mass: 0.6 } });
  return (
    <span
      style={{
        display: "inline-block",
        padding: "6px 18px",
        borderRadius: 999,
        border: `1.5px solid ${C.amber}`,
        color: C.amber,
        background: "rgba(210,153,34,0.12)",
        fontSize: 22,
        whiteSpace: "nowrap",
        opacity: s,
        scale: `${0.5 + 0.5 * s}`,
        ...style,
      }}
    >
      {children}
    </span>
  );
};

export const easeOutCubic = Easing.out(Easing.cubic);
