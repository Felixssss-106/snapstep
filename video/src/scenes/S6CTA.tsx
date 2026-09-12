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
import { Terminal, TLine } from "../components/Terminal";
import { SnapLogo } from "../components/SnapLogo";
import { Badge } from "../components/Badge";

// S6 · 安装与 CTA（旁白 7.1s → 240 帧，结尾淡出收束全片）
export const S6CTA: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const springIn = (t: number) =>
    t < 0 ? 0 : spring({ frame: t, fps, config: { damping: 18, stiffness: 120, mass: 0.9 } });

  const cardS = springIn(frame - 64);

  const topDim = interpolate(frame, [116, 134], [1, 0.32], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const coverS = springIn(frame - 120);
  const barW = interpolate(frame, [144, 156], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const urlO = interpolate(frame, [154, 164], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const fade = interpolate(frame, [271, 285], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const breath = 1 + 0.008 * Math.sin(frame / 7);

  return (
    <AbsoluteFill
      style={{
        background: C.bg,
        fontFamily: FONT_CN,
        alignItems: "center",
        opacity: fade,
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          paddingTop: 96,
          scale: `${breath}`,
          transformOrigin: "50% 55%",
        }}
      >
        <div style={{ opacity: topDim, translate: `0 ${(1 - topDim) * -20}px` }}>
          <Terminal width={1160} title="get snapstep">
            <TLine
              from={8}
              text="$ github.com/Felixssss-106/snapstep → Releases"
              color={C.term}
              framesPerChar={0.9}
            />
          </Terminal>

          <div
            style={{
              width: 1160,
              background: C.panel,
              border: `1px solid ${C.border}`,
              borderRadius: 12,
              padding: "26px 34px",
              marginTop: 26,
              display: "flex",
              alignItems: "center",
              gap: 24,
              opacity: cardS,
              translate: `0 ${(1 - cardS) * 36}px`,
            }}
          >
            <SnapLogo size={64} />
            <div>
              <div style={{ fontFamily: FONT_MONO, fontSize: 30, color: C.text }}>
                Felixssss-106 / SnapStep
              </div>
              <div style={{ fontSize: 23, color: C.dim, marginTop: 8 }}>
                按一下热键，教程自动写好 · Windows 免安装
              </div>
            </div>
          </div>

          <div style={{ display: "flex", gap: 24, marginTop: 30, justifyContent: "center" }}>
            <Badge delay={92}>MIT 开源</Badge>
            <Badge delay={97}>100% 本地</Badge>
            <Badge delay={102}>v0.2.0</Badge>
          </div>
        </div>

        <div
          style={{
            marginTop: 92,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            opacity: coverS,
            translate: `0 ${(1 - coverS) * 30}px`,
          }}
        >
          <div style={{ fontSize: 52, fontWeight: 700, color: C.text, textAlign: "center" }}>
            操作会重复，教程不必重写。
          </div>
          <div
            style={{
              width: `${barW * 1.8}px`,
              height: 4,
              background: C.red,
              borderRadius: 2,
              marginTop: 30,
            }}
          />
          <div
            style={{
              fontFamily: FONT_MONO,
              fontSize: 26,
              color: C.dim,
              marginTop: 28,
              opacity: urlO,
            }}
          >
            github.com/Felixssss-106/snapstep
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
