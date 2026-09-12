import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, FONT_CN, FONT_MONO } from "../theme";
import { SnapLogo } from "../components/SnapLogo";
import { Badge } from "../components/Badge";

const TITLE = "SnapStep";

// S2 · 产品揭示（旁白 3.7s → 180 帧）
export const S2Reveal: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const springIn = (t: number) =>
    t < 0 ? 0 : spring({ frame: t, fps, config: { damping: 18, stiffness: 120, mass: 0.9 } });

  const iconS = springIn(frame - 4);

  return (
    <AbsoluteFill
      style={{
        background: C.bg,
        justifyContent: "center",
        alignItems: "center",
        fontFamily: FONT_CN,
      }}
    >
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ opacity: iconS, translate: `${(1 - iconS) * -80}px 0`, marginBottom: 26 }}>
          <SnapLogo size={150} />
        </div>

        <div style={{ fontFamily: FONT_MONO, fontWeight: 700, fontSize: 96, display: "flex" }}>
          {TITLE.split("").map((ch, i) => {
            const s = springIn(frame - (14 + i * 2));
            return (
              <span
                key={i}
                style={{
                  color: C.text,
                  opacity: s,
                  translate: `0 ${(1 - s) * 22}px`,
                  whiteSpace: "pre",
                }}
              >
                {ch}
              </span>
            );
          })}
        </div>

        <div
          style={{
            marginTop: 26,
            fontSize: 34,
            color: C.dim,
            opacity: interpolate(frame, [56, 68], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
            translate: `0 ${interpolate(frame, [56, 68], [14, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            })}px`,
          }}
        >
          按一下热键，教程自动写好
        </div>

        <div style={{ marginTop: 56, display: "flex", gap: 28 }}>
          <Badge delay={78}>自动截屏</Badge>
          <Badge delay={84} color={C.red}>
            自动标注
          </Badge>
          <Badge delay={90}>一键导出</Badge>
        </div>
      </div>
    </AbsoluteFill>
  );
};
