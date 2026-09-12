import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, FONT_CN, FONT_MONO } from "../theme";
import { SnapLogo } from "../components/SnapLogo";

const COPY = {
  zh: {
    h1: "按一下热键",
    h2: "教程自动写好",
    size: 66,
    sub: "开源 Windows 工具 · 截屏标注全自动",
    note: "↑ 真实生成结果，非示意",
  },
  en: {
    h1: "One hotkey.",
    h2: "Your guide is done.",
    size: 52,
    sub: "Open-source · Auto-annotated guides",
    note: "↑ Real output, not a mockup",
  },
} as const;

// 封面帧（1280×720）：左文右真实教程截图。lang="en" 为国际渠道英文版。
export const Cover: React.FC<{ lang?: "zh" | "en" }> = ({ lang = "zh" }) => {
  const t = COPY[lang];
  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: FONT_CN, overflow: "hidden" }}>
      {/* 右下角步骤圆圈水印 */}
      <div
        style={{
          position: "absolute",
          right: -30,
          bottom: 40,
          fontSize: 100,
          fontFamily: FONT_MONO,
          fontWeight: 700,
          color: C.text,
          opacity: 0.05,
          letterSpacing: 24,
          whiteSpace: "nowrap",
        }}
      >
        1 2 3
      </div>

      <div style={{ display: "flex", padding: "130px 90px 0", gap: 60, alignItems: "flex-start" }}>
        {/* 左：文案 */}
        <div style={{ flex: 1, paddingTop: 60 }}>
          <SnapLogo size={110} />
          <div style={{ fontSize: t.size, fontWeight: 700, color: C.text, lineHeight: 1.3, marginTop: 30 }}>
            {t.h1}
            <br />
            {t.h2}
          </div>
          <div style={{ fontFamily: FONT_MONO, fontSize: 34, color: C.red, marginTop: 28 }}>
            SnapStep
          </div>
          <div style={{ fontSize: 24, color: C.dim, marginTop: 18 }}>
            {t.sub}
          </div>
        </div>

        {/* 右：真实导出教程（微倾相框） */}
        <div style={{ rotate: "-2deg", marginTop: 40 }}>
          <div
            style={{
              width: 470,
              height: 380,
              overflow: "hidden",
              borderRadius: 14,
              border: `1px solid ${C.border}`,
              boxShadow: "0 30px 80px rgba(0,0,0,0.6)",
              background: C.bgDeep,
            }}
          >
            <Img src={staticFile("guide-html.png")} style={{ width: 470 }} />
          </div>
          <div
            style={{
              marginTop: 16,
              textAlign: "center",
              fontFamily: FONT_MONO,
              fontSize: 19,
              color: C.dim,
            }}
          >
            ↑ {t.note.replace("↑ ", "")}
          </div>
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          left: 90,
          right: 90,
          bottom: 86,
          height: 3,
          background: C.red,
          borderRadius: 2,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 90,
          bottom: 42,
          fontFamily: FONT_MONO,
          fontSize: 23,
          color: C.dim,
        }}
      >
        github.com/Felixssss-106/snapstep · MIT
      </div>
    </AbsoluteFill>
  );
};

export const CoverEn: React.FC = () => <Cover lang="en" />;
