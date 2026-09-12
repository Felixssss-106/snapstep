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
import { Typewriter } from "../components/Typewriter";
import { CheckIcon } from "../components/Stamp";
import { RollingNumber } from "../components/RollingNumber";

const STEPS = [
  "打开截图工具，截下每一步操作",
  "逐张裁剪、打码、加红框标注",
  "手动编号：步骤 1、步骤 2……",
  "排版贴进文档，图和文字对齐",
];
const ROW_T = [125, 142, 159, 176];

// S1 · 痛点（旁白 4.5s → 240 帧）
export const S1Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const springIn = (t: number) =>
    t < 0 ? 0 : spring({ frame: t, fps, config: { damping: 18, stiffness: 120, mass: 0.9 } });

  const cardS = springIn(frame - 100);
  const tagT = frame - 196;

  return (
    <AbsoluteFill
      style={{
        background: C.bg,
        justifyContent: "center",
        alignItems: "center",
        fontFamily: FONT_CN,
      }}
    >
      {/* 命题输入框 */}
      <div
        style={{
          width: 900,
          background: C.panel,
          border: `1px solid ${C.border}`,
          borderRadius: 12,
          padding: "22px 30px",
          display: "flex",
          alignItems: "center",
          gap: 16,
          marginBottom: 34,
        }}
      >
        <span style={{ fontFamily: FONT_MONO, color: C.term, fontSize: 28 }}>$</span>
        <Typewriter
          text="给新同事写一份软件使用教程"
          startFrame={10}
          framesPerChar={6.5}
          style={{ fontSize: 32, color: C.text }}
        />
      </div>

      {/* 手动流程清单 */}
      <div
        style={{
          width: 900,
          background: C.panel,
          border: `1px solid ${C.border}`,
          borderRadius: 12,
          padding: "28px 36px",
          opacity: cardS,
          translate: `0 ${(1 - cardS) * 36}px`,
        }}
      >
        <div style={{ color: C.dim, fontSize: 20, marginBottom: 20 }}>手动流程 · 每一步都要你自己来</div>
        {STEPS.map((s, i) => {
          const t = frame - ROW_T[i];
          const rowS = springIn(t);
          const checked = t >= 10;
          return (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                height: 52,
                opacity: rowS,
                translate: `${(1 - rowS) * -24}px 0`,
              }}
            >
              <div
                style={{
                  width: 26,
                  height: 26,
                  borderRadius: 7,
                  border: `2px solid ${checked ? C.dim : C.border}`,
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  flexShrink: 0,
                }}
              >
                {checked ? <CheckIcon color={C.dim} size={16} /> : null}
              </div>
              <span style={{ fontSize: 26, color: C.text }}>{s}</span>
            </div>
          );
        })}
      </div>

      {/* 右侧计时器 */}
      <div
        style={{
          position: "absolute",
          right: 150,
          top: 400,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          opacity: interpolate(frame, [120, 132], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        <div style={{ color: C.dim, fontSize: 22, marginBottom: 10 }}>预计耗时</div>
        <RollingNumber
          value={32}
          startFrame={132}
          duration={34}
          suffix=" 分钟"
          style={{ fontFamily: FONT_MONO, fontSize: 56, fontWeight: 700, color: C.red }}
        />
        {tagT >= 0 ? (
          <div
            style={{
              marginTop: 18,
              display: "inline-flex",
              padding: "7px 16px",
              borderRadius: 8,
              border: `1.5px solid ${C.red}`,
              color: C.red,
              fontSize: 21,
              opacity: interpolate(tagT, [0, 6], [0, 1], { extrapolateRight: "clamp" }),
              scale: `${interpolate(tagT, [0, 8], [1.4, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
                easing: Easing.out(Easing.cubic),
              })}`,
            }}
          >
            全程手动
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
