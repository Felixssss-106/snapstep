import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";

// 数字滚动：数值插值滚入
export const RollingNumber: React.FC<{
  value: number;
  startFrame: number;
  duration?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  style?: React.CSSProperties;
}> = ({
  value,
  startFrame,
  duration = 18,
  decimals = 0,
  prefix = "",
  suffix = "",
  style,
}) => {
  const frame = useCurrentFrame();
  const v = interpolate(frame, [startFrame, startFrame + duration], [0, value], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <span style={style}>
      {prefix}
      {v.toFixed(decimals)}
      {suffix}
    </span>
  );
};
