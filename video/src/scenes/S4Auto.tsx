import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, FONT_CN, FONT_MONO } from "../theme";
import { Stamp } from "../components/Stamp";

const NOTES = [
  { title: "红圈高亮", sub: "点哪儿圈哪儿，自动" },
  { title: "步骤编号", sub: "顺序自动排好" },
  { title: "键入内容", sub: "输入的文字自动归档" },
];
const NOTE_T = [45, 70, 95];

// S4 · 杀手锏（旁白 6.6s → 225 帧）：真实导出结果 + 自动标注弹出
export const S4Auto: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const springIn = (t: number) =>
    t < 0 ? 0 : spring({ frame: t, fps, config: { damping: 18, stiffness: 120, mass: 0.9 } });

  const frameS = springIn(frame - 8);
  // 相框内截图缓慢上移，露出后续步骤
  const pan = interpolate(frame, [30, 205], [0, -128], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.4, 0, 0.3, 1),
  });

  return (
    <AbsoluteFill
      style={{
        background: C.bg,
        fontFamily: FONT_CN,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div style={{ display: "flex", gap: 60, alignItems: "flex-start" }}>
        {/* 左：真实导出结果（相框内慢速上移） */}
        <div
          style={{
            opacity: frameS,
            translate: `0 ${(1 - frameS) * 30}px`,
          }}
        >
          <div
            style={{
              color: C.dim,
              fontSize: 22,
              marginBottom: 16,
              textAlign: "center",
            }}
          >
            导出的 HTML 教程 · 真实生成结果
          </div>
          <div
            style={{
              width: 880,
              height: 560,
              overflow: "hidden",
              borderRadius: 14,
              border: `1px solid ${C.border}`,
              boxShadow: "0 30px 90px rgba(0,0,0,0.6)",
              background: C.bgDeep,
            }}
          >
            <Img
              src={staticFile("guide-html.png")}
              style={{
                width: 880,
                translate: `0 ${pan}px`,
              }}
            />
          </div>
          <div style={{ display: "flex", justifyContent: "center", marginTop: 40 }}>
            <Stamp
              startFrame={150}
              color={C.red}
              style={{ background: "rgba(248,81,73,0.10)" }}
            >
              截图、标注、编号——全自动。
            </Stamp>
          </div>
        </div>

        {/* 右：自动标注说明 */}
        <div style={{ width: 560, paddingTop: 60 }}>
          {NOTES.map((n, i) => {
            const s = springIn(frame - NOTE_T[i]);
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 18,
                  background: C.panel,
                  border: `1px solid ${C.border}`,
                  borderRadius: 12,
                  padding: "22px 26px",
                  marginBottom: 20,
                  opacity: s,
                  translate: `${(1 - s) * 36}px 0`,
                }}
              >
                <div
                  style={{
                    width: 30,
                    height: 30,
                    borderRadius: 15,
                    border: `3px solid ${C.red}`,
                    flexShrink: 0,
                  }}
                />
                <div>
                  <div style={{ fontSize: 27, fontWeight: 500, color: C.text }}>
                    {n.title}
                    <span
                      style={{
                        color: C.red,
                        fontSize: 20,
                        marginLeft: 14,
                        fontFamily: FONT_MONO,
                      }}
                    >
                      AUTO
                    </span>
                  </div>
                  <div style={{ fontSize: 20, color: C.dim, marginTop: 6 }}>{n.sub}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
