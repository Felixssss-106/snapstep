import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, FONT_CN, FONT_MONO } from "../theme";
import { Stamp } from "../components/Stamp";

const FORMATS = [
  { ext: ".md", name: "Markdown", desc: "纯文本即用", hot: false },
  { ext: ".html", name: "单文件网页", desc: "图片全部内嵌", hot: true },
  { ext: ".docx", name: "Word", desc: "直接分发", hot: false },
];
const CARD_T = [24, 40, 56];

// S5 · 导出与隐私（旁白 6.0s → 210 帧）
export const S5Export: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const springIn = (t: number) =>
    t < 0 ? 0 : spring({ frame: t, fps, config: { damping: 18, stiffness: 120, mass: 0.9 } });

  const capS = springIn(frame - 8);

  return (
    <AbsoluteFill
      style={{
        background: C.bg,
        fontFamily: FONT_CN,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div style={{ width: 1280 }}>
        <div
          style={{
            textAlign: "center",
            color: C.dim,
            fontSize: 25,
            marginBottom: 36,
            opacity: capS,
            translate: `0 ${(1 - capS) * 12}px`,
          }}
        >
          录完，一键导出三种格式
        </div>

        <div style={{ display: "flex", gap: 30, justifyContent: "center" }}>
          {FORMATS.map((f, i) => {
            const s = springIn(frame - CARD_T[i]);
            return (
              <div
                key={f.ext}
                style={{
                  width: 380,
                  background: C.panel,
                  border: `1.5px solid ${f.hot ? C.green : C.border}`,
                  borderRadius: 14,
                  padding: "34px 34px",
                  textAlign: "center",
                  opacity: s,
                  translate: `0 ${(1 - s) * 20}px`,
                  position: "relative",
                }}
              >
                {f.hot ? (
                  <span
                    style={{
                      position: "absolute",
                      top: -14,
                      right: 22,
                      padding: "4px 14px",
                      borderRadius: 999,
                      background: C.green,
                      color: C.bg,
                      fontSize: 18,
                      fontWeight: 700,
                    }}
                  >
                    推荐
                  </span>
                ) : null}
                <div
                  style={{
                    fontFamily: FONT_MONO,
                    fontSize: 48,
                    fontWeight: 700,
                    color: f.hot ? C.green : C.text,
                  }}
                >
                  {f.ext}
                </div>
                <div style={{ fontSize: 27, color: C.text, marginTop: 14 }}>{f.name}</div>
                <div style={{ fontSize: 21, color: C.dim, marginTop: 10 }}>{f.desc}</div>
              </div>
            );
          })}
        </div>

        <div style={{ display: "flex", justifyContent: "center", marginTop: 56 }}>
          <Stamp startFrame={112}>100% 本地运行 · 零遥测</Stamp>
        </div>

        <div
          style={{
            textAlign: "center",
            color: C.dim,
            fontSize: 22,
            marginTop: 30,
            opacity: interpolate(frame, [140, 152], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          密码框自动遮蔽 · 隐私模式可跳过截屏
        </div>
      </div>
    </AbsoluteFill>
  );
};
