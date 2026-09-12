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

const NODES = [
  { num: "1", name: "开始录制", key: "Ctrl+Alt+S", sub: "托盘常驻 · 全局热键" },
  { num: "2", name: "每步自动记录", key: null, sub: "点击即截屏 · 高亮圈 · 序号" },
  { num: "3", name: "生成教程", key: null, sub: "标注齐全，直接可用" },
];
const R = 64;
const Y = 500;
const xs = NODES.map((_, i) => 960 + (i - 1) * 470);
const activateT = (i: number) => 25 + i * 55;

// S3 · 三步流程（旁白 5.4s → 195 帧）
export const S3Flow: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pulse = interpolate(frame, [168, 174, 180], [1, 0.86, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: FONT_CN }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 190, textAlign: "center" }}>
        <span style={{ color: C.dim, fontSize: 26 }}>
          三步，写完一份带标注截图的图文教程
        </span>
      </div>

      <AbsoluteFill style={{ opacity: pulse }}>
        <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0 }}>
          {NODES.slice(0, -1).map((_, i) => {
            const x1 = xs[i] + R + 22;
            const x2 = xs[i + 1] - R - 22;
            const len = x2 - x1;
            const t = frame - (activateT(i) + 4);
            const off = interpolate(t, [0, 10], [len, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            });
            return (
              <line
                key={i}
                x1={x1}
                y1={Y}
                x2={x2}
                y2={Y}
                stroke={C.red}
                strokeWidth={3}
                strokeDasharray={len}
                strokeDashoffset={Math.max(0, off)}
                opacity={t < 0 ? 0 : 0.9}
              />
            );
          })}
        </svg>

        {NODES.map((n, i) => {
          const t = frame - activateT(i);
          const active = t >= 0;
          const s = active
            ? spring({ frame: t, fps, config: { damping: 16, stiffness: 140, mass: 0.8 } })
            : 0;
          const scale = active
            ? interpolate(Math.min(s, 1), [0, 0.5, 1], [0.9, 1.06, 1])
            : 0.9;
          const subT = t - 12;
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: xs[i] - 200,
                top: Y - R,
                width: 400,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                opacity: active ? 1 : 0.4,
              }}
            >
              <div
                style={{
                  width: R * 2,
                  height: R * 2,
                  borderRadius: R,
                  border: `3px solid ${active ? C.red : C.border}`,
                  background: active ? "rgba(248,81,73,0.10)" : C.panel,
                  boxShadow: active ? `0 0 40px rgba(248,81,73,0.30)` : "none",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  scale: `${scale}`,
                  fontFamily: FONT_MONO,
                  fontSize: 46,
                  fontWeight: 700,
                  color: active ? C.text : C.dim,
                }}
              >
                {n.num}
              </div>
              <div
                style={{
                  marginTop: 26,
                  fontSize: 31,
                  fontWeight: 500,
                  color: active ? C.text : C.dim,
                }}
              >
                {n.name}
              </div>
              {n.key ? (
                <div
                  style={{
                    marginTop: 12,
                    fontFamily: FONT_MONO,
                    fontSize: 25,
                    fontWeight: 700,
                    color: active ? C.red : C.dim,
                    opacity: interpolate(subT, [0, 10], [0, 1], {
                      extrapolateLeft: "clamp",
                      extrapolateRight: "clamp",
                    }),
                  }}
                >
                  {n.key}
                </div>
              ) : null}
              <div
                style={{
                  marginTop: n.key ? 10 : 12,
                  fontSize: 21,
                  color: C.dim,
                  opacity: interpolate(subT, [0, 10], [0, 1], {
                    extrapolateLeft: "clamp",
                    extrapolateRight: "clamp",
                  }),
                  translate: `0 ${interpolate(subT, [0, 10], [10, 0], {
                    extrapolateLeft: "clamp",
                    extrapolateRight: "clamp",
                  })}px`,
                  whiteSpace: "nowrap",
                }}
              >
                {n.sub}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
